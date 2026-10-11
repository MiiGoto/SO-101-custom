"""Offline URDF gravity screening and conservative rigid-body load envelopes.
No hardware interfaces. Custom masses/COMs are planning assumptions, not CAD validation.
Run with Python + numpy from the project directory.
"""
from pathlib import Path
import copy, csv, json, math, xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
URDF = ROOT / 'mechanical/reference/Simulation/SO101/so101_new_calib.urdf'
NAMES = ['shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper']
G = 9.80665
MASS = {'shoulder_link': .080, 'upper_arm_link': .080,
        'lower_arm_link': .085, 'wrist_link': .053,
        'gripper_link': .048, 'moving_jaw_so101_v1_link': .012}

def vec(s): return np.array([float(v) for v in s.split()])
def rpy(a):
    r,p,y=a; cr,sr,cp,sp,cy,sy=math.cos(r),math.sin(r),math.cos(p),math.sin(p),math.cos(y),math.sin(y)
    return np.array([[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],
                     [sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]])

def load():
    root=ET.parse(URDF).getroot(); links={}; joints={}
    for e in root.findall('link'):
        i=e.find('inertial')
        if i is None: continue
        a=i.find('inertia').attrib
        I=np.array([[float(a['ixx']),float(a['ixy']),float(a['ixz'])],
                    [float(a['ixy']),float(a['iyy']),float(a['iyz'])],
                    [float(a['ixz']),float(a['iyz']),float(a['izz'])]])
        links[e.attrib['name']]={'mass':float(i.find('mass').attrib['value']),
            'com':vec(i.find('origin').attrib['xyz']), 'inertia_bound':float(np.linalg.eigvalsh(I).max())}
    for e in root.findall('joint'):
        o=e.find('origin'); li=e.find('limit')
        joints[e.attrib['name']]={'parent':e.find('parent').attrib['link'],
            'child':e.find('child').attrib['link'],'xyz':vec(o.attrib['xyz']),
            'rpy':vec(o.attrib['rpy']), 'limits':None if li is None else
                [float(li.attrib['lower']),float(li.attrib['upper'])]}
    return links,joints

def model(kind):
    links,joints=load()
    if kind!='official':
        for n,m in MASS.items():
            links[n]['mass']=m
            # COM remains official proxy. Bounding inertia is an explicit planning allowance.
            links[n]['inertia_bound']=max(links[n]['inertia_bound'],.0002)
        for n in NAMES[:4]: joints[n]['limits']=[-math.radians(80),math.radians(80)]
        joints['wrist_roll']['limits']=[-math.pi/2,math.pi/2]
        joints['gripper']['limits']=[0,math.pi/3]
    scale={'official':1,'A':1,'B80':.8,'B85':.85,'B90':.9}.get(kind)
    if scale is not None and kind!='official':
        # Conceptual axis/COM offsets only; no motor/hole/mesh dimensions are scaled.
        for j in joints.values(): j['xyz']*=scale
        for l in links.values(): l['com']*=scale
    if kind=='C':
        for jn,target in [('elbow_flex',.09),('wrist_flex',.10),('wrist_roll',.045),('gripper_frame_joint',.07)]:
            j=joints[jn]; old=np.linalg.norm(j['xyz']); j['xyz']*=target/old
        for ln,jnext in [('upper_arm_link','elbow_flex'),('lower_arm_link','wrist_flex'),('wrist_link','wrist_roll'),('gripper_link','gripper_frame_joint')]:
            _,orig=load(); ratio=np.linalg.norm(joints[jnext]['xyz'])/np.linalg.norm(orig[jnext]['xyz'])
            links[ln]['com']*=ratio
    if kind=='D':
        # Shoulder lift + elbow flex test rig; 50/60 mm links, no powered wrist/gripper.
        for n,m in {'upper_arm_link':.072,'lower_arm_link':.025,'wrist_link':0.,'gripper_link':0.,'moving_jaw_so101_v1_link':0.}.items():
            links[n]['mass']=m
            if m==0: links[n]['inertia_bound']=0.
        for jn,target in [('elbow_flex',.05),('wrist_flex',.06)]:
            j=joints[jn]; old=np.linalg.norm(j['xyz']); j['xyz']*=target/old
        links['upper_arm_link']['com']=np.array([-.035,0,0])
        links['lower_arm_link']['com']=np.array([-.03,0,0])
        for jn in ['wrist_roll','gripper_frame_joint']: joints[jn]['xyz']*=0
    return links,joints

def fk(q,joints):
    count=len(q); pos={'base_link':np.zeros((count,3))}; rot={'base_link':np.broadcast_to(np.eye(3),(count,3,3)).copy()}; axes=[]; origins=[]
    for k,n in enumerate(NAMES):
        j=joints[n]; p,R=pos[j['parent']],rot[j['parent']]
        o=p+np.einsum('nij,j->ni',R,j['xyz']); A=R@rpy(j['rpy']); axis=A[:,:,2]
        c,s=np.cos(q[:,k]),np.sin(q[:,k]); Z=np.zeros((count,3,3)); Z[:,0,0]=c;Z[:,0,1]=-s;Z[:,1,0]=s;Z[:,1,1]=c;Z[:,2,2]=1
        pos[j['child']]=o;rot[j['child']]=A@Z; axes.append(axis);origins.append(o)
    return pos,rot,np.array(axes),np.array(origins)

