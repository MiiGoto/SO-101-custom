"""Check exported STL dimensions/closed edges/volume and render actual meshes."""
from pathlib import Path
from collections import Counter
import json,struct
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
meshes={};records=[]
for path in sorted((ROOT/'stl').glob('*.stl')):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:raise ValueError(f'Not binary STL: {path}')
    dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
    v=np.frombuffer(data,dtype=dtype,offset=84,count=n)['vertices'].astype(float)
    meshes[path.stem]=v
    edges=Counter()
    for tri in v:
        p=[tuple(np.round(x,5)) for x in tri]
        for i,j in ((0,1),(1,2),(2,0)):edges[tuple(sorted((p[i],p[j])))]+=1
    volume=abs(float(np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2])).sum()/6))
    low=v.min(axis=(0,1));high=v.max(axis=(0,1))
    records.append({'file':path.name,'triangles':n,'minimum_mm':low.tolist(),'maximum_mm':high.tolist(),'size_mm':(high-low).tolist(),'mesh_volume_mm3':volume,'non_two_sided_edges':sum(x!=2 for x in edges.values()),'within_220_cube_when_reoriented':bool(np.all(high-low<=220))})
expected={'Base':(130,8,85),'Servo_Envelope':(38,38.5,19),'Servo_Mount_Coupon':(52,52,4),'Horn_Adapter_Test':(30,30,4),'Encoder_Alignment_Test':(32,32,4),'Bearing_Fit_Coupon':(65,25,8)}
for name,size in expected.items():
    actual=next(p['size_mm'] for p in records if p['file']==name+'.stl')
    if not np.allclose(actual,size,atol=.05):raise AssertionError((name,actual,size))
if any(r['non_two_sided_edges'] for r in records): raise AssertionError([(r['file'],r['non_two_sided_edges']) for r in records if r['non_two_sided_edges']])
(ROOT/'analysis/stl_validation.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
assembly=[('Base',(0,0,0)),('Shoulder_Mount',(0,0,0)),('Servo_Envelope',(0,0,0)),('Upper_Arm',(0,0,0)),('Servo_Horn_Adapter',(0,0,0)),('Elbow_Mount',(0,0,0)),('Servo_Envelope',(90,0,34)),('Forearm',(90,0,0)),('Elbow_Horn_Adapter',(90,0,0)),('Payload_Mount',(90,0,0))]
audit=ROOT/'analysis/kinematic_audit.json'
if audit.exists():
    refs=json.loads(audit.read_text(encoding='utf-8-sig')).get('reference_geometry_checks',[])
    if refs:assembly=[(p['part'],p['position_mm']) for p in refs]
def render(items,path,title):
    colors=[(142,156,176),(113,132,158),(47,68,91),(70,154,188),(196,132,58),(86,137,153),(47,68,91),(67,162,135),(204,145,69),(178,141,74)]
    # Orthographic mesh preview, not an Inventor UI screenshot.
    camera=np.array([[.88,.15,-.45],[-.12,.985,.09],[.45,-.025,.89]])
    rows=[]
    for i,(name,offset) in enumerate(items):
        t=(meshes[name]+np.array(offset))@camera.T
        for tri in t:rows.append((tri[:,2].mean(),tri,colors[i%len(colors)]))
    allv=np.concatenate([t for _,t,_ in rows]);lo=allv[:,:2].min(0);hi=allv[:,:2].max(0)
    scale=min(1100/(hi[0]-lo[0]),660/(hi[1]-lo[1]));image=Image.new('RGB',(1280,850),'#f3f5f8');draw=ImageDraw.Draw(image)
    for _,tri,color in sorted(rows,key=lambda r:r[0]):
        pts=[(90+(p[0]-lo[0])*scale,760-(p[1]-lo[1])*scale) for p in tri]
        normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);shade=.68+.3*abs(normal[2])/(np.linalg.norm(normal)+1e-9)
        col=tuple(int(c*shade) for c in color);draw.polygon(pts,fill=col)
    draw.text((24,20),title,fill='#15213a');draw.text((24,42),'Actual exported STL meshes / fit-study only / hardware assembly HOLD',fill='#15213a');image.save(path)
render(assembly,ROOT/'views/assembly_mesh_preview.png','SO101 Two Joint P1: 90 mm + 100 mm')
render([('Servo_Mount_Coupon',(0,0,0)),('Horn_Adapter_Test',(80,0,0)),('Encoder_Alignment_Test',(135,0,0)),('Bearing_Fit_Coupon',(200,0,0))],ROOT/'views/coupons_mesh_preview.png','Four dimension-check coupons')
print(f'{len(records)} closed STL meshes; critical dimensions match; previews saved.')
