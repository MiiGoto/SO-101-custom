from pathlib import Path
import json, csv
import numpy as np
M=Path(__file__).resolve().parents[2];P=M.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
ref=read(M/'upstream_reference/kinematic_reference.json');joints=ref['joints'];parts={x['name']:x for x in read(M/'follower_six_axis/analysis/part_mass_properties.json')}
def fk(q):
    frames={'base_link':np.eye(4)};origins=[];axes=[]
    for j,angle in zip(joints,q):
        pre=frames[j['parent']]@np.array(j['origin']);origins.append(pre[:3,3]/1000);axes.append(pre[:3,2])
        c,s=np.cos(angle),np.sin(angle);rz=np.eye(4);rz[:2,:2]=[[c,-s],[s,c]];frames[j['child']]=pre@rz
    return frames,np.array(origins),np.array(axes)
index={'base_link':-1,**{j['child']:i for i,j in enumerate(joints)}}
limits=np.array([j['limits_rad'] for j in joints]);limits[:4]=np.array([[-np.deg2rad(75),np.deg2rad(75)]]*4)
limits[4]=[-np.pi/2,np.pi/2];limits[5]=[0,np.pi/2]
axis_results=[]
for item in read(M/'upstream_reference/axis_geometry.json'):
    T=np.array(item['world']);targets=([1] if item['part'].startswith('Upper') else [2] if item['part'].startswith('Under') else [3]);hits=[]
    for k in targets:
        p=np.array(joints[k]['world'])[:3,3];ax=np.array(joints[k]['world'])[:3,2];candidates=[]
        for cyl in item['cylinders']:
            world=T@np.r_[cyl['point_mm'],1];a=T[:3,:3]@cyl['axis'];distance=np.linalg.norm(np.cross(world[:3]-p,ax));align=abs(a@ax)
            if align>.999:candidates.append((distance,cyl['radius_mm'],world[:3].tolist()))
        candidates.sort();hits.append({'joint':joints[k]['name'],'nearest_parallel_cylinder_distance_mm':candidates[0][0] if candidates else None,'radius_mm':candidates[0][1] if candidates else None,'candidates':candidates[:4]})
    axis_results.append({'part':item['part'],'measurements':hits,'bbox_mm':(np.array(item['bounds_max_mm'])-item['bounds_min_mm']).tolist(),'solid_bodies':item['solid_bodies']})
