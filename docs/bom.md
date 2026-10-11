# 最小追加購入BOM（条件付き、購入しない）

在庫UNKNOWNを即購入必要と判定しない。単価と費用は未見積。以下の予算は計画用Assumptionで、実売価格/送料/税/供給状況を調査した見積ではない。

| item | D 2軸段階の必要数 | Hybrid 6軸総数 | 手持ち/購入判定 | 決定ゲート |
|---|---:|---:|---|---|
| VS-S092J候補 | 2 | 4 | 大量所有、数/型番/状態TBD、新規購入予定なし | labelと寸法 |
| XL330-M288-T | 0（単体試験は1） | 2 | 2所有Confirmed、新規購入不要候補 | 状態/horn |
| absolute angle sensor | 2 | 4 | 在庫UNKNOWN、なければ追加必要 | Inventor取付確認 |
| 径方向着磁磁石+carrier | 2 | 4 | 在庫UNKNOWN | sensor/金属軸影響 |
| I2C mux等 | 0–1 | 0–1 | boardで4bus使えれば不要 | AS5600 bus案確定 |
| STM32 USB対応board | 1 | 1 | 在庫UNKNOWN、追加購入条件付き | GPIO/timer/USB resources |
| half-duplex TTL buffer/interface | 単体XL試験時1 | 1 | 在庫UNKNOWN、必要 | direction/level/echo |
| regulated 7.4 V supply | 1 | 1 | 在庫UNKNOWN、必要 | Vstoneピーク電流測定 |
| regulated 5 V supply | XL試験時1 | 1 | 在庫UNKNOWN、必要 | >=2.94 A+margin候補 |
| E-stop +両rail遮断部 | 1組 | 1組 | 在庫UNKNOWN、必要 | 定格/落下受け |
| fuses/holders/protection/distribution | 1組 | 1組 | 在庫UNKNOWN、必要 | 電流・線・時間特性 |
| 正規motor cable/connector/buffer wiring | 1組 | 1組 | 在庫UNKNOWN | pinout/定格 |
| horns/screws/inserts/spacers | 2軸分 | 6軸分 | 所有TBD、不足のみ | 実寸/ねじ深さ |
| support bearings/bush/shaft | 2軸分候補 | 4 PWM軸分候補 | 在庫UNKNOWN | radial load/clearance |
| filament | coupon/D分 | C全体分 | 材料/残量UNKNOWN | bed/nozzle/profile |
| camera | 0 | dataset段階1–2候補 | 初期位置制御には追加不要 | 視野/fps/同期 |
| USB DXL adapter | 0–1 | 0–1 | STM32透過成功/在庫で不要 | SDK transport適合 |

最小Dセットは手持ちPWM2台+STM32+実位置sensor2台+保護付き外部電源+取付/支持部品。既存在庫で賄えれば追加購入を減らせるが、ゼロ購入保証不可。
将来6軸の追加motor購入は現時点では保留。肩が不適合なら、既存別motor型番を棚卸し→釣合い/軽量/短縮→適正smart motor購入比較の順。
予算枠例：Standard motor6台+interface/電源等 2.5–4万円、all Dynamixel不足motor/mount等 4–10万円以上、Hybrid feedback/electronics/power等 1–3万円。メーカー見積も現在価格も根拠にしていない概算で、未確認在庫/肩交換次第で大きく変わる。発注判断に使わない。

購入せず進められる作業：公式調査、在庫/寸法記録、Inventorパラメータ設計、FK/負荷モデル、mock API/firmware状態遷移設計。coupon製作もフィラメント/締結材が既にある場合に限る。今回印刷はしない。

## 2026-10-11 在庫更新とP1追加BOM

VS-S092J10個、XL3302個は確定。軸受0個、STM32未購入/未選定。プリンタAdventurer 5M Pro。上の旧在庫判定を最新inventoryで置き換える。[今回の追加BOM](../mechanical/two_joint_prototype/additional_bom.md)と[実CAD BOM](../mechanical/two_joint_prototype/mechanical_bom.csv)を参照。発注/購入なし。

## 公式継承/JIS改訂BOM
最新の各occurrenceはmechanical/follower_six_axis/mechanical_bom.csv、two_joint_revb/mechanical_bom.csv、追加候補はmechanical/release_review/additional_bom.csv。新cradleは干渉があり製造HOLD。モータ購入・部品発注なし。
