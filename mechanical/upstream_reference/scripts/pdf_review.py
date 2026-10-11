from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
from pypdf import PdfReader
M=Path(__file__).resolve().parents[2];out=M/'release_review/pdf_qa';out.mkdir(exist_ok=True)
exe=Path('${USERPROFILE}/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
files=[p for folder in ['adapters','two_joint_revb','follower_six_axis'] for p in (M/folder/'pdf').glob('*.pdf')]
records=[];images=[]
for file in files:
    reader=PdfReader(file);text=''.join(p.extract_text() or '' for p in reader.pages)
    prefix=out/file.stem;subprocess.run([str(exe),'-png','-singlefile','-scale-to','1400',str(file),str(prefix)],check=True,creationflags=0x08000000)
    im=Image.open(prefix.with_suffix('.png')).convert('RGB');images.append((file.stem,im.copy()))
    records.append(dict(file=str(file.relative_to(M)).replace('\\','/'),pages=len(reader.pages),japanese_present='第三角法' in text,hold_present='HOLD' in text,nonblank=im.convert('L').getextrema()[0]<100,visual_status='PENDING'))
for start in range(0,len(images),4):
    contact=Image.new('RGB',(1800,1400),'#ddd');draw=ImageDraw.Draw(contact)
    for idx,(label,im) in enumerate(images[start:start+4]):
        im.thumbnail((875,660));x=10+idx%2*900;y=30+idx//2*700;contact.paste(im,(x,y));draw.text((x,y-20),label,fill='black')
    contact.save(out/f'contact_{start//4+1}.png')
(M/'release_review/pdf_validation.json').write_text(json.dumps(records,indent=2),encoding='utf-8');print('Rendered',len(files),'PDFs')
