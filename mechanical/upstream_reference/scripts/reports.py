from pathlib import Path
import json,csv,hashlib
M=Path(__file__).resolve().parents[2];P=M.parent;D=P/'docs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def md(name,text):(D/name).write_text(text,encoding='utf-8')
ref=read(M/'upstream_reference/kinematic_reference.json');pin=ref['pin']
parts=read(M/'follower_six_axis/analysis/part_mass_properties.json');catalog={x['name']:x for x in parts}
mapping=[]
for p in ref['parts']:
    mapping.append(dict(custom_part=p['part']+'.ipt',classification='UNMODIFIED_UPSTREAM',upstream_part=p['part']+'.step',official_commit=pin,official_dimension='Original STEP solid',custom_dimension='Unchanged solid; added datum planes only',reason='Reuse official SO-101 structure',joint=p['link'],strength_effect='Geometry unchanged; printing/material qualification TBD',compatibility='Feetech mounting interfaces retained; replacement coupling HOLD',print_status='OEM geometry available; hybrid release HOLD',manufacturing_hold='motor/horn/support fit; actual FDM mass/strength'))
for name in ['Vstone_Cradle_HOLD','XL330_Cradle_HOLD','Servo_Mount_Coupon','Horn_Adapter_Test','Encoder_Alignment_Test','Bearing_Fit_Coupon']:
    mapping.append(dict(custom_part=name+'.ipt',classification='ORIGINAL_CUSTOM_PART',upstream_part='NONE; supplementary fixture',official_commit=pin,official_dimension='Not applicable',custom_dimension='Native CAD; new mounting coupon / adjustable cradle',reason='Replacement motor footprint or measurement fixture',joint='see BOM',strength_effect='Not qualified for load carrying',compatibility='Horn/fastening/placement HOLD',print_status='coupon geometry ready; cradle structural release HOLD',manufacturing_hold='Measured OEM interface and print qualification'))
