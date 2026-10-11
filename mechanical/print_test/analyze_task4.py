from pathlib import Path
import json,csv
import numpy as np
M=Path(__file__).resolve().parents[1];P=M.parent;R=M/'release_review/task4'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
ref=read(M/'upstream_reference/kinematic_reference.json');joints=ref['joints']
parts={p['name']:p for p in read(M/'follower_revb/analysis/part_mass_properties.json')}
limits=np.array([[-np.pi*75/180,np.pi*75/180]]*4+[[-np.pi/2,np.pi/2],[0,np.pi/2]])
idx={'base_link':-1,**{j['child']:i for i,j in enumerate(joints)}}
rng=np.random.default_rng(101);qs=np.vstack([np.zeros(6),rng.uniform(limits[:,0],limits[:,1],(6000,6))])
def frames(q):
 n=len(q);F={'base_link':np.repeat(np.eye(4)[None],n,axis=0)};O=[];A=[]
 for k,j in enumerate(joints):
  pre=F[j['parent']]@np.array(j['origin']);O.append(pre[:,:3,3]/1000);A.append(pre[:,:3,2]);r=np.repeat(np.eye(4)[None],n,axis=0);r[:,0,0]=r[:,1,1]=np.cos(q[:,k]);r[:,0,1]=-np.sin(q[:,k]);r[:,1,0]=np.sin(q[:,k]);F[j['child']]=pre@r
 return F,np.stack(O,axis=1),np.stack(A,axis=1)
def bodies(meta):
 out=[]
 for b in meta['body_records']:
  key=b.get('source_part',b['name']);p=parts[key];local=np.array(b['local']);com=(local@np.r_[p['com_mm'],1])[:3]/1000
  out.append(dict(name=b['name'],part=key,link=b['link'],mass=p['mass_kg'],com=com,trace=sum(p['inertia_kg_m2'][:3])))
 return out
def evaluate(B,q,payload,two=False):
 F,O,A=frames(q);G=np.zeros((len(q),6));radius=np.zeros((6,len(B)+1));masses=np.array([b['mass'] for b in B]+[payload]);trace=np.array([b['trace'] for b in B]+[0.])
 for n,b in enumerate(B):
  pos=np.einsum('nij,j->ni',F[b['link']][:,:3,:3],b['com'])+F[b['link']][:,:3,3]/1000;last=idx[b['link']];force=np.array([0,0,-b['mass']*9.80665])
  for k in range(last+1):
   G[:,k]+=np.einsum('ni,ni->n',A[:,k],np.cross(pos-O[:,k],force))
   radius[k,n]=np.linalg.norm(b['com'])+sum(np.linalg.norm(np.array(joints[l]['origin'])[:3,3])/1000 for l in range(k+1,last+1))
 if two:
  pt=F['wrist_link'][:,:3,3]/1000;last=2;tool=np.zeros(3)
 else:
  toolmat=np.linalg.inv(np.array(ref['frames']['gripper_link']))@np.array(ref['tool']);pt=(F['gripper_link']@toolmat)[:,:3,3]/1000;last=4;tool=toolmat[:3,3]/1000
 for k in range(last+1):
  G[:,k]+=np.einsum('ni,ni->n',A[:,k],np.cross(pt-O[:,k],[0,0,-payload*9.80665]));radius[k,-1]=np.linalg.norm(tool)+sum(np.linalg.norm(np.array(joints[l]['origin'])[:3,3])/1000 for l in range(k+1,last+1))
 if two:radius[[0,3,4,5]]=0;G[:,[0,3,4,5]]=0
 active=radius>0;acc=np.sum(.2*radius,axis=0)+np.sum(.1*active,axis=0)**2*np.max(radius,axis=0)
 D=(radius*(masses*acc)).sum(axis=1)+(active*trace*(.2*active.sum(axis=0)+(.1*active.sum(axis=0))**2)).sum(axis=1)
 return G,D
