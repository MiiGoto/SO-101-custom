"""Offline inverse dynamics using measured Inventor CAD properties, not real hardware."""
import csv,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kinematics import forward
parts={p['part']:p for p in json.loads((ROOT/'analysis/mass_properties.json').read_text(encoding='utf-8-sig'))}
# Full solid PET library density proxy; no assumed infill multiplier.
bodies=[]
for name in ('Upper_Arm','Elbow_Mount','Servo_Horn_Adapter','Spring_Link_Anchor','Shoulder_Output_Flange','Shoulder_Shaft_Envelope','Elbow_Support_Carrier'):
    p=parts[name];bodies.append((name,1,p['mass_kg'],np.array(p['com_mm'][:2])/1000,p['inertia_kg_m2'][2]))
p=parts['Servo_Envelope'];bodies.append(('Elbow servo (42 g manufacturer mass, envelope COM assumed)',1,.042,np.array([.09,-.019]),p['inertia_kg_m2'][2]))
for name in ('Forearm','Payload_Mount','Elbow_Horn_Adapter','Elbow_Output_Flange','Elbow_Shaft_Envelope'):
    p=parts[name];bodies.append((name,2,p['mass_kg'],np.array(p['com_mm'][:2])/1000,p['inertia_kg_m2'][2]))
# Not yet mounted: support/encoder/fasteners allowance, deliberately explicit.
for name,group,x,z in [('Bearing_625_Envelope',1,.09,.034),('Bearing_Retainer',1,.09,.034),
                     ('Encoder_Mount',1,.09,.034),('Encoder_Board_Envelope',1,.09,.034),
                     ('Magnet_Carrier',1,0,0),('Magnet_6x2_Envelope',1,0,0),
                     ('Magnet_Carrier',2,0,.034),('Magnet_6x2_Envelope',2,0,.034),
                     ('Encoder_Standoff',1,.078,.034),('Encoder_Standoff',1,.102,.034)]:
    p=parts[name];c=np.array(p['com_mm'][:2])/1000+np.array([x,0]);bodies.append((name,group,p['mass_kg'],c,p['inertia_kg_m2'][2]))
bodies.extend([('upper moving fastener allowance TBD',1,.006,np.array([.09,0]),0),
               ('distal horn/fastener allowance TBD',2,.006,np.array([0,0]),0)])

def matrices(q,payload):
    M=np.zeros((2,2));G=np.zeros(2)
    a,b=q;R=lambda t:np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
    perp=lambda r:np.array([-r[1],r[0]])
    shoulder_to_elbow=R(a)@np.array([.09,0])
    for name,group,mass,c,iz in bodies+[('payload',2,payload,np.array([.10,0]),0)]:
        if group==1:
            r=R(a)@c;J=np.column_stack((perp(r),np.zeros(2)));w=np.array([1.,0])
        else:
            rel=R(a+b)@c;r=shoulder_to_elbow+rel;J=np.column_stack((perp(r),perp(rel)));w=np.ones(2)
        M+=mass*J.T@J+iz*np.outer(w,w)
        G+=mass*9.80665*J[1]
    return M,G

def dynamics(q,payload,v=(.1,.1),acc=(.2,.2)):
    M,G=matrices(q,payload);eps=1e-5
    d=np.zeros((2,2,2))
    for k in range(2):
        dq=np.eye(2)[k]*eps;d[:,:,k]=(matrices(np.array(q)+dq,payload)[0]-matrices(np.array(q)-dq,payload)[0])/(2*eps)
    C=np.zeros(2)
    for i in range(2):
        for j in range(2):
            for k in range(2):C[i]+=(d[i,j,k]+d[i,k,j]-d[j,k,i])*.5*v[j]*v[k]
    # Conservative triangle bound for either sign acceleration/velocity.
    c_bound=np.zeros(2)
    for i in range(2):
        for j in range(2):
            for k in range(2):c_bound[i]+=abs((d[i,j,k]+d[i,k,j]-d[j,k,i])*.5)*abs(v[j]*v[k])
    return G, M@acc+C, abs(G)+abs(M)@np.abs(acc)+c_bound

poses=[('initial',0,0),('extension',0,0),('mid',35,60),('lift',60,30),('max_flex',75,120)]
result={'status':'CAD-derived conditional estimate, no thermal qualification','units':'SI',
        'assumptions':{'gravity':9.80665,'velocity_rad_s':[.1,.1],'acceleration_rad_s2':[.2,.2],
        'material':'Inventor PET full solid proxy, not sliced PLA/PETG mass',
        'hardware_mass_allowances_g':[6,6],'friction_cable_spring_hysteresis':'TBD; not included',
        'joint_limits_deg':[[0,75],[0,120]],'continuous_torque_available':'UNKNOWN'},
        'bodies':[{'name':n,'group':g,'mass_kg':m,'local_com_m':c.tolist(),'izz_kg_m2':iz} for n,g,m,c,iz in bodies],
        'cases':[]}
