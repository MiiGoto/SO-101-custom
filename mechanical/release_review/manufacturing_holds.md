# 製造HOLD / 2026-10-11

| 項目 | 状態 | 解除に必要な証拠 |
|---|---|---|
| 公式形状を保持したRev B / 6軸IAM | CAD保存済み | 物理成立の保証とは区別 |
| Vstoneケースと出力軸の相対位置 | HOLD | 分解せず現物寸法を測定 |
| Vstone純正horn・耳・ねじ | HOLD | 実寸・穴配置・深さ・horn所有を確認 |
| XL330機械結合 | HOLD | 公式PCD12/4穴/M2 depthと現物horn、公式jaw側接口を照合 |
| 原形holder + 新cradle | BLOCKED | native interferenceで衝突あり。局所マウント変更・再干渉検証 |
| Follower肩駆動 | BLOCKED under full-solid model | CAD全ソリッド+50gは1.55Nm。slicer/実測重量、連続能力、補助機構を再評価 |
| 二関節肩駆動 | HOLD | full-solid+50g 0.65Nmは公称以下でも連続適合未確認 |
| センサ配置 | HOLD | output4軸の実基板・磁石・gap・固定・配線CADを完成 |
| bearing/shaft/stop/pan固定 | HOLD | 寸法、保持、許容荷重、全域ストッパ、固定ねじを確定 |
| 全域可動性 | NOT VERIFIED | 独立CAD動作のみ成立。全複合域/連続掃引/ケーブルを検査 |
| 製作図面完全性 | HOLD | 残る穴位置・深さ・datum・fit・ねじ・材料・断面を確認 |
| FDM公差/重量/強度 | HOLD | couponを別指示で印刷、Adventurer5MPro設定と材料を記録して測定 |
| 電源・実機駆動 | HOLD | 電流/保護/落下受け/E-stop/配線を先に検証 |

寸法確認用coupon4種のSTLは閉じたメッシュとして利用できる。構造部品として荷重を載せる承認ではない。最初はServo_Mount_Coupon。実印刷/G-code生成/通電は今回行っていない。

6軸CADを破棄したり全リンクを縮小したりせず、必要箇所の計測→取り付け局所修正→再解析に進む。次タスクは自動開始しない。
