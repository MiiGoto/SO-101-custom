# 最初の印刷・測定
最初はServo_Body_Fit_Gridのみを手動スライスする。STLはmm。底面をベッドに置き、PLA、ノズルは実装径を先に確認。0.4mm装着の場合の候補：層0.2mm、外周4、上下面5、coupon100%infill、サポートなし。温度は使用PLAメーカー指定から選ぶ。プリンタへ送信・印刷は未実施。
3窓19.2/19.4/19.6×38.2/38.4/38.6の造形後寸法をノギスで測る。どの窓にケースが軽く入るか、挿入抵抗・欠け・軸方向・耳の干渉を記録。無理に押し込まない。7穴径も造形寸法測定。印刷状態を変えずにfdm_correction_template.csvへ記録。
次にMounting_Pitch_Gaugeで実耳穴を観察し、OEM_Horn_Trace_Plateに純正ホーンの輪郭/穴を転写。転写板は軸結合部品ではない。Encoder_Gap_Gaugeは幾何・配列確認だけでセンサ基板互換と磁石air gap未認定。Bearing_Fit_Gaugeは購入予定軸受の実寸が分かってから。XL330_Horn_PCD_Testは純正穴に対応する配置確認で、固定ねじの径・侵入長を先に確認。
全6couponのソリッド体積からPLA材料量・6mm³/s流量+50%移動時間を仮定した時間screenはmesh_validation.json。スライサー見積もりではない。ノズル径/速度/ブリムで変わる。センサ/ホーン/モータを装着したフルフレーム印刷・締結・通電は承認対象外。
docs/servo_measurement_sheet.pdfの測定欄は空欄。本体/軸中心/耳/穴/ホーン/出口/裏面を測りCSVへ記録する。Measuredは実測時のみ記入する。測定後、native UserParameterを変更しSTL・図面・検査表を再生成する。
