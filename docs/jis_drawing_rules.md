# JIS製図ルール
Confirmed: Inventor2026.2 installed ja-JP/Metric/JIS.idwを基に作成。ActiveStandardStyle=Default Standard (JIS)、FirstAngleProjection=False、mm。日本語ＭＳゴシック、A4/A3、第三角法の投影図・記号、枠、部品番号/名称/数量欄/材質/尺度/単位/日付/改訂/作成者/状態を含む。
参照規格: JIS B 0001:2019 機械製図、JIS Z 8315-2:1999 正投影法。日本規格協会の公式書誌で確認。
https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+B+0001%3A2019
https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+Z+8315-2%3A1999
規格全文の条項照合・完全適合認証は未実施。JIS様式採用をJIS完全適合と呼ばない。
図形寸法はDrawingCurveのGeometryIntentへ関連付け、手入力数値で代替しない。ビュー尺度はネイティブ尺度ラベル。断面・詳細・datum・幾何公差・ねじ深さ等が必要なものは製造図の完成までHOLD。
FDMにJIS B0405普通公差を一律適用しない。取付窓はケース実測とcoupon測定、ねじ穴/磁石座/軸受座/インサートは個別測定。公差記号だけで精度を保証しない。
元Rev Aの32枚は保管。今回重要部品と組立図から別IDWへ置換し、残りの旧ISO図はJIS化未実施と記録する。
テンプレートはmechanical/templates/SO101_JIS_A4.idw、A3.idw。再読込して使用し、日本語PDFを実表示レビューする。
数量欄がBOM参照のとき同番号のBOMを必須とする。材料候補は実部品の製造指定が確定するまでHOLD。
