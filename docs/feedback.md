# 実位置フィードバック

| 方式 | 長所 | 制約/結論 |
|---|---|---|
| AS5600外付け | 12 bit absolute、非接触、I2C/analog/PWM、比較的簡単 | 同軸の径方向着磁磁石、位置/磁界/配線の検証。候補留保 |
| AS5048A等SPI絶対角 | 14 bit、軸ごとのCS、診断/parity | 配線と実装、磁石/温度/精度TBD。高bit数だけで高実精度とは判定しない |
| 外付け回転pot / 光学絶対encoder | 磁気影響回避、potならADC可 | potは摩耗/トルク/範囲、光学は大きさ/価格。関節output側へ接続 |
| サーボ内部位置検出利用 | 内部には位置閉ループの検出機構がある可能性 | 外部取得API未確認。分解/tapは侵襲的で未許可。採用しない |
| 一部smart servo置換 | 実位置・電流・温度をbus取得 | 新規購入/マウント、連続負荷とrail再評価。肩だけ交換候補は残す |

根拠：[AS5600公式datasheet](https://look.ams-osram.com/m/7059eac7531a86fd/original/AS5600-DS000365.pdf)、[AS5048公式datasheet](https://look.ams-osram.com/m/287d7ad97d1ca22e/original/AS5048-DS000298.pdf)。公開検索で仕様確認。PDF直接保存はAsset restrictedで未取得。
AS5600 4096 count/turn = 0.08789°/countは量子化幅であって取付後の精度ではない。磁石偏心、傾き、磁界強度、機械ガタと遅延を含めて評価。
AS5600固定I2C address 0x36の4台を直結しない。候補は4独立bus、またはI2C mux（型番/在庫TBD）。raw angleとmagnet detect/weak/strongを監視。OTP zero/range設定は不要、software校正を保存しOTP書込みしない。
配線が長くなる場合は軸近くで取得して差動/堅牢通信にする案を再評価。PWM outputをタイマ入力captureにする案もmux回避候補。

## Inventor実装確認ゲート（現在TBD）

固定側：sensor boardを関節軸受支持体へ固定。回転側：関節outputの反対軸/別体軸に同軸磁石carrier。サーボケースに穴あけしない。
horn中心ねじ、金属軸、反対軸ブッシュ、ケースねじの干渉を測る。中心が使えなければ独立軸+非侵襲連結を設計し、伝達ガタも評価。
Inventorパラメータ：board W/H/T、chip active plane、magnet D/H、air gap min/max、eccentricity、bearing/shaft D、horn sweep、cable bend radius。選ぶモジュールにより寸法が違うので未知値で凍結できない。
air gapは資料と選定磁石の磁界条件から設定。仮の0.5–2.5 mm空間を検討範囲にするが、磁界強度/diagnosticsによる確認なしに適合判定しない。
受入：全角度でsensor/magnet/ねじ/ケーブル非接触、磁石保持、軸の共線性、調整可能なgap、組立と交換アクセス、magnet status正常、真角との誤差目標を満たす。
今回は公式STEPの利用確認を試みたが、手持ちmotor/hornの現物寸法とsensor module外形が未確定。カスタムmountのInventor実装検証・干渉試験は未完了。AS5600を選定確定せず、購入BOMも条件付きとする。
