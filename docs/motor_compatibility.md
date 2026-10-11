# モータ・構成比較

## 確認状態

Confirmed：公式[Vstone VS-S092J](https://www.vstone.co.jp/robotshop/index.php?main_page=product_info&products_id=299)はPWM、4–9 V、7.4 V測定の公称9.2 kgf cm（0.9022 Nm）、約42 g、最大180°、0.11 s/60°、19×38×38.5 mm。公式販売終了品。デジタル実位置取得APIは記載なし。
TBD：ユーザー申告VS-SO92Jと公式VS-S092Jが同一か。数量は「大量」から整数を推定しない。ケース/ラベル・寸法・ケーブル・ホーン照合が必要。
Confirmed：XL330-M288-Tを2個所有、[ROBOTIS公式](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/)の推奨5 V、18 g、0.52 Nm stall、288.4:1、4096 count/rev、TTL Protocol 2.0。熱保護機能があることは連続許容トルクの保証にならない。
TBD：どちらも連続トルク、実機の劣化、バックラッシュ、保持の熱、停電時落下/逆駆動。公称/ stallを連続値として比較していない。

## Standard / Dynamixel / Hybrid

| 構成 | 手持ちモータ利用 | 追加購入 | 機械/制御工数 | LeRobot/拡張 | リスク | 目安工数* |
|---|---|---|---|---|---|---|
| Standard STS3215 | 確認済み在庫で0/6 | STS3215×6+adapter+電源等（在庫TBD） | 低/低 | 公式対応が最も容易 | 組立精度・電源・熱 | 24–48 h |
| all Dynamixel | XL330×2/6 | 適正モータ4台以上・mount等 | 高/中 | 既存bus活用、custom Robot | 2個で6軸不可、肩用モータ能力未選定 | 50–100 h |
| Hybrid Vstone×4+XL330×2 | 6/6候補。4台の型番・状態確認が前提 | 4実位置sensor+電源/保護/interface等 | 高/高 | custom Robot、将来smart化可能 | 肩熱・狭い範囲・観測/同期 | 70–140 h |

*設計/調達待ち除くAssumption。追加購入費はbom.mdの予算枠であり見積価格ではない。
手持ちを最大限活用する学習目的にはHybridを優先検討。公式設計の短期間完成を最重視する場合の対照案はStandard。

## 6軸割当候補

| 軸 | 候補 | 実位置 | 仮のソフト範囲（校正後rad中心を定義） | 判定 |
|---|---|---|---|---|
| shoulder_pan | Vstone | 外部encoder | ±80° | gravity≈0だが慣性・軸受・取付傾きTBD |
| shoulder_lift | Vstone | 外部encoder | ±80° | 最優先の成立性ブロック。釣合い/短縮/別motor候補 |
| elbow_flex | Vstone | 外部encoder | ±80° | 肩より軽いが連続保持TBD |
| wrist_flex | Vstone | 外部encoder | ±80° | 手首遠位質量を小さく、成立TBD |
| wrist_roll | XL330 #1 | Present_Position | ±90° | ケーブル捻り・偏心把持で確認 |
| gripper | XL330 #2 | Present_Position | 0–60° | 力制限とjaw geometry、連続把持TBD |

XL330を肩へ置くと公称stallもVstoneより小さく、今回の肩負荷を解消しない。XL330をwrist flexへ移す代案は遠位Vstoneが増えて肩負荷が増えるため再計算が必要。
Vstone180°は公式上限。実機のusable range、中心PWM、取り付け方向、機械ストッパを測定するまで±80°も許可済み可動域ではない。
公式URDF範囲pan±110°、lift±100°、elbow±96.83°、wrist flex±95°、roll約−157.21～162.79°、gripper−10～100°をそのままPWM180°機に適用できない。

## 寸法案A–D

| 案 | L上腕/L前腕/手首軸間/tool offset (mm) | 位置付け |
|---|---|---|
| A 標準幾何+手持ちmotor | 116/135/63.7/98.45 | 質量置換の仮定モデル。標準部品への物理装着は未成立 |
| B 80–90% | 92.8–104.4/108–121.5/51.0–57.3/78.8–88.6 | 比較用関節/COMパラメータ。モータ/穴を縮尺変更しない。固定外形・ケーブル空間が支配する |
| C 専用再設計 | 90/100/45/70 | 推奨評価開始値、製作確定値ではない |
| D 肩lift+肘flex | 50/60、手首/グリッパなし | 最初の実験候補。無把持物から段階試験 |

全体リーチはFKと関節制限で決定。小型化率は80/85/90%の比較仮定であり目標仕様ではない。支持軸・motor周りのclearanceを残すと単純体積s³では軽くならない。
最小Cを自動採用せず、肩連続能力・必要リーチ・把持物・干渉でPareto比較する。肩を釣合いばねで補助する場合はばねトルクの姿勢依存性と機械故障時も再計算。

計算、最悪姿勢、仮定、全6軸動的値はtorque_report.md / torque_results.csv。連続許容がUNKNOWNなので全軸の最終適合判定はTBD。
