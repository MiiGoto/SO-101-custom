# Task 1–12：Follower優先、次Task自動開始なし

全時間は実作業時間のAssumption、調達/ユーザー確認待ちを除く。実機操作は今回の許可に含まれず、この表は将来の計画。

| Task | objective | prerequisites | deliverables | acceptance criteria | effort | blocked items |
|---|---|---|---|---|---|---|
| 1 在庫・型番・電源・通信 | 現物の正確な仕様を確定 | ラベル/図面/所有機器へアクセス | inventory、写真/寸法/状態記録、電源定格 | 型番O/0一致、4台候補健全、XL2個、電源/connector/boardを記録 | 3–6 h | 現物、正確数、printer/PSU/STM32 |
| 2 構成・不足BOM | C+D/対照Standardから選ぶ | Task1、要求payload/reach | 決定記録、BOM、負荷予算 | 連続能力根拠または単体評価計画、予算、全6軸観測計画 | 3–6 h | 連続トルク/電流/予算/必要reach |
| 3 CAD適合・custom部品 | 非侵襲mountとoutput sensor成立 | T1寸法、T2候補 | Inventor parametric ipt/iam、図面、mass/COM、range report | holes/horn/ねじ/ケーブル/磁石gap確認、全range干渉、強度仮定記録 | 12–24 h | 実寸・sensor外形・shaft/bearing |
| 4 印刷test・組立準備 | couponから適合と材料を確認 | T3、printer profile、別の印刷指示 | coupon結果、slicer g/時間、短リンクD | 実ネジ着座、精度/変形/剛性、軸位置再現、重量更新 | 4–8 h +造形時間 | printer/材料/実寸、印刷未許可 |
| 5 単体通信・低速 | 1台ずつ安全に電源・観測・駆動 | 電源/保護、固定/落下受け、別の実機指示 | 電流温度/角度/遅延log、usable load envelope | 保護/非常停止、read/command区別、範囲/追従、heat試験、ID変更は別承認 | 6–12 h | Vstone電流・熱、実機未許可 |
| 6 Follower組立 | D肩/肘→追加軸→C全体 | T3–5、各軸受入 | 組立記録、段階可動/電流log | 無負荷→限定payload、温度/電流/誤差/干渉/停止条件内 | 8–16 h | shoulder連続能力、全部品 |
| 7 関節calibration | 実joint zero/sign/range統合 | T6、安全手動range | host calibration JSON、単位/符号/再取付結果 | 6軸実位置、校正再現、limit余白、EEPROM自動変更なし | 3–6 h | encoder実装、range |
| 8 LeRobot統合 | custom Robot +既存DXL bus | T7、版固定、transport | installable plugin、integration log | 6*.pos読書、stale/断線fault、SDK透過、mock/実機境界明示 | 10–20 h | composite CDC/firmware、LeRobot実行環境 |
| 9 PC操作・camera・record | Leaderなしでデータ記録 | T8、操作enable、UVC inventory | GUI/keyboard、動画/state/action/time dataset | 低速jog/home、画像同期、実位置欠測を捏造しない、offline replay照合 | 6–12 h | camera/FPS/同期、操作選択 |
| 10 Leader/代替操作 | 操作性を改善 | T9、必要性評価、予算 | gamepad等またはLeader設計 | 操作範囲/符号一致、非常停止、手動操作の負荷/安全 | 4–12 h代替 / 16–32 h Leader | Leader用motor未確定 |
| 11 模倣学習 | 記録→policy→安全評価 | T9/10、品質dataset、計算資源 | dataset split、training/eval記録 | 実位置/画像/指令metadata一致、offline評価、別実機gate | 12–24 h +学習時間 | data/camera、compute/評価条件 |
| 12 独自機能 | task要件に沿う追加機能 | T11と新規目的 | 要求/設計/試験結果 | 明示した用途の指標で受入、負荷/安全再検証 | TBD | 用途未定 |

今回：Task1の資料/申告在庫整理と、Task2以降の計画・初期成立性計算まで。Task1の現物確認も未完了。Task2以降を実行済みとは扱わない。

## 最初の2関節試作（将来の具体計画）

基部panを固定し、Vstone2台でshoulder_lift + elbow_flex、50/60 mm短リンク、wrist/gripperなし。重い遠位モータを省いてgravity機能を検証。取り付けcouponは先に確認。
外部encoder2軸、STM32、保護付きVstone電源、受け台、独立非常停止を用意。XL330単体通信は別の5 V経路で並行計画できるが今回は実行しない。
最初の機能は「未通電手動回転に対する実joint angle読出し」の検証。その後に将来許可された単体電源/通信試験と低速位置追従へ進む。
当初は無payload、速度0.1 rad/s・加速度0.2 rad/s²から開始（Assumption）。指令階段ではなくslew-limited trajectory。片軸ずつ±10°範囲から拡張。
測定：q_cmd/q_actual、電圧、電流ピーク/平均、surface/internal温度、timestamp、tracking error、方向反転誤差。PWM角パルス対応を低力/非終端の範囲で確定する。
温度・電流・持続時間の絶対許容値はメーカー/個体条件から先に設定する。未知のまま30分保持やstall試験をしない。熱平衡未到達の短試験から連続定格を断定しない。
受入目標：sensor誤差<=1°、校正繰返し<=0.5°、追従<=2°（初期Assumption）、範囲外指令拒否、センサ断線/PC停止/E-stop時のfault/落下受けを確認。必要保持トルクに1.25余裕を持ち、熱/電流/gearの証拠で合格判定。
停止条件：異常電流/温度/音、角度逸脱、magnet status異常、更新欠損、配線接触、固定緩み。原因修正と再評価まで拡張しない。

## 今回の停止

ロードマップと報告が完了したら停止。automation/heartbeatを作らず、Task2/製造/通電/EEPROM変更を自動開始しない。

## 2026-10-11 新規指示によるP1実施

最初の2関節試作を90/100 mmで詳細化。旧Dの50/60 mmは保存した初期対照案であり、P1では採用しない。Task3相当の実CAD/取付候補、Task4のcouponデータ、Task8/9へつなぐoffline運動学を作成。Task4の印刷、Task5以降の通電/駆動、Leader CADは未着手。各既存Taskの現物確認条件は維持。[レビュー](../mechanical/two_joint_prototype/review_report.md)のHOLD条件を解除してから製作を判断する。今回の終了後停止。

## 公式継承/JIS改訂の現状
別フォルダでRevBと6軸Followerの実CAD・JIS図面を作成。Task3相当の機構モデルと製作準備は進めたが、マウント干渉/ホーン/全域可動性/製作図全寸法/連続能力はHOLD。次は現物寸法とcoupon測定、局所マウント修正。Task4の印刷とTask5の通電を自動開始しない。最新状態はmechanical/release_review/README.md。
