# 検証記録：2026-10-11 JST

Confirmed：simulation/torque_envelope.pyをbundled Python + numpyで実行。公式SO101 URDFを読込み、7案×3payload×6joint=126行の計算を生成。
Confirmed：`python -m unittest discover -s tests -v` 8 tests / OK。
機械計算の独立照合：重力と位置エネルギー微分が7桁で一致、1000姿勢×7案で半径上界以内、無mass時zero gravity、kgf cm→Nm変換。
software契約：指令と観測分離、stale/invalid/disconnected拒否、NaN/Inf/範囲外writeをatomic拒否、6軸欠測を捏造しない。
未検証：実motor/実sensor、STM32 firmware、LeRobot import/統合実行、各rail回路、連続定格/熱、gear/backlash、停電保持、CAD interference/strength、造形精度、模倣学習。
Inventor：2026.2起動画面確認、公式STEP選択操作を試みたがUI操作でtimeoutがあり、STEPの正常import結果とcustom mountの確認は得ていない。成功と報告しない。
ネットワーク制限下の通常shell取得は失敗、許可された公開資料取得でcommit/STEP/URDF/APIを保存。encoder PDF直接取得はAsset restricted、公開一次datasheet検索結果のみ参照。
公式ファイルは参照copy、LICENSE保持、SHA256はsource_manifest.csv。既存プロジェクトのファイルは未変更。
今回購入/発注/全印刷/個別印刷/通電/駆動/EEPROM-ID変更/実機校正/GitHub公開/automationは実施なし。
