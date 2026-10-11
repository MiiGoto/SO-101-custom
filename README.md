> 2026-10-11 公式継承/JIS改訂：独自90/100 mm Rev Aを保持し、公式116/135 mm基準のRev Bと6軸Followerを別フォルダに保存。現行の成果・製造HOLDは [release_review](mechanical/release_review/README.md)、[公式比較](docs/upstream_alignment_report.md)、[6軸レビュー](docs/six_axis_design_review.md)、[図面レビュー](docs/drawing_quality_review.md)。以降の旧計画本文は履歴。
> 2026-10-11 P1追補: 現物型番VS-S092Jと10個、XL3302個、Adventurer 5M Pro、軸受未所有を確認。今回の新規指示により肩/肘90/100 mmの実Inventor CADを作成した。最新成果は[2関節試作](mechanical/two_joint_prototype/README.md)と[レビュー](mechanical/two_joint_prototype/review_report.md)。以下は保存した初期計画で、在庫UNKNOWNと「commitなし」の記述は初期報告時の状態。現時点はローカルfeature branchとcommitあり、購入/印刷/通電/pushなし。

# 手持ちモータで作るSO-101派生Follower：計画報告

2026-10-11 JST。**推薦はHybridの専用リンク再設計Cを、肩・肘2関節の短リンク試作Dから検証すること。6軸の成立は未確定。**
今回は調査・在庫整理・初期計算・ロードマップを作成して停止。購入、発注、印刷、通電、駆動、EEPROM/ID変更、実機校正は実施していない。新規GitHub remote/公開/commitも行っていない。

## 1. SO-101公式仕様（Confirmed）

5 arm joints+gripper、6 actuators。FollowerはSTS3215 1/345×6、Leaderは191/345/191/147/147/147で別構成。STL/STEP、URDF/MJCF、LeRobot対応あり。SO100/Miniと混同しない。
公式資料、電源/通信/組立/校正/カメラ/模倣学習/ライセンスは[official_reference](docs/official_reference.md)。
Hardware commit `a758567c3978dfeefe282ede0500085a48fe8f78`、LeRobot commit `b9cb121cb7d4e3e26ec5c906d08dda68d151ba52`、取得mainのversion0.6.2。公開Webドキュメントとmainの差を記録。

## 2–3. Inventoryと未確認事項

[inventory.csv](inventory/inventory.csv)：指定15列。
Confirmed：Vstone「VS-SO92J」大量所有、XL330-M288-T 2個、使用可能な個人3Dプリンタ。
TBD：Vstone VS-S092Jとの同一性（O/0）、正確な数量/状態、printer機種/bed/nozzle/material、motor horns/cables、電源/controller/camera/締結部品。
Vstone公式候補仕様は確認できたが、現物へ確定適用しない。詳細は[questions](docs/questions.md)。

## 4–5. 比較と推奨

[motor_compatibility](docs/motor_compatibility.md)：Standard/全Dynamixel/Hybridの費用予算・改造・工数・LeRobot・拡張・リスク比較。
手持ち2個のXL330だけでは6軸Dynamixel構成にならない。Hybrid候補は手持ちmotor6/6を活用できるが4台のVstone型番/状態が前提。
寸法比較A（標準幾何）、B（80/85/90%関節offset）、C（90/100 mm専用リンク）、D（50/60 mm肩/肘試作）。Bの単純小型化だけでは肩負荷を解消できない。

## 6. 全軸割当と負荷

Vstone：pan/lift/elbow/wrist flex、XL330：wrist roll/gripper。
全6軸の範囲・静的/動的負荷・最悪候補姿勢を[torque_report](docs/torque_report.md)、[126行CSV](docs/torque_results.csv)、[仮定入力](docs/torque_inputs.json)へ保存。
Assumption：50 g把持時Cの肩静的上界0.614 Nm、動作上界0.782 Nm、1.25倍設計目標0.977 Nm。Vstone公称0.902 Nmを連続値として使っていない。肩能力が大きなブロック。
公式URDF由来geometryに仮定mass/COMを入れた初期screeningで、実CAD/実測による適合保証ではない。

## 7. 電源/通信