with (D/'upstream_parts_mapping.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(mapping[0]));w.writeheader();w.writerows(mapping)
old=[90,100];new=[116.000021,135.000185]
align=read(M/'release_review/axis_alignment.json')
md('upstream_alignment_report.md',f'''# 公式SO-101との整合・2026-10-11
Confirmed / Assumption / TBDを区別する。固定commit `{pin}`。
公式STEPアセンブリをInventor 2026.2に読み込み、実個別STEPからネイティブIPTを生成した。既存Rev Aは変更しない。
出典: https://github.com/TheRobotStudio/SO-ARM100/tree/{pin}/STEP/SO101

| 比較 | 既存Rev A | 今回基準 | 差 |
|---|---:|---:|---:|
| Shoulder Lift–Elbow Flex軸間 | 90 mm | 116.000021 mm | +26.000021 mm (+28.89%) |
| Elbow Flex–Wrist Flex相当 | 100 mm（payload点まで） | 135.000185 mm（手首軸まで） | +35.000185 mm (+35.00%); 終端の意味は異なる |
| 二リンク長合計 | 190 mm | 251.000206 mm | +61.000206 mm (+32.11%); collision-free reachではない |

これはSTEPモデル全長の外形をリンク長と呼んだ値ではなく、公式URDFの関節座標から求めた軸間距離。
Upper_armの肩出力円筒軸、Under_armの肘出力円筒軸を実STEPで抽出し、URDF基準に対する軸直交方向誤差は約0.00005 mm（URDF丸め誤差）だった。
サーボ取付側はモータ出力軸の円筒穴を必ずしも持たない。最寄りの別穴を出力軸として採用していない。実データは`mechanical/release_review/axis_alignment.json`。
追加測定されたWrist_Roll_Pitch軸の整合は同JSONを参照。CAD内の基準座標と現物軸位置の一致は別確認。

個別STEP由来のUpper外形は約142.17×24.50×67.30 mm、Underは約130.80×24.02×64.40 mm（各部品座標）。旧板状Upper90×22×5 / Forearm100×20×5とは支持構造も異なる。
公式全体STEPには歴史的SO100表記が残る部品名がある。SO101ディレクトリの固定データという出所を優先し、SO100の別ファイルに置換していない。

再利用: Followerに公式造形部品11種類、二関節Rev Bに8種類。公式STEP/STLの形状は変更・縮尺変更していない。追加datumは形状を変更しない。
ADAPTER_ONLYは組立適合を示す言葉としてまだ認定しない。現状は原形＋追加クレードルの干渉検討モデル。
公式モータ中心・ホーン出力位置は関節基準として保持。Vstoneケース軸位置・ホーン面・メーカー穴はTBD。XL330はメーカー図面の20×34×26 mm・PCD12・4×φ1.6 DP3 max/M2タッピングを確認、ケース包絡体の内部COMや取付実装はAssumption。
公式6関節とtool frameの座標、RPY、元limitsはkinematic_reference.json。元limitsをPWM180°機へ無条件適用しない。暫定評価範囲PWM各±75°、roll±90°、gripper0..90°はAssumption。

支持、穴、配線、モータ包絡体、実質量/COM、干渉は別表に記録。全到達空間、連続干渉、締結アクセス、ケーブル曲げ半径はTBD。
取り込み全アセンブリの初期材料は現物材料と一致しないためその質量を本Hybridへ流用せず、カスタムCADの材料・overrideを明記する。
''')
md('custom_modifications.md',f'''# カスタム差分
固定公式commit `{pin}`、Apache-2.0。Rev Aは独自90/100 mmのP1として保存。Rev BとFollowerは別ディレクトリ。
1. 公式11部品は形状再利用、IPT化と拘束用datum追加のみ。リンク長変更なし。
2. Vstoneクレードル: 機体38×38.5×19 mm仮定、窓38.6×39.1 mm、左右4 mm支持壁、4 mm底板、独自3.4×20 mmクランプ長穴。メーカー耳穴ではない。干渉・固定・hornはHOLD。
3. XL330クレードル: 窓20.6×34.6 mm、同じ独自クランプ構造。公式holderと干渉し、現状は組立不能。底/側面への固定方式を再設計する必要あり。
4. Vstone4台・XL3302台の包絡体。メーカーCADをカスタムモデルへ転用せず、独自簡略ソリッドを使用。Vstone軸–ケース関係はAssumption。
5. 7個の非製造REF datum carrierは非表示・reference BOM、1e-9 kg質量。基準座標/拘束にのみ使い、物理部品として印刷しない。
6. 二関節Rev Bは公式Baseを追加し、Base Panを3面拘束で固定。肩・肘だけ回転する。panロックの実物締結部品はTBD。
7. Rev Aの4 couponをコピー保持。センサ実装・ホーン結合を成立した扱いにしない。
アダプタだけで成立した場合にADAPTER_ONLYへ変更する。現時点では部品表のUNMODIFIED_UPSTREAMとORIGINAL_CUSTOM_PARTを使い、MODIFIED_UPSTREAMは0。
必要な次変更は干渉しているクレードル/取付局所に限定する。実印刷重量・連続能力で不成立が示されるまでは、公式リンク全体の縮小をしない。
第三者機器入り公式アセンブリとROBOTIS資料はLOCAL_REFERENCE_ONLY、再配布権未確認。無断公開しない。出典・LICENSE・source_manifest.jsonを保持。
''')
md('jis_drawing_rules.md','''# JIS製図ルール
Confirmed: Inventor2026.2 installed ja-JP/Metric/JIS.idwを基に作成。ActiveStandardStyle=Default Standard (JIS)、FirstAngleProjection=False、mm。日本語ＭＳゴシック、A4/A3、第三角法の投影図・記号、枠、部品番号/名称/数量欄/材質/尺度/単位/日付/改訂/作成者/状態を含む。
参照規格: JIS B 0001:2019 機械製図、JIS Z 8315-2:1999 正投影法。日本規格協会の公式書誌で確認。
https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+B+0001%3A2019
https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+Z+8315-2%3A1999
規格全文の条項照合・完全適合認証は未実施。JIS様式採用をJIS完全適合と呼ばない。
図形寸法はDrawingCurveのGeometryIntentへ関連付け、手入力数値で代替しない。ビュー尺度はネイティブ尺度ラベル。断面・詳細・datum・幾何公差・ねじ深さ等が必要なものは製造図の完成までHOLD。
FDMにJIS B0405普通公差を一律適用しない。取付窓はケース実測とcoupon測定、ねじ穴/磁石座/軸受座/インサートは個別測定。公差記号だけで精度を保証しない。
元Rev Aの32枚は保管。今回重要部品と組立図から別IDWへ置換し、残りの旧ISO図はJIS化未実施と記録する。
テンプレートはmechanical/templates/SO101_JIS_A4.idw、A3.idw。再読込して使用し、日本語PDFを実表示レビューする。
数量欄がBOM参照のとき同番号のBOMを必須とする。材料候補は実部品の製造指定が確定するまでHOLD。
''')
six=read(M/'follower_six_axis/analysis/assembly.json');two=read(M/'two_joint_revb/analysis/assembly.json')
tor=read(M/'follower_six_axis/analysis/torque_analysis.json');tt=read(M/'two_joint_revb/analysis/torque_analysis.json')
table='|軸|motor|50g静的Nm|動作上界Nm|1.25設計目標Nm|\n|---|---|---:|---:|---:|\n'
case=tor['cases'][1]
for i,j in enumerate(ref['joints']):table+=f"|{j['name']}|{j['motor']}|{case['sampled_static_peak_Nm'][i]:.4f}|{case['motion_bound_Nm'][i]:.4f}|{case['design_target_1_25_Nm'][i]:.4f}|\n"
md('six_axis_design_review.md',f'''# 6軸Follower設計レビュー
Confirmed: `SO101_Custom_Follower_RevA.iam`をInventor2026.2で保存・再読込。{six['occurrences']} occurrences、{len(six['constraints'])} constraints。Base reference固定、6つの回転軸でそれぞれ並進0/回転1をGetDegreesOfFreedom(out...)で確認し、各軸10°の独立動作とUpdate2成功を記録。
公式リンク・関節配置を維持。製造・組立・駆動を承認するモデルではない。

{table}
CAD全ソリッド質量 {six['mass_kg']:.6f} kg、COM {six['com_mm']} mm。個別COM/慣性はpart_mass_properties.json。公式形状PET1541 kg/m³、追加クレードル既定材料1000 kg/m³、Vstone42g/XL18g override。実印刷重量ではない。
無負荷の肩static {tor['cases'][0]['sampled_static_peak_Nm'][1]:.4f} /motion {tor['cases'][0]['motion_bound_Nm'][1]:.4f} Nm。
50g肩は公称0.9022Nmを超える。全ソリッド条件で採用不可。FDM実質量と連続能力が不明なため、軽量造形後も成立とは断定できない。
gripperは仮定5N×35mm=0.175Nmの接触トルクを含む。把持指摩擦・荷重・形状・horn伝達は未検証。
速度各0.1rad/s、加速度各0.2rad/s²。CAD COMによる重力、経路半径と慣性traceによる保守的加速上界、6001姿勢の静的探索。格子外global最大の証明ではない。
fastener、センサ完成品、配線抵抗、反射ロータ慣性、衝撃、熱、実ホーン結合を含まない。限界payloadはTBD。

暫定可動域: PWM各±75°、XLroll±90°、gripper0..90°。CAD拘束にはまだ機械ストッパ/可動限界を確定実装していない。元URDF限界は通信・現物角度とは別。
干渉: 独立軸ごと-30/-15/0/15/30°で30姿勢を検査、衝突あり。連続全域・複合全域はNOT VERIFIED。検査結果をPASSとしない。実motor/horn/board/cableモデルが未確定。
Encoder: PWM4軸出力側へ追加ブラケット方式を検討、AS5600同一address0x36には別bus/mux。AS5048AならSPI個別CS。PCB寸法・磁石・air gap・固定面はTBD。6軸に搭載成立するsensor CADは未完成。
電源: Vstone7.4V候補、XL5V、GND基準共通、PC USBは論理のみ、E-stopで両motor rail遮断、落下受け。電流/保護定格未確定。
LeRobot: 固定版0.6.2 / commit b9cb121cb7d4e3e26ec5c906d08dda68d151ba52でxl330-m288対応確認済み。今回ライブ最新版/API再実行は未実施。custom Robotで6*.pos観測/指令、PWMは実角度sensor必須。STS用標準SO101クラスへmotor名だけ変更して接続しない。
肩補償: まず重量実測、次に交換可能な小型補助ばねブラケットを検討。旧RevAのばね点/k/残留トルクをこの長い6軸へ流用しない。選定ばねと取付CADは未完成。

二関節Rev B: {two['occurrences']} occurrences / {len(two['constraints'])} constraints、公式ベース＋pan固定、2自由度。質量{two['mass_kg']:.6f}kg。50gの肩static/motion {tt['cases'][1]['sampled_static_peak_Nm'][1]:.4f}/{tt['cases'][1]['motion_bound_Nm'][1]:.4f}Nm、肘 {tt['cases'][1]['sampled_static_peak_Nm'][2]:.4f}/{tt['cases'][1]['motion_bound_Nm'][2]:.4f}Nm。基部追加は固定部なので肩/肘負荷を変えない。
重要HOLD: 公式holderとクレードルの重なり、OEMhorn接続、motor軸–case、pan固定、センサ保持、軸受/支持、ねじ締結、材料、熱/連続能力、ストッパ、配線。
今回製造リリースBLOCKED。幾何・拘束・保存済みCADを削除せず、次に干渉しているマウントのみ局所修正する。
''')
rows=[]
for b in six['body_records']:
    name=b.get('source_part',b['name']);rows.append(dict(occurrence=b['name'],part=name,quantity=1,classification=b['classification'],status='ENVELOPE_NOT_MANUFACTURED' if b['classification']=='ASSUMPTION_ENVELOPE' else 'MANUFACTURING_HOLD',material='as CAD; printing PLA+/PETG TBD',interface_hold='measured horn and fastening; interference; printed tolerance'))
with (M/'follower_six_axis/mechanical_bom.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for folder in ['two_joint_revb','follower_six_axis']:
    (M/folder/'assembly_guide.md').write_text('''# 組立準備・HOLD
今回のIAMは機構・インターフェース検討用。印刷、機械組立、通電は未承認。
公式ベース固定→pan固定/駆動の取付を確定→肩housingと純正horn adapter→Upper→肘housing/horn→Under→手首/roll/jaw（6軸のみ）→output sensor、の順で検討。
干渉しているクレードルはそのまま組み付けない。純正horn穴/スプライン・出力面・ねじ深さの現物計測、局所マウント再設計、無通電手動全域確認が先。
ねじ・軸受・ケーブル・受け台・E-stopが確定するまで実機を組み立て/動かす手順には進まない。
''',encoding='utf-8')
(M/'adapters/print_plan.md').write_text('''# 最初の造形準備
Confirmed: Adventurer5M Pro、220×220×220mm。ノズル/材料/残量はTBD。G-codeなし、印刷なし。
Servo_Mount_Couponを最優先。次はHorn_Adapter_Test、Encoder_Alignment_Test、Bearing_Fit_Coupon。全て寸法確認専用で、モータ荷重を載せる製品ではない。
PLA+またはPETG、0.4mm候補/0.2mm層、外周4、底上面5層、couponは100%充填候補。広い平面をbedへ、穴軸はZ、基本supportなし。cradleは底をbedへ支持壁をZ、構造荷重は未認定。
window38.6×39.1とケース隙間を測る。slot3.4×20は独自クランプ用。horn OD30/t4/access5/PCD24は自作側だけ、メーカーhorn穴ではない。encoder32×32/t4/window18は汎用基板fixture、磁気性能試験は未実施。625coupon65×25×8の16.0/16.2/16.4はfit比較用。部品表のHOLD寸法は穴あけ/圧入しない。
補正は実測外形/穴/窓別に記録し、軸受は無理な圧入をしない。公差は印刷後測定で検証、JIS普通公差一律適用なし。
mm/STLmanifold/外形はmesh_validation.json。filament gと時間は未知のnozzle/material/profileのslicerが必要なためTBD。出力STLは印刷指示ではない。
全フレーム、cradleの荷重利用、motor envelope/REF datumの印刷はHOLD/禁止。元officialSTLを形状の正本として再利用する。
''',encoding='utf-8')
print('Authored alignment, mapping, modification, JIS, six-axis review, BOM and build preparation documents.')
