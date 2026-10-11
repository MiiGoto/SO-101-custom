from pathlib import Path
import json,csv,collections,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
parts=read('analysis/mass_properties.json');audit=read('analysis/kinematic_audit.json');torque=read('torque_analysis.json');spring=read('gravity_compensation.json')
references=audit['reference_geometry_checks'];counts=collections.Counter(p['part'] for p in references)
mass={p['part']:p for p in parts}
assembly_mass=sum(r['mass_kg'] for r in references)
assembly_com=[sum(r['mass_kg']*(mass[r['part']]['com_mm'][j]+r['position_mm'][j]) for r in references)/assembly_mass for j in range(3)]
package={'status':'COMPLETED CAD mass extraction; material and hardware COM assumptions apply','inventor':'2026.2','units':{'mass':'kg','COM':'mm','inertia':'kg m^2 about COM'},'parts':parts,'assembly_neutral':{'mass_kg':assembly_mass,'com_mm':assembly_com},'source':'Inventor MassProperties; XYZMomentsOfInertia is COM-centered; motor mass override42g, bearing5g, encoder2g, magnet0.4g are stated assumptions/specifications'}
(ROOT/'mass_properties.json').write_text(json.dumps(package,indent=2),encoding='utf-8')
with (ROOT/'mechanical_bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['part','assembly_quantity','test_print_quantity','material','mass_each_g','role','status'])
    for p in parts:
        name=p['part'];coupon='Coupon' in name or 'Test' in name
        envelope='Envelope' in name;role='hardware envelope, not printed' if envelope else ('coupon' if coupon else ('assembled frame/interface' if counts[name] else 'separate design study'))
        w.writerow([name,counts[name],1 if coupon else 0,p['material'],round(p['mass_kg']*1000,3),role,'COMPLETED native solid; physical fit TBD'])

lines=['# Inventor干渉・拘束検証','', '最終保存IPTの体積と全アセンブリ参照体積が一致した。旧版混入を検出するチェックを含む。', '',
       f'構成部品 {len(references)}個、拘束 {len(audit["final_constraints"])}個。固定Base、肩/肘は同軸mate＋軸方向flush、その他は3平面flushによる剛体接続。', '',
       'ディスクからのcold reloadを実施、32 IDWも再読込みで参照欠落なし。', '', '3平面flushによる剛体29組、固定1個、軸mate/flush2組の拘束構造では独立自由度2。Inventorで肩のみ・肘のみの角度変更が成立することを検証した。GetDegreesOfFreedomの数値取得はCOM出力型変換に失敗したためTBD。数値APIが成功したとは報告しない。', '',
       '| 姿勢 | 肩/肘 deg | Update | solid干渉数 |','|---|---|---|---|']
for p in audit['pose_audit']:lines.append(f'| {p["pose"]} | {p["requested_angles_deg"]} | {p["update_ok"]} | {len(p["interferences"])} |')
lines+=['','全姿勢で91本の本拘束＋一時角度拘束の状態を記録。一時拘束は試験後に削除。保存・再読込み後、参照欠落なし。',
        '', 'この検査は7離散姿勢のCAD solid検査であり、連続全域、ケーブル、コネクタ、製造誤差、実ホーン形状、ねじ、弾性変形を含まない。公差を含む実機干渉検証はTBD。ストッパとばねは個別設計で、実動作検証に含めていない。']
(ROOT/'interference_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

lines=['# 2関節試作 P1 レビュー報告','', 'Confirmed: VS-S092J 10個、XL330-M288-T 2個、軸受0、Adventurer 5M Pro。モータ状態・純正ホーン寸法・ノズル/材料はTBD。', '',
       '肩–肘90 mm、肘–payload100 mm。XY運動平面、Z出力軸。肩0..75°、肘0..120°は設計上のsoft limit。Upper板Z0..5、Forearm板Z33..38。', '',
       f'Inventor 2026.2で{len(parts)}種類のIPT、32構成部品/91拘束のIAMを実際に保存。各部品は1 solid body。STEP/STLを出力し、ファイル生成状況はartifact_manifest.jsonで確認できる。', '',
       '支持キャリア2個、625座、リテーナ、補助軸/フランジ、磁石キャリア、4 mmセンサ柱をIAMに配置。金属軸・軸受・センサ基板・磁石は仕様/質量仮定を記録した包絡体。純正ホーン接続、実基板固定、支持足の締結、公差/強度は未承認。', '',
       '| CAD部品 | kg | COM mm | Izz kg m² |','|---|---:|---|---:|']
for name in ('Upper_Arm','Elbow_Mount','Elbow_Support_Carrier','Forearm','Payload_Mount'):
    p=mass[name];lines.append(f'| {name} | {p["mass_kg"]:.6f} | {[round(v,3) for v in p["com_mm"]]} | {p["inertia_kg_m2"][2]:.8g} |')
lines+=['',f'中立アセンブリCAD質量 {assembly_mass:.6f} kg、COM {[round(v,3) for v in assembly_com]} mm。全ソリッドPETライブラリ（約1541 kg/m³）を使用。これは実印刷質量ではない。', '',
        '## 重力・動作トルク', '', 'G_i=Σ m g ∂y_COM/∂q_i。M=Σ(m JvᵀJv + Izz JωᵀJω)、CはMの姿勢微分から計算。必要トルクの三角不等式上界を|G|+|M||α|+|C|で評価。速度各0.1 rad/s、加速度各0.2 rad/s²。摩擦・配線抵抗・熱・弾性・衝突は含まない。', '',
        '| payload g | 肩static Nm | 肘static Nm | 肩motion bound Nm | 肘motion bound Nm |','|---:|---:|---:|---:|---:|']
for c in torque['cases']:lines.append(f'| {c["payload_g"]:.0f} | {c["max_static_Nm"][0]:.4f} | {c["max_static_Nm"][1]:.4f} | {c["max_motion_bound_Nm"][0]:.4f} | {c["max_motion_bound_Nm"][1]:.4f} |')
lines+=['','最悪値は肩1°/肘2°刻みの設計範囲探索。離散格子外の厳密な最大値ではない。肘側サーボ42 g、支持キャリア、センサ・軸受、先端マウント、追加ねじ各6 g仮定を含む。サーボ内部COM/慣性とねじ分布はTBD。',
        '', '以前の0.614/0.782、0.339/0.456 Nmは6軸派生の遠位モータ/グリッパを含む別負荷モデル。今回は2軸のみと低速条件であり、同条件の性能改善値として比較しない。',
        '', '9.2 kgf cm=0.9022 Nmは公称トルク、連続定格ではない。両軸の連続適合はTBD。payload上限は可用連続トルクと温度・電流・ギヤ・支持荷重を測定してから決定する。追加payload1 gの伸展時増分は肩0.001863、肘0.000981 Nm。肘サーボCOM誤差±10 mm各方向の重力モーメント不確かさは最大約0.0058 Nm。',
        '', '## 肩の重力補償比較', '', '| 案 | 特性・補償 | 質量/空間 | 破損・難度 |','|---|---|---|---|',
        '| 軽量化 | すべての姿勢で重力/慣性を低下。実印刷重量測定が必要 | 最小 | 剛性/クリープを確認、容易 |',
        '| 引張ばね | 以下の固定/移動点で可変モーメント | 後方Z=-40 mm面に約81 mm長の空間、ばね重量TBD | 破断時に落下、フック/固定部の強度試験必要 |',
        '| ねじりばね | kθ(θ0−θ)、cos重力を完全には追従しない。任意姿勢の肘依存は補償しない | 関節周囲、軸受/encoderと競合 | 破断/外れ/巻方向の確認、難度中 |',
        '| カウンターウェイト | 後方重りで概ねcos肩を補償。肘角の負荷変化は残る | 50 g caseの最大肩重力を0.1 m後方で相殺する質量は下記式、慣性増加 | 脱落危険、機械固定必要 |',
        '| モータ変更 | メーカー連続特性に基づく選定が可能 | マウント/電源変更、追加費TBD | 選定/再設計必要 |', '',
        f'50 g case最大staticを100 mm後方で相殺する参考重り: {torque["cases"][2]["max_static_Nm"][0]/(.1*9.80665)*1000:.1f} g。これは全姿勢に最適な重りではない。', '',
        f'引張ばね暫定: 固定(-35,40,-40) mm、リンク側(35,0,-40) mm。有効k={spring["effective_spring_k_N_m"]} N/m、等価無張力長{spring["equivalent_zero_force_length_mm"]:.1f} mm、必要長さ{spring["length_range_mm"][0]:.1f}..{spring["length_range_mm"][1]:.1f} mm、力{spring["force_range_N"][0]:.2f}..{spring["force_range_N"][1]:.2f} N、幾何ストローク{spring["length_range_mm"][1]-spring["length_range_mm"][0]:.1f} mm。50 gモデル格子の最大残留肩トルク{spring["worst_residual_shoulder_Nm"]:.4f} Nm。',
        '', '実ばね自由長Lfreeを選ぶ場合、初期張力Fi=k(Lfree−L0)としてフック間長・端末コンプライアンスを含める。自由長は最短要求長44.5 mm以下（公差余白も必要）にする。例Lfree=44 mmならFi=k(44−43)/1000=0.28 N、最長側の自由長からの伸びは36.6 mm。負のFiや最短距離より長い自由長は、この引張ばねモデルに不適合。初期張力をストローク端でゼロと仮定していない。二つのAnchor.iptの眼穴を具体化したが、ベース/リンクへの延長支持、ばね実形状、疲労・取付強度は未完。未選定ばねで連続能力が解決したと扱わない。', '',
        '## 次に確認する事項と停止点', '', '最初の印刷候補はServo_Mount_Coupon 1個。次に純正ホーン寸法測定→Horn_Adapter_Testの接続面を確定、センサ/磁石基板の実寸→alignment fixtureの最終積層、軸受/補助軸保持と固定足のねじ→フレーム製作レビュー。現物寸法確認でリンク長やcase positionを変更したらmass/torque/干渉を再計算する。', '',
        'A: 寸法確認用coupon STL生成済み。B: 全フレーム印刷はfit/締結/ストッパ/強度HOLD。C: 組立HOLD。D: 通電HOLD。印刷、購入、実機I/O、EEPROM変更、次Task自動開始は実施しない。', '',
        'Leader/Follower数量と操作性はadditional_bom.md。電源/基板はelectrical_interface.md。Pythonは7件の制御unittestと5件の解析成果物チェックを実行、実機通信を持たない。Gitはfeature/so101-two-joint-prototypeのローカルcommitのみ。']
(ROOT/'review_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
manifest=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and 'OldVersions' not in p.parts and '__pycache__' not in p.parts and p.name!='artifact_manifest.json':
        manifest.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'COMPLETED FILE; manufacturing validity per review_report'})
(ROOT/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Review, mass package, actual BOM, interference report and artifact manifest saved.')