[architecture](docs/architecture.md)：PC→USB composite CDC→STM32、PWM4ch+output encoder4軸、half-duplex TTL→XL330×2。
Vstone7.4 V候補とXL3305 V railは分離、GND基準は適切に共通化。モータ電流をPC USBへ流さない。fuse/過電流/逆接/緊急遮断と落下受けを計画。
DXL5 V stall電流予算2.94 A/2個、Vstoneピーク電流TBD。電源/線/fuse確定には実測が必要。

## 8–9. 公式CADとカスタムCAD

公式SO101 assembly/upper/under STEPとURDFを保存しSHA256記録。[mechanical_plan](docs/mechanical_plan.md)に必要なmotor mount、支持軸、専用リンク、jaw、encoder/magnet holder、電装部品を一覧化。
Inventor2026.2の起動確認を行った。カスタムipt/iam設計、encoderの関節軸への取付、全可動域干渉は**未完了**。現物寸法と選ぶsensor moduleが必要。パラメータ表は製造図面ではない。
AS5600等の[feedback比較](docs/feedback.md)を作成。4 PWM軸は指令角と実角を区別し、非侵襲output角観測を候補にする。未検証なので選定/購入確定しない。

## 10. 3Dプリント計画

[printing_plan](docs/printing_plan.md)：PLA+/0.4 mm/0.2 mm/15%を公式初期候補、PETG比較、部品数/向き/support/公差/組立順を記載。filament g/印刷時間はCADとslicer未確定のためTBD。

## 11–12. 最小BOMと追加購入

[bom](docs/bom.md)：D用2位置sensorから、6軸用4sensor、磁石、STM32、TTL interface、2rail電源、E-stop/fuse/connector/支持部品。不足かどうかは在庫確認後。
追加motor購入は保留。手持ちで進められる調査/計測/設計/mockを優先。予算枠はAssumptionで実売見積ではない。

## 13. LeRobot方針

[lerobot_plan](docs/lerobot_plan.md)：xl330-m288対応を固定ソースで確認、DynamixelMotorsBus優先、Vstoneは独自PWM+external feedbackをcustom Robotへ統合。
全6軸共通position read/writeとhost校正、teleoperate/record/replay/inferenceの接続方針を定義。実装済みはoffline契約試作品のみ、LeRobot自体の実行/実機統合は未実施。
単一の独自UARTフレームでは既存DXL busがそのまま使えないため、raw DXL専用CDCまたは独立USB adapterを選ぶ。

## 14. Simulation方針

[simulation_plan](docs/simulation_plan.md)：公式モデルを基準にcustom FK/IK/limits/collision/controllerへ段階更新。現状はFKと初期重力/慣性screening。mesh表示・IK・干渉・追従は未検証。
公式READMEにはbase collision除去とgripper0–100 mapping未反映の注意があり、そのまま全衝突/把持モデルと扱わない。

## 15. Task 1–12

[roadmap](docs/roadmap.md)：各Taskにobjective/prerequisites/deliverables/acceptance criteria/effort/blocked items。
Followerを先に作り、LeaderはT10以降。現在は現物未確認なのでTask1も一部未完了。次Task自動開始なし。

## 16–17. 最初の印刷と実験

印刷候補はVstone取付coupon、次にXL330/encoder holder coupon。現物寸法確定までは印刷しない。
最初の機能は未通電手動回転と実角度readout。将来の短リンクD（shoulder lift+elbow flex）は無payload・低速から温度/電流/追従誤差を記録。homeは安全経路を確認してから。

## 18. 確認事項と検証範囲

確認すべき項目は[questions](docs/questions.md)。最優先はVstoneのラベル/数/状態/horn、printer/電源/STM32、把持物/必要reach。
オフライン8テスト合格：指令が観測を上書きしない、stale/invalid/disconnectで拒否、無効指令のatomic拒否、欠測軸捏造なし、重力=位置エネルギー勾配、半径上界、zero mass、単位変換。
熱・連続保持・停電・backlash・強度・実機通信・Inventor interferenceは未検証。[validation](docs/validation.md)参照。

ロードマップ作成の成果を報告して停止する。次Task、automation、製造、通電を開始しない。
