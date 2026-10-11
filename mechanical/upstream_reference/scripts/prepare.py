"""Pin provenance and retain official joint frames; never fabricate servo interfaces."""
from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parents[1]; P=R.parents[1]
PIN='a758567c3978dfeefe282ede0500085a48fe8f78'
def transform(xyz,rpy):
    x,y,z=map(float,rpy.split());cx,sx=np.cos(x),np.sin(x);cy,sy=np.cos(y),np.sin(y);cz,sz=np.cos(z),np.sin(z)
    t=np.eye(4);t[:3,:3]=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    t[:3,3]=np.array(list(map(float,xyz.split())))*1000;return t
urdf=ET.parse(P/'mechanical/reference/Simulation/SO101/so101_new_calib.urdf').getroot()
names=['shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper']
joints=[];frames={'base_link':np.eye(4)}
for name in names:
    j=urdf.find(f"joint[@name='{name}']");o=j.find('origin');t=transform(o.get('xyz'),o.get('rpy'))
    parent=j.find('parent').get('link');child=j.find('child').get('link');frames[child]=frames[parent]@t
    lim=j.find('limit');joints.append(dict(name=name,parent=parent,child=child,origin=t.tolist(),world=frames[child].tolist(),limits_rad=[float(lim.get('lower')),float(lim.get('upper'))],motor='VS-S092J' if len(joints)<4 else 'XL330-M288-T'))
# Fixed tool frame
j=urdf.find("joint[@name='gripper_frame_joint']");o=j.find('origin');tool=frames[j.find('parent').get('link')]@transform(o.get('xyz'),o.get('rpy'))
map_names={p.stem.lower():p.stem for p in (R/'step').glob('*.step')}
visuals=[]
for link in urdf.findall('link'):
    for v in link.findall('visual'):
        filename=v.find('geometry/mesh').get('filename');stem=Path(filename).stem
        if stem.startswith('sts3215'):continue # Third-party motor models excluded from custom deliverables.
        key=stem.rsplit('_v',1)[0];official=map_names.get(key)
        if not official:continue
        o=v.find('origin');local=transform(o.get('xyz'),o.get('rpy'));world=frames[link.get('name')]@local
        visuals.append(dict(part=official,link=link.get('name'),local=local.tolist(),world=world.tolist(),classification='UNMODIFIED_UPSTREAM',interface_status='HOLD: original Feetech interface not qualified for replacement motor'))
data=dict(pin=PIN,units='mm',joints=joints,frames={k:v.tolist() for k,v in frames.items()},parts=visuals,tool=tool.tolist(),source='Official URDF frames; STEP correspondence must be independently measured')
(R/'kinematic_reference.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
manifest=[dict(file=str(f.relative_to(R)).replace('\\','/'),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),commit=PIN,source='https://github.com/TheRobotStudio/SO-ARM100') for folder in ['step','stl'] for f in (R/folder).glob('*') if f.is_file()]
(R/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(R/'NOTICE.md').write_text(f'''# Official design provenance\nSO-101 design: TheRobotStudio / Hugging Face / contributing authors.\nSource https://github.com/TheRobotStudio/SO-ARM100/tree/{PIN}\nPinned commit {PIN}; Apache-2.0 LICENSE retained verbatim.\nDownloaded individual STEP/STL geometry is unchanged. Native imports change file format only.\nCustom adapters and joint datum features must be identified in custom_modifications.md.\nOfficial assembly STEP may contain external vendor motor models: LOCAL_REFERENCE_ONLY, redistribution HOLD pending separate permission.\nNo external vendor mesh or CAD is copied into the custom Follower; independently authored envelopes represent unknown interfaces.\n''',encoding='utf-8')
print('reference',len(visuals),'parts',len(joints),'joints')