for payload in (0,.025,.05,.075,.10,.15):
    maximum=np.zeros(2);dynamicmax=np.zeros(2);arg=[None,None]
    for a in range(0,76,1):
        for b in range(0,121,2):
            q=np.radians([a,b]);G,_,bound=dynamics(q,payload)
            for j in range(2):
                if abs(G[j])>maximum[j]:maximum[j]=abs(G[j]);arg[j]=[a,b]
            dynamicmax=np.maximum(dynamicmax,bound)
    row={'payload_g':payload*1000,'max_static_Nm':maximum.tolist(),'max_motion_bound_Nm':dynamicmax.tolist(),'max_static_pose_deg':arg,'grid_resolution_deg':[1,2],'poses':[]}
    for name,a,b in poses:
        G,D,B=dynamics(np.radians([a,b]),payload)
        row['poses'].append({'name':name,'q_deg':[a,b],'gravity_Nm':G.tolist(),'dynamic_addition_Nm':D.tolist(),'motion_bound_Nm':B.tolist(),'tip_m':forward(tuple(np.radians([a,b])))})
    result['cases'].append(row)
(ROOT/'torque_analysis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

# Extension spring anchors modeled in native IPT. Force acts at rotating r.
anchor=np.array([-.035,.040]);local=np.array([.035,0])
def spring(q,k,L0):
    a=q[0];r=np.array([math.cos(a)*local[0],math.sin(a)*local[0]])
    d=anchor-r;length=np.linalg.norm(d);force=max(0,k*(length-L0));f=d/length*force
    return float(r[0]*f[1]-r[1]*f[0]),float(length),float(force)
samples=[(np.radians([a,b]),matrices(np.radians([a,b]),.05)[1][0]) for a in range(0,76,5) for b in range(0,121,10)]
best=None
for k in range(50,801,10):
    for L0 in np.linspace(.02,.065,46):
        residual=[g-spring(q,k,L0)[0] for q,g in samples]
        score=max(abs(x) for x in residual)
        if best is None or score<best[0]:best=(score,k,float(L0))
score,k,L0=best
spring_rows=[{'shoulder_deg':a,'torque_Nm':spring(np.radians([a,0]),k,L0)[0],'length_mm':spring(np.radians([a,0]),k,L0)[1]*1000,'force_N':spring(np.radians([a,0]),k,L0)[2]} for a in range(0,76,5)]
comp={'status':'PARAMETER_STUDY_ONLY; no spring selected or tested','fixed_anchor_mm':[-35,40,-40],'rotating_anchor_local_mm':[35,0,-40],
      'effective_spring_k_N_m':k,'equivalent_zero_force_length_mm':L0*1000,'worst_residual_shoulder_Nm':score,
      'length_range_mm':[min(x['length_mm'] for x in spring_rows),max(x['length_mm'] for x in spring_rows)],
      'force_range_N':[min(x['force_N'] for x in spring_rows),max(x['force_N'] for x in spring_rows)],'poses':spring_rows,
      'initial_tension_note':'Equivalent F=k(L-L0); choose actual free length Lfree and Fi=k(Lfree-L0). Closed-coil hook length Lfree must be <=44.49 mm (plus tolerance margin); example Lfree44 mm -> Fi0.28 N, extension36.62 mm. Hook compliance/initial tension/stroke/fatigue must be checked.',
      'failure':'Breakage removes compensation; arm falls until a qualified stop/support. Spring overstress and excess upward torque possible.'}
(ROOT/'gravity_compensation.json').write_text(json.dumps(comp,indent=2),encoding='utf-8')

with (ROOT/'mechanical_bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['part','quantity','role','cad_mass_g','status'])
    for name,p in parts.items():
        quantity=1
        if name=='Servo_Envelope':quantity=2
        writer.writerow([name,quantity,'coupon' if 'Test' in name or 'Coupon' in name else 'CAD prototype',round(p['mass_kg']*1000,3),'COMPLETED CAD; hardware fit TBD'])
print(json.dumps({'payload_50g':result['cases'][2],'spring':{key:val for key,val in comp.items() if key!='poses'}},indent=2))
