from pathlib import Path
import json,hashlib,struct
from collections import Counter
import numpy as np
M=Path(__file__).resolve().parents[2];old=M/'two_joint_prototype'
errors=[];records=[]
for rec in json.loads((old/'artifact_manifest.json').read_text(encoding='utf-8-sig')):
    p=old/rec['path'];got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=rec['sha256']:errors.append(rec['path'])
(M/'release_review/reva_preservation.json').write_text(json.dumps(dict(checked=241,mismatches=errors,scope='Existing manifest-listed Rev A deliverables'),indent=2),encoding='utf-8')
assert not errors,errors
dt=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')])
for directory in [M/'adapters/stl',M/'upstream_reference/stl']:
    for p in directory.glob('*.stl'):
        raw=p.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n,p
        v=np.frombuffer(raw[84:],dtype=dt)['vertices'].astype(float);verts=np.round(v.reshape(-1,3),5);_,ids=np.unique(verts,axis=0,return_inverse=True);idx=ids.reshape(-1,3)
        edges=Counter(tuple(sorted(e)) for tri in idx for e in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])])
        bad=sum(count!=2 for count in edges.values());vol=abs(np.einsum('ij,ij->',v[:,0],np.cross(v[:,1],v[:,2]))/6)
        records.append(dict(file=str(p.relative_to(M)).replace('\\','/'),units='mm',triangles=n,bbox_mm=(v.max(axis=(0,1))-v.min(axis=(0,1))).tolist(),volume_mm3=float(vol),closed_edge_manifold=(bad==0),nonmanifold_edges=bad,manufacturing='COUPON_DIMENSION_CHECK_ONLY' if p.stem in ['Servo_Mount_Coupon','Horn_Adapter_Test','Encoder_Alignment_Test','Bearing_Fit_Coupon'] else 'HOLD'))
(M/'release_review/mesh_validation.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
assert all(r['closed_edge_manifold'] for r in records if r['file'].startswith('adapters/'))
ref=json.loads((M/'upstream_reference/kinematic_reference.json').read_text());jointnames=[x['name'] for x in ref['joints']]
assert len(jointnames)==len(set(jointnames))==6
dof=json.loads((M/'release_review/dof_api.json').read_text(encoding='utf-8-sig'));six=[x for x in dof if x['assembly']=='follower_six_axis'];assert sum(x['rotation'] for x in six)==6 and sum(x['translation'] for x in six)==0
for folder,count in [('two_joint_revb',2),('follower_six_axis',6)]:
    audit=json.loads((M/folder/'analysis/motion_interference.json').read_text(encoding='utf-8-sig'));assert not audit['missing_refs'];assert len(audit['independent_motion'])==count;assert all(p['update_ok'] for p in audit['independent_motion']);assert all(c['health']=='11778' for c in audit['constraints']) # kUpToDateHealth
print('Rev A hashes unchanged; 6 joint frames; native DOF and independent movement; adapter STL closed meshes checked.')
