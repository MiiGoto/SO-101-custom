# 6軸Follower設計レビュー
Confirmed: `SO101_Custom_Follower_RevA.iam`をInventor2026.2で保存・再読込。30 occurrences、81 constraints。Base reference固定、6つの回転軸でそれぞれ並進0/回転1をGetDegreesOfFreedom(out...)で確認し、各軸10°の独立動作とUpdate2成功を記録。
公式リンク・関節配置を維持。製造・組立・駆動を承認するモデルではない。

|軸|motor|50g静的Nm|動作上界Nm|1.25設計目標Nm|
|---|---|---:|---:|---:|
|shoulder_pan|VS-S092J|0.0000|0.0507|0.0634|
|shoulder_lift|VS-S092J|1.5461|1.5879|1.9849|
|elbow_flex|VS-S092J|0.8174|0.8438|1.0548|
|wrist_flex|VS-S092J|0.2553|0.2658|0.3323|
|wrist_roll|XL330-M288-T|0.0120|0.0167|0.0209|
|gripper|XL330-M288-T|0.1844|0.1850|0.2312|

CAD全ソリッド質量 1.180895 kg、COM [126.18283226620419, -5.818503715824641, 148.9068774743736] mm。個別COM/慣性はpart_mass_properties.json。公式形状PET1541 kg/m³、追加クレードル既定材料1000 kg/m³、Vstone42g/XL18g override。実印刷重量ではない。
無負荷の肩static 1.3456 /motion 1.3790 Nm。
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

二関節Rev B: 16 occurrences / 43 constraints、公式ベース＋pan固定、2自由度。質量0.831055kg。50gの肩static/motion 0.6497/0.6553Nm、肘 0.2451/0.2483Nm。基部追加は固定部なので肩/肘負荷を変えない。
重要HOLD: 公式holderとクレードルの重なり、OEMhorn接続、motor軸–case、pan固定、センサ保持、軸受/支持、ねじ締結、材料、熱/連続能力、ストッパ、配線。
今回製造リリースBLOCKED。幾何・拘束・保存済みCADを削除せず、次に干渉しているマウントのみ局所修正する。
