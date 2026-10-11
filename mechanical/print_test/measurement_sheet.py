from pathlib import Path
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).resolve().parents[2]
pdfmetrics.registerFont(TTFont('JP','C:/Windows/Fonts/msgothic.ttc',subfontIndex=0))
items=[('W','本体幅'),('D','本体奥行'),('H','本体高さ'),('EW','取付耳全幅'),('ET','取付耳厚み'),('PX','取付穴X方向ピッチ'),('PY','取付穴Y方向ピッチ'),('HD','取付穴径'),('SX','左基準面から出力軸中心'),('SY','奥行基準面から出力軸中心'),('SZ','本体上面から軸突出'),('OD','純正ホーン外径/最大幅'),('HT','純正ホーン厚み'),('HP','ホーン穴配置/PCD'),('HH','ホーン固定穴径/深さ'),('HB','ホーン裏面段差/ボス'),('CX','ケーブル出口X'),('CY','ケーブル出口Y'),('CZ','ケーブル出口Z'),('SC','ねじ頭径/工具空間')]
with (P/'docs/servo_measurement_template.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['model','specimen_id','symbol','measurement','unit','manufacturer_nominal','measured','instrument_resolution','datum','notes','status'])
 for model in ['VS-S092J','XL330-M288-T']:
  for code,label in items:w.writerow([model,'',code,label,'mm','','','','','','MEASUREMENT_REQUIRED'])
with (P/'mechanical/print_test/fdm_correction_template.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['feature','nominal_mm','prototype_allowance_mm','actual_measured_mm','required_correction_mm','material','nozzle_mm','status'])
 for feature,nom,allow in [('body_width',19,.2),('body_depth',38,.2),('hole_diameter',3,.2),('screw_clearance',3,.4),('bearing_fit',16,.2),('insert_fit','',''),('magnet_fit',6,.2),('sensor_window',18,.4)]:w.writerow([feature,nom,allow,'','','PLA','','MEASUREMENT_REQUIRED'])
c=canvas.Canvas(str(P/'docs/servo_measurement_sheet.pdf'),pagesize=A4);W,H=A4
def text(x,y,s,size=9):c.setFont('JP',size);c.drawString(x,y,s)
def dim(x1,y1,x2,y2,code):
 c.setLineWidth(.45);c.line(x1,y1,x2,y2)
 dx=x2-x1;dy=y2-y1;l=(dx*dx+dy*dy)**.5;ux=dx/l;uy=dy/l
 for x,y,sgn in [(x1,y1,1),(x2,y2,-1)]:
  p=c.beginPath();p.moveTo(x,y);p.lineTo(x+sgn*ux*5-uy*2,y+sgn*uy*5+ux*2);p.lineTo(x+sgn*ux*5+uy*2,y+sgn*uy*5-ux*2);p.close();c.drawPath(p,fill=1)
 text((x1+x2)/2+3,(y1+y2)/2+3,code,9)
for model in ['VS-S092J','XL330-M288-T']:
 c.rect(24,24,W-48,H-48);text(36,H-47,f'SO-101-custom 現物測定シート / {model}',14)
 text(36,H-66,'第三角法・mm / 図形は測定箇所の説明図。外形・軸位置・穴は未確定。',9)
 text(36,H-84,'個体ID: __________________   日付: __________   測定者: __________',9)
 # Plan above front, right side to right. These schematic views never assert actual mounting geometry.
 x,y=95,570;fw,fh=100,75
 c.rect(x,y,fw,fh);c.circle(x+50,y+38,9);text(x,y-16,'正面参考図 / 出力軸・ホーン',8)
 dim(x,y-28,x+fw,y-28,'W');dim(x-18,y,x-18,y+fh,'H')
 c.rect(x,y+95,fw,65);c.circle(x+50,y+125,8);text(x,y+166,'平面参考図',8);dim(x-18,y+95,x-18,y+160,'D')
 c.rect(x+195,y,60,fh);text(x+192,y-16,'右側面参考図',8);dim(x+195,y-28,x+255,y-28,'D')
 c.setDash(4,2);c.line(x-10,y+38,x+fw+10,y+38);c.line(x+50,y-8,x+50,y+fh+8);c.setDash()
 text(360,690,'SX/SY/SZ: 基準面から軸中心',8);text(360,675,'EW/ET/PX/PY/HD: 取付耳',8)
 text(360,660,'OD/HT/HP/HH/HB: 純正ホーン',8);text(360,645,'CX/CY/CZ: ケーブル出口',8)
 text(36,512,'測定値は空欄。無通電で計測。サーボ分解・スプライン加工は禁止。',9)
 y0=488;cols=[36,75,265,370,550]
 for yy in range(22):c.line(36,y0-yy*17,559,y0-yy*17)
 for xx in [36,75,265,370,559]:c.line(xx,y0,xx,y0-21*17)
 text(41,y0-12,'記号',8);text(80,y0-12,'測定箇所',8);text(270,y0-12,'測定値 mm',8);text(375,y0-12,'基準面・穴数・備考',8)
 for i,(code,label) in enumerate(items):yy=y0-(i+1)*17-12;text(41,yy,code,8);text(80,yy,label,8)
 text(36,108,'ノギス最小表示: ______ mm / 測定位置を写真またはスケッチで記録。',8)
 text(36,93,'穴ピッチは中心間。穴が小さければ外側/内側距離と穴径を併記して算出。',8)
 text(36,78,'ねじ深さは工具で無理に探らない。メーカー資料・純正ねじと照合する。',8)
 text(36,48,'図番 SO101-MEAS-004 / Rev A / 状態 MEASUREMENT_REQUIRED / 2026-10-11',8)
 c.showPage()
c.save();print('Measurement sheet: 2 pages, all measured values blank')
