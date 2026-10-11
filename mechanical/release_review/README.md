# 公式SO-101継承/JIS・成果と製造レビュー
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