def gravity(q,links,joints,payload):
    pos,rot,axes,origins=fk(q,joints); t=np.zeros((len(q),6));
    for b,n in enumerate(NAMES):
        ln=joints[n]['child']; l=links[ln]; c=pos[ln]+np.einsum('nij,j->ni',rot[ln],l['com']); force=np.array([0,0,-G*l['mass']])
        for j in range(b+1): t[:,j]+=np.sum(axes[j]*np.cross(c-origins[j],force),axis=1)
    fixed=joints['gripper_frame_joint']; ln=fixed['parent']; p=pos[ln]+np.einsum('nij,j->ni',rot[ln],fixed['xyz'])
    # Payload supported by the gripper body, not counted again on the moving jaw.
    for j in range(5): t[:,j]+=np.sum(axes[j]*np.cross(p-origins[j],[0,0,-G*payload]),axis=1)
    return t

def distances(links,joints):
    R=np.zeros((6,7)); bodyI=[]
    for b,n in enumerate(NAMES):
        l=links[joints[n]['child']]; bodyI.append(l['inertia_bound'])
        for j in range(b+1):
            R[j,b]=np.linalg.norm(l['com'])+sum(np.linalg.norm(joints[NAMES[k]]['xyz']) for k in range(j+1,b+1))
    for j in range(5): R[j,6]=np.linalg.norm(joints['gripper_frame_joint']['xyz'])+sum(np.linalg.norm(joints[NAMES[k]]['xyz']) for k in range(j+1,5))
    return R,np.array(bodyI+[0.])

def envelope(kind,payload=.05,alpha=1.,omega=.5):
    links,joints=model(kind); lim=np.array([joints[n]['limits'] for n in NAMES]); rng=np.random.default_rng(101)
    q=rng.uniform(lim[:,0],lim[:,1],size=(30000,6)); q=np.vstack([q,np.zeros(6)])
    t=np.abs(gravity(q,links,joints,payload)); idx=np.argmax(t,axis=0); maxima=t[idx,np.arange(6)]; poses=q[idx].copy()
    # Deterministic local coordinate refinement; no global optimality claim.
    for j in range(6):
        for step in [.1,.02,.004,.0008]:
            for _ in range(4):
                candidates=np.repeat(poses[j][None,:],13,axis=0)
                for k in range(6): candidates[1+2*k,k]+=step;candidates[2+2*k,k]-=step
                candidates=np.clip(candidates,lim[:,0],lim[:,1]); vals=np.abs(gravity(candidates,links,joints,payload)[:,j]); win=int(vals.argmax())
                if vals[win]>maxima[j]: maxima[j]=vals[win];poses[j]=candidates[win]
    R,I=distances(links,joints); masses=np.array([links[joints[n]['child']]['mass'] for n in NAMES]+[payload]); static=(R*masses).sum(axis=1)*G
    static[0]=0. # Vertical base axis, level mounting, pure gravity.
    # |a_body| <= sum alpha*r + (sum |omega|)^2 * max_path_radius.
    # All ancestor motions are allowed simultaneously. Deliberately loose, collision-independent.
    accel=np.array([sum(alpha*R[k,b] for k in range(b+1))+(b+1)**2*omega**2*R[0,b] for b in range(6)]+[sum(alpha*R[k,6] for k in range(5))+25*omega**2*R[0,6]])
    inertia=(R*masses*accel).sum(axis=1)
    for j in range(6): inertia[j]+=sum(I[b]*((b+1)*alpha+(b+1)**2*omega**2) for b in range(j,6))
    grasp=0. if kind=='D' else 5*.035 # Assumed 5 N jaw force, 35 mm lever arm.
    static[5]+=grasp; maxima[5]+=grasp
    reserve=np.array([.02]*4+[.01,.01]); motion=static+inertia+reserve
    rows=[]
    for j,n in enumerate(NAMES): rows.append({'variant':kind,'joint':n,'payload_kg':payload,
        'sampled_static_Nm':round(float(maxima[j]),6),'conservative_static_Nm':round(float(static[j]),6),
        'inertial_bound_Nm':round(float(inertia[j]),6),'friction_reserve_Nm':reserve[j],
        'motion_required_Nm':round(float(motion[j]),6),'design_target_Nm':round(float(1.25*motion[j]),6),
        'sampled_worst_q_rad':json.dumps(poses[j].tolist()),'status':'Assumption; not physical rating'})
    return rows,{'mass_kg':masses.tolist(),'radius_bounds_m':R.tolist(),'alpha_rad_s2':alpha,'omega_rad_s':omega,
                 'assumed_inertia_bound_kg_m2':I.tolist(),'joint_limits_rad':lim.tolist()}

def main():
    rows=[]; details={}
    for kind in ['official','A','B80','B85','B90','C','D']:
        for payload in [0,.05,.1]:
            result,detail=envelope(kind,payload);rows.extend(result);details[f'{kind}/{payload}']=detail
    out=ROOT/'docs';
    with (out/'torque_results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'torque_inputs.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
    official_links,official_joints=load()
    data={'joint_origins':{n:{'xyz_m':j['xyz'].tolist(),'distance_m':float(np.linalg.norm(j['xyz'])),'limits_rad':j['limits']} for n,j in official_joints.items()},
          'links':{n:{'mass_kg':l['mass'],'com_m':l['com'].tolist()} for n,l in official_links.items()}}
    (out/'official_geometry.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('Generated',len(rows),'joint-load rows; no hardware accessed.')
    for r in rows:
        if r['payload_kg']==.05 and r['variant'] in ['A','B85','C']: print(r['variant'],r['joint'],r['sampled_static_Nm'],r['conservative_static_Nm'],r['motion_required_Nm'])
if __name__=='__main__': main()