outputs={}
for folder,two in [('two_joint_revc',True),('follower_revb',False)]:
 meta=read(M/folder/'analysis/assembly.json');B=bodies(meta);q=qs.copy()
 if two:q[:,[0,3,4,5]]=0
 cases=[]
 for load in [0,.05,.1]:
  G,D=evaluate(B,q,load,two);absolute=np.abs(G);peak=absolute.max(axis=0);where=absolute.argmax(axis=0);contact=0 if two else .175;peak[5]+=contact
  cases.append(dict(payload_kg=load,sampled_static_peak_Nm=peak.tolist(),motion_bound_Nm=(peak+D).tolist(),design_target_1_25_Nm=((peak+D)*1.25).tolist(),sampled_worst_q_rad=q[where].tolist(),grip_contact_assumption_Nm=contact))
 torque=dict(cases=cases,samples=len(q),limits_rad=limits.tolist(),velocity_rad_s=.1,acceleration_rad_s2=.2,method='Native mass/COM plus exact vectorized FK gravity; conservative path-radius inertia acceleration bound. Sampled maximum not global proof.',mass_model='Native full-solid PLA 1240 kg/m3 mass override; motor42/18g. Inertia comes from native library material and may remain conservative after mass override; not sliced or measured.',payload_location='Wrist-flex axis; hypothetical attachment TBD' if two else 'Official fixed gripper tool frame; not moving jaw',continuous_torque='UNKNOWN',omissions=['unmeasured horns','fasteners','sensors','cables','rotor reflected inertia','friction','thermal limits','real FDM mass/strength'])
 save(M/folder/'analysis/torque_analysis.json',torque)
 save(M/folder/'analysis/mass_properties.json',dict(total_mass_kg=meta['mass_kg'],com_mm=meta['com_mm'],parts=[{**b,'com':b['com'].tolist()} for b in B],scope='CAD full-solid/overrides; native assembly inertia saved separately; physical test not run'))
 outputs[folder]=torque;print(folder,meta['mass_kg'],cases[1]['sampled_static_peak_Nm'],cases[1]['motion_bound_Nm'])
# Separate changes of solid mass from hypothetical infill reductions. No strength-release from a density factor.
B=bodies(read(M/'follower_revb/analysis/assembly.json'));comparison=[]
for fraction in [1,.7,.5,.35,.25]:
 trial=[dict(b) for b in B]
 for b in trial:
  if b['part'] not in ['Vstone_Envelope','XL330_Envelope']:b['mass']*=fraction;b['trace']*=fraction
 G,D=evaluate(trial,qs,.05);peak=np.abs(G).max(axis=0)
 comparison.append(dict(plastic_mass_fraction=fraction,total_mass_kg=sum(b['mass'] for b in trial),static_Nm=peak.tolist(),motion_Nm=(peak+D).tolist(),continuous_requirement_margin_1_25_Nm=(1.25*peak).tolist(),status='CALCULATED_SENSITIVITY_ONLY; shell/infill geometry/strength and sliced mass not validated'))
save(R/'lightweight_sensitivity.json',comparison)
with (R/'part_mass_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['part','old_cad_kg','new_cad_kg','delta_kg','scope']);old={p['name']:p for p in read(M/'follower_six_axis/analysis/part_mass_properties.json')}
 for key,p in parts.items():w.writerow([key,old.get(key,{}).get('mass_kg',''),p['mass_kg'],p['mass_kg']-old[key]['mass_kg'] if key in old else '', 'Native CAD proxy; not measured'])
# Shoulder spring screen in its motion plane, angle from horizontal, not raw URDF command zero.
spring=[];a=r=.06;k=100;free=.06;initial=10
for angle in range(-75,76,5):
 th=np.deg2rad(angle);L=np.sqrt(a*a+r*r-2*a*r*np.sin(th));arm=a*r*np.cos(th)/L;force=0 if L < free else initial+k*(L-free);spring.append(dict(angle_from_horizontal_deg=angle,length_mm=L*1000,extension_mm=max(0,(L-free)*1000),moment_arm_mm=arm*1000,force_N=force,compensation_Nm=force*arm))
save(R/'gravity_compensation.json',dict(status='ASSUMPTION; free-length60mm spring slack where span<60mm; full-range compensation infeasible; no native spring bracket created; selection/anchor/retention/strength HOLD',fixed_anchor_local_mm=[0,60,0],rotating_anchor_radius_mm=60,stiffness_N_m=k,free_length_mm=free*1000,initial_tension_N=initial,rows=spring,required_length_range_mm=[min(s['length_mm'] for s in spring),max(s['length_mm'] for s in spring)],broken_spring_behavior='Full uncompensated CAD gravity loads return; motor fit not certified, catch/support mandatory',alternative='Torsion needs preload 0.5..1Nm; constant force varies with lever; counterweight0.6Nm at80mm needs0.765kg excluding holder'))
save(R/'strength_screen.json',dict(status='CALCULATED SCREEN ONLY; manufacturing HOLD',wall_force_N=25,cantilever_mm=12,width_mm=38.6,thickness_mm=3,bending_MPa=6*25*.012/(.0386*.003**2)/1e6,notch_factor_assumption=3,PLA_FDM_allowable_assumption_MPa=10,deflection_mm=4*25*.012**3/(1.5e9*.0386*.003**3)*1000,limits='Notch/fixation, base frame, screw load, anisotropy, creep not qualified. Not proof that removed base material or lightened bracket is adequate. Do not manufacture as load-bearing.'))
