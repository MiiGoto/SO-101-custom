from pathlib import Path
import json,csv,hashlib
M=Path(__file__).resolve().parents[2];P=M.parent;D=P/'docs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
draws=read(M/'release_review/drawing_validation.json');pdfs=read(M/'release_review/pdf_validation.json')
for p in pdfs:p['visual_status']='REVIEWED: nonblank/Japanese/third-angle views/title block/border/HOLD checked; manufacturing dimensions still HOLD'
save(M/'release_review/pdf_validation.json',pdfs)
quality='''# JIS図面品質レビュー・2026-10-11
全10PDFを1400pxに描画し、全ページをcontact1..3と重要couponの個別表示で確認。はみ出していた組立投影図は1:5で再配置、大きすぎた尺度ラベルは縮小・寸法から離して再出力した。
Confirmed: native JIS standard、Default(JIS)寸法style、third angle（FirstAngleProjection=False）、mm、A4 297×210/A3 420×297。日本語表示、枠・表題欄・図番、4views、モデル関連寸法を確認。テンプレートA4/A3を実際に再読込。
JIS B0001:2019 / Z8315-2:1999の書誌・様式を参照。規格全文による全条項・記号寸法・幾何公差適合は未検証。
全ての製作図を完成としない。未知のhorn/ねじ深さ、位置datum、インサート、必要断面、FDM fit、材料/強度はHOLD。公式Upper/Under図は重要部品の形状参照用で、全体外形・全穴位置を網羅した製造図ではない。cradleも締結側の設計未確定。
旧RevAの32枚は保存、今回全32枚をJIS製造図へ完成した扱いにはしない。

|IDW|関連寸法数|標準|第三角法|PDF表示|製造リリース|
|---|---:|---|---|---|---|
'''
for d in draws:
    if d['folder']=='templates':continue
    quality+=f"|{d['file']}|{d['associated_dimensions']}|{d['standard']}|確認|確認・日本語正常|HOLD|\n"
