from pathlib import Path
import subprocess,json
from pypdf import PdfReader
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
poppler=Path('${USERPROFILE}/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
out=ROOT/'views/pdf_qa';out.mkdir(exist_ok=True)
records=[];images=[]
for pdf in sorted((ROOT/'pdf').glob('*.pdf')):
    reader=PdfReader(pdf)
    if len(reader.pages)!=1:raise AssertionError(pdf.name)
    text=reader.pages[0].extract_text()
    if pdf.stem not in text:raise AssertionError('Missing drawing label: '+pdf.name)
    prefix=out/pdf.stem
    subprocess.run([str(poppler),'-png','-singlefile','-scale-to','950',str(pdf),str(prefix)],check=True,creationflags=0x08000000)
    image=Image.open(prefix.with_suffix('.png')).convert('RGB');images.append((pdf.stem,image))
    records.append({'file':pdf.name,'pages':1,'label_verified':True,'rendered':str(prefix.with_suffix('.png').relative_to(ROOT)),'status':'rendered; visual review via contact sheet'})
for start in range(0,len(images),8):
    sheet=Image.new('RGB',(1600,2360),'#e5e8ed');draw=ImageDraw.Draw(sheet)
    for idx,(name,im) in enumerate(images[start:start+8]):
        im.thumbnail((780,552));x=(idx%2)*800+10;y=(idx//2)*590+28;sheet.paste(im,(x,y));draw.text((x,y-18),name,fill='black')
    sheet.save(out/f'contact_{start//8+1}.png')
(ROOT/'analysis/pdf_validation.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(f'{len(records)} PDFs rendered and label/page count checked.')