save(M/'release_review/axis_alignment.json',axis_results)
import sys
if '--axes-only' in sys.argv:sys.exit(0)
# Native geometry derived properties transformed by exact joint/visual frames.
for folder in ['two_joint_revb','follower_six_axis']:
    if '--two-only' in sys.argv and folder!='two_joint_revb':continue
    assembly=read(M/folder/'analysis/assembly.json');bodies=[]
    for b in assembly['body_records']:
        name=b.get('source_part',b['name']);p=parts[name];local=np.array(b['local']);com=(local@np.r_[p['com_mm'],1])[:3]/1000
        bodies.append({'name':b['name'],'link':b['link'],'mass':p['mass_kg'],'com':com,'inertia_trace':sum(p['inertia_kg_m2'][:3]),'part':name})
    def evaluate(q,payload):
        frames,origins,axes=fk(q);G=np.zeros(6);R=np.zeros((6,len(bodies)+1));inert=np.zeros(len(bodies)+1);masses=np.array([b['mass'] for b in bodies]+[payload]);locations=[]
        for n,b in enumerate(bodies):
            F=frames[b['link']];pos=F[:3,:3]@b['com']+F[:3,3]/1000;locations.append(pos);inert[n]=b['inertia_trace'];last=index[b['link']]
            for k in range(last+1):
                G[k]+=axes[k]@np.cross(pos-origins[k],np.array([0,0,-b['mass']*9.80665]))
                # Per-body path radius upper bound, including link COM, avoids relying on instantaneous Jacobian radius.
                R[k,n]=np.linalg.norm(b['com'])+sum(np.linalg.norm(np.array(joints[l]['origin'])[:3,3])/1000 for l in range(k+1,last+1))
        # Payload belongs to fixed gripper body, not moving jaw; no double count.
        base=np.array(ref['frames']['gripper_link']);tool_local=np.linalg.inv(base)@np.array(ref['tool']);F=frames['gripper_link'];pt=(F@tool_local)[:3,3]/1000
        for k in range(5):
            G[k]+=axes[k]@np.cross(pt-origins[k],[0,0,-payload*9.80665]);R[k,-1]=np.linalg.norm(tool_local[:3,3])/1000+sum(np.linalg.norm(np.array(joints[l]['origin'])[:3,3])/1000 for l in range(k+1,5))
        # Conservative coupled acceleration envelope: alpha=.2 rad/s2; omega=.1 rad/s. Geared rotor, friction/cables absent.
        if folder=='two_joint_revb':R[[0,3,4,5],:]=0 # Locked pan and absent wrist/gripper do not accelerate.
        active=(R>0);acc=np.sum(.2*R,axis=0)+np.sum(.1*active,axis=0)**2*np.max(R,axis=0)
        D=(R*(masses*acc)).sum(axis=1)+(active*inert*(.2*active.sum(axis=0)+(.1*active.sum(axis=0))**2)).sum(axis=1)
        if folder=='two_joint_revb':G[[0,3,4,5]]=0;D[[0,3,4,5]]=0
        return np.abs(G),D
    if '--refresh-dynamics' in sys.argv:
        path=M/folder/'analysis/torque_analysis.json';old=read(path)
        for case in old['cases']:
            # This conservative path-radius D is posture-independent; preserve sampled gravity evidence.
            _,D=evaluate(np.zeros(6),case['payload_kg']);peak=np.array(case['sampled_static_peak_Nm']);motion=peak+D
            case['motion_bound_Nm']=motion.tolist();case['design_target_1_25_Nm']=(motion*1.25).tolist()
        old['fixed_joint_acceleration_excluded']=True;save(path,old);print(folder,'updated dynamic bound',old['cases'][1]['motion_bound_Nm']);continue
    rng=np.random.default_rng(101);samples=rng.uniform(limits[:,0],limits[:,1],(6000,6));samples=np.vstack([np.zeros(6),samples])
    if folder=='two_joint_revb':samples[:,[0,3,4,5]]=0
    cases=[]
    for payload in [0,.05,.1]:
        peak=np.zeros(6);dyn=np.zeros(6);pose=np.zeros((6,6))
        for q in samples:
            G,D=evaluate(q,payload);mask=G>peak;peak=np.maximum(peak,G);pose[mask]=q;dyn=np.maximum(dyn,G+D)
        # Requested gripping-force case separate from joint self weight.
        contact=.175 if folder=='follower_six_axis' else 0
        peak[5]+=contact;dyn[5]+=contact
        cases.append({'payload_kg':payload,'sampled_static_peak_Nm':peak.tolist(),'motion_bound_Nm':dyn.tolist(),'design_target_1_25_Nm':(dyn*1.25).tolist(),'sampled_worst_q_rad':pose.tolist(),'grip_contact_assumption_Nm':contact})
    save(M/folder/'analysis/torque_analysis.json',dict(cases=cases,limits_rad=limits.tolist(),samples=len(samples),velocity_rad_s=.1,acceleration_rad_s2=.2,method='CAD mass/COM/inertia; exact FK gravity and conservative path-radius dynamic bound; sampled static maximum not global proof',mass_model='Full solid PET 1541 kg/m3 on official parts; custom cradle default 1000 kg/m3; motor overrides 42/18 g. Not sliced mass.',continuous_torque='UNKNOWN; nominal/stall not a permissible rating',omissions=['rotor reflected inertia','friction','cables','fasteners','actual sensor assembly','unqualified horn coupling','structural/thermal qualification']))
    save(M/folder/'analysis/mass_properties.json',dict(total_mass_kg=assembly['mass_kg'],com_mm=assembly['com_mm'],parts=[dict(name=b['name'],part=b['part'],mass_kg=b['mass'],link=b['link'],link_com_m=b['com'].tolist(),inertia_trace_kg_m2=b['inertia_trace']) for b in bodies],scope='Inventor native model, not actual printed mass. Reference datum carriers excluded.'))
    print(folder,assembly['mass_kg'],cases[1]['sampled_static_peak_Nm'],cases[1]['motion_bound_Nm'])
