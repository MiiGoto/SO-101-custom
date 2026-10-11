# JIS図面品質レビュー・2026-10-11
全10PDFを1400pxに描画し、全ページをcontact1..3と重要couponの個別表示で確認。はみ出していた組立投影図は1:5で再配置、大きすぎた尺度ラベルは縮小・寸法から離して再出力した。
Confirmed: native JIS standard、Default(JIS)寸法style、third angle（FirstAngleProjection=False）、mm、A4 297×210/A3 420×297。日本語表示、枠・表題欄・図番、4views、モデル関連寸法を確認。テンプレートA4/A3を実際に再読込。
JIS B0001:2019 / Z8315-2:1999の書誌・様式を参照。規格全文による全条項・記号寸法・幾何公差適合は未検証。
全ての製作図を完成としない。未知のhorn/ねじ深さ、位置datum、インサート、必要断面、FDM fit、材料/強度はHOLD。公式Upper/Under図は重要部品の形状参照用で、全体外形・全穴位置を網羅した製造図ではない。cradleも締結側の設計未確定。
旧RevAの32枚は保存、今回全32枚をJIS製造図へ完成した扱いにはしない。

|IDW|関連寸法数|標準|第三角法|PDF表示|製造リリース|
|---|---:|---|---|---|---|
|Bearing_Fit_Coupon_JIS.idw|8|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|Encoder_Alignment_Test_JIS.idw|6|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|Horn_Adapter_Test_JIS.idw|4|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|Servo_Mount_Coupon_JIS.idw|7|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|Under_arm_SO101_JIS.idw|7|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|Upper_arm_SO101_JIS.idw|7|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|Vstone_Cradle_HOLD_JIS.idw|6|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|XL330_Cradle_HOLD_JIS.idw|6|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|SO101_TwoJoint_RevB_JIS.idw|0|Default Standard (JIS)|確認|確認・日本語正常|HOLD|
|SO101_Custom_Follower_RevA_JIS.idw|0|Default Standard (JIS)|確認|確認・日本語正常|HOLD|

非空白・図形の用紙内配置・文字・材質候補/部品番号・HOLD表示・モデル参照欠落なしは確認済み。寸法線/リーダーを量産製図として最終承認するレビューと、実物製作/検査可能な全寸法網羅は未完了。
組立図番号はSO101-ASM-B-001 / SO101-ASM-A-001、部品図番号SO101-B-001..008で重複を除いた。数量欄はBOM参照であり、下面に全ねじ製造仕様が確定した意味ではない。