quality+='''
非空白・図形の用紙内配置・文字・材質候補/部品番号・HOLD表示・モデル参照欠落なしは確認済み。寸法線/リーダーを量産製図として最終承認するレビューと、実物製作/検査可能な全寸法網羅は未完了。
組立図番号はSO101-ASM-B-001 / SO101-ASM-A-001、部品図番号SO101-B-001..008で重複を除いた。数量欄はBOM参照であり、下面に全ねじ製造仕様が確定した意味ではない。
'''
(D/'drawing_quality_review.md').write_text(quality,encoding='utf-8')
for folder in ['two_joint_revb','follower_six_axis']:
    a=read(M/folder/'analysis/assembly.json');audit=read(M/folder/'analysis/motion_interference.json');poses=audit['sampled_sweeps']
    text=f'# 干渉・可動性: {folder}\n\nNative再読込、参照欠落{len(audit["missing_refs"])}、拘束{len(audit["constraints"])}件はkUpToDateHealth。独立回転{len(audit["independent_motion"])}軸はUpdate成功。\n'
    text+=f'姿勢検査{len(poses)}、各軸のみ-30/-15/0/15/30°。全域連続掃引・全軸組合せ・ケーブル/締結アクセスはNOT VERIFIED。\n\n|軸|角度deg|重なり件数|最大重なりmm³|\n|---|---:|---:|---:|\n'
    for p in poses:text+=f'|{p["joint"]}|{p["angle_deg"]}|{len(p["interferences"])}|{max((x["volume_mm3"] for x in p["interferences"]),default=0):.2f}|\n'
    text+='\n衝突あり。包絡体の不確かな軸位置/ホーン寸法も含むため現物の衝突量そのものではないが、CAD干渉をPASSと扱わない。局所マウントとsensorの完成後に再評価。\n'
    (M/folder/'interference_report.md').write_text(text,encoding='utf-8')
    rows=[]
    for b in a['body_records']:rows.append(dict(occurrence=b['name'],part=b.get('source_part',b['name']),quantity=1,classification=b['classification'],status='ENVELOPE_NOT_MANUFACTURED' if b['classification']=='ASSUMPTION_ENVELOPE' else 'MANUFACTURING_HOLD'))
    with (M/folder/'mechanical_bom.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Complete summary includes fixed base, without rerunning unchanged moving-link dynamics.
    props={x['name']:x for x in read(M/'follower_six_axis/analysis/part_mass_properties.json')}
    summary=read(M/folder/'analysis/mass_properties.json');summary['total_mass_kg']=a['mass_kg'];summary['com_mm']=a['com_mm'];summary['all_body_records']=[dict(name=b['name'],link=b['link'],source_part=b.get('source_part',b['name']),mass_kg=props[b.get('source_part',b['name'])]['mass_kg']) for b in a['body_records']];save(M/folder/'analysis/mass_properties.json',summary)
counts={folder:read(M/folder/'analysis/assembly.json') for folder in ['two_joint_revb','follower_six_axis']}
readme=f'''# 公式SO-101継承/JIS・成果と製造レビュー
2026-10-11。Inventor2026.2による実ファイルのみ生成済みと記録。計画のゼロからの再設計を更新し、旧RevAは保持。

|成果|実体|状態|
|---|---|---|
|公式個別STEP/STL|各12ファイル + LICENSE/NOTICE + pin/hash|取得済み・原形維持|
|公式全アセンブリSTEP/import IAM|ローカル参照のみ|取得/読込済み・第三者モデル再配布HOLD|
|Follower部品IPT|11公式形状 + 7非製造datum|26新規使用IPT全てsolid/参照欠落0（adapter8を含む）|
|二関節RevB|two_joint_revb/iam/SO101_TwoJoint_RevB.iam|16occ/43拘束、肩・肘2回転を確認|
|6軸Follower|follower_six_axis/iam/SO101_Custom_Follower_RevA.iam|30occ/81拘束、6回転を確認|
|JISテンプレート|templates/SO101_JIS_A4.idw / A3.idw|保存・再読込済み|
|JIS図面|8部品IDW + 2組立IDW +10PDF|PDF表示確認、全寸法網羅と製造承認HOLD|
|STEP|2組立 +2クレードル|Inventorから実出力|
|STL|2クレードル +4coupon +12公式STL|閉じたmesh確認、couponのみ寸法確認用途|

**CADファイル・拘束検証は作成済み。交換モータ取付を完了した製造設計ではない。**
公式形状再利用11種類、追加の製造候補はクレードル2種類と継承coupon4種類。直接適合のADAPTER_ONLY認定0、MODIFIED_UPSTREAM0。Envelope2種とREF7種は製造部品ではない。
RevAの既存241成果物hash不変。COM内のユーザー既存dirty documentsを一括閉鎖/破棄せず保存済み新規CADのみ再読込。Inventor全セッションをcold resetした検証とは区別。

1. 公式比較: ../../docs/upstream_alignment_report.md。90/100→116/135mm基準、先端の定義差を明記。公式円筒軸3か所のURDF基準誤差約0.00003..0.00005mm。
2. 固定commit a758567c3978dfeefe282ede0500085a48fe8f78、Apache-2.0出典・変更履歴を保持。
3. 新規モータ配置: pan/shoulder/elbow/wrist flex=VS-S092J、roll/gripper=XL330。case/horn等の未確認寸法は包絡体とHOLDで区別。
4. Follower質量1.180895kg、RevB0.831055kgは全ソリッドCAD。COM/慣性はassembly_mass_reference_validation.json、部品値は各analysis。
5. Follower50g shoulder static1.5461 /motion1.5879Nm、elbow0.8174/0.8438、wrist flex0.2553/0.2658Nm。公称/stallを連続値に使わず駆動適合HOLD。
6. RevB50g shoulder0.6497/0.6553、elbow0.2451/0.2483Nm。固定pan・未搭載遠位軸の加速を除いた保守的動作上界。肩公称以下でも連続適合未確認。
7. 原形とcradleは干渉あり。zero poseのroll envelope–Wrist Roll部品約5170.6mm³。全複合域、ケーブル、ねじ締結空間は未検証。
8. センサ取付CADは継承coupon以外、6軸出力に成立したブラケット未完成。PWM実角度は指令値で代用しない。
9. 非侵襲純正horn方式を優先。Vstone穴/ねじ/軸位置はTBD、XL330メーカーPCD12/4×φ1.6 DP3max/M2 tappingを確認、カスタム結合面はHOLD。
10. 第一印刷候補adapters/stl/Servo_Mount_Coupon.stl。他の3couponは現物合わせ後。荷重支持部品/全フレームはBLOCKED。
11. 追加BOMはadditional_bom.csv、各組立mechanical_bom.csv。モータ追加購入なし、軸受/センサ/基板/電源等は所有・型番・定格を確定後。
12. STM32候補NUCLEO-G474RE、他プロジェクトG474と共通化検討。旧基板流用なし。2rail/保護/E-stop未実装。
13. LeRobot固定版0.6.2でXL330 support確認済み、今回最新版API実行未実施。PWM4軸sensorとcustomRobot必要。
14. offline既存tests: 2joint12件 +初期project8件合格。初回2joint実行はmodule path未設定でimport失敗、PYTHONPATH修正後全件合格。今回CADmesh/DOF/hash整合検査も合格。衝突検査はFAILを維持。
15. JIS様式とfull complianceは別。Default(JIS)実スタイル、日本語PDF、第三角法確認。製作図の全穴位置/深さ/fit/datum/断面等の完成は未完了。

完成条件A/B/C/E/F/H/Iは上記証拠範囲で確認。DはJIS様式図面生成・表示確認まで、製造図の完成はHOLD。Gはmotor配置済み/機械取付適合HOLD。
次に行うべき作業: Vstone純正horn・軸位置・耳/ねじ実測、couponの別指示による印刷/測定、クレードルを公式開口に適合する局所マウントへ修正、slicer/実重量で再負荷計算、sensor/支持/stop完成。今回自動開始しない。
購入・印刷・通電・駆動・EEPROM/ID変更・Leader設計・学習・remote作成/pushなし。
Git: feature/so101-upstream-jis-sixaxis、ローカルcommitのみ。ネイティブCADにはローカル参照があり、そのまま公開しない。第三者モデル入りアセンブリとvendor資料を新規commitから除外。
'''
(M/'release_review/README.md').write_text(readme,encoding='utf-8')
review_fields=['empty_page','view_projection','readable_dimensions','dimension_overlap','page_fit','section_views','title_block','japanese_font','material_part_number','hold_annotations','model_association']
save(M/'release_review/review_status.json',dict(cad_files='COMPLETED_EXISTING_FILES',independent_dof='VERIFIED_2_AND_6',jis_style='VERIFIED',jis_full_compliance='NOT_VERIFIED',manufacturing_drawings='HOLD_INCOMPLETE_DIMENSION_COVERAGE',interference='FAIL',encoder_mounts='TBD',power_on='NOT_PERFORMED',print='NOT_PERFORMED'))
files=[]
for folder in ['two_joint_revb','follower_six_axis','adapters','templates','upstream_reference','release_review']:
    for p in (M/folder).rglob('*'):
        if not p.is_file() or 'OldVersions' in p.parts or 'vendor_local_only' in p.parts or 'SO101 Assembly' in p.parts or p.name in ['Official_SO101_Imported.iam','documents_before.json','XL330_dimension_reference.png','artifact_manifest.json'] or '__pycache__' in p.parts:continue
        files.append(dict(file=str(p.relative_to(M)).replace('\\','/'),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='COMPLETED_FILE; validity per review_status and manufacturing_holds'))
save(M/'release_review/artifact_manifest.json',files)
print('Saved quality review, both BOMs, final report and',len(files),'artifact hashes')
