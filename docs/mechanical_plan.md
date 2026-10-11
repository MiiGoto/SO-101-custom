# Inventorカスタム設計計画

公式assembly STEPを参照componentとして保持し、別のカスタムassemblyを作る。既存別プロジェクトと公式原本は変更しない。
Inventor 2026.2の起動画面は確認。カスタムipt/iamは未作成、全関節干渉・encoder mountの成立はTBD。

| 部品/単位 | 数の初期候補 | 改造内容 | 決定に必要な寸法 |
|---|---:|---|---|
| base / pan holder | 1組 | Vstone支持、机への固定、反対軸/encoder、配線 | 外形/ねじpitch/horn/軸の中心 |
| shoulder clevis | 1 | Vstone lift、両持ち支持、encoder space、落下受け | ケースねじ深さ/反対軸/取付高さ |
| upper link | 1 | L1可変、elbow Vstone mount、ケーブル | L1、断面、ねじ、リブ |
| forearm link + wrist holder | 1組 | L2可変、wrist flex Vstone | L2、motor固定面、重心 |
| wrist pitch/roll carrier | 1組 | XL330小型mount/軸のoffset | hornとhousing、ケーブル出口 |
| fixed jaw / moving jaw | 各1 | XL330 gripper、把持lever/力/開口 | contact radius、jaw sweep、horn |
| encoder fixed carrier / magnet carrier | 各4 | 無分解・output軸位置検出 | module実寸、磁石/中心ねじclearance |
| axis support / spacer / bearing housing | 4軸分候補 | motor出力軸への曲げ集中を抑制 | bearing/ブッシュ在庫/軸径 |
| control/power bracket | 1 | STM32、rail分離、E-stop、connector | 実物基板/端子定格/アクセス |
| test coupons | motor各1種+sensor1組 | 最初の取付確認 | すきま系列、穴実測 |

穴pitch、shaft/hornスプライン、ねじ種別/長さ/有効深さはUNKNOWN。motor図面/現物に合わせて個別parameterにし、全体scaleで穴合わせしない。
標準motorが使える部位は公式部品を再利用できるが、今回確認済み在庫にSTS3215はない。baseの机固定やjaw等も取付互換を確認してから再利用判定。
parameters.csvは設計開始用の長さ・範囲・状態表。製作図面ではない。
可動域確認：joint sweep→隣接リンク/軸受/机/配線の交差→最接近clearance→組立アクセス。collision-freeを確認するまでは計算上の最悪姿勢を実機で再現しない。
剛性/クリープ/層間強度、servo shaftラジアル荷重、horn抜け、熱を検証。幾何クリアランスだけで強度・実機成立と判定しない。
