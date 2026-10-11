# 最初の造形準備
Confirmed: Adventurer5M Pro、220×220×220mm。ノズル/材料/残量はTBD。G-codeなし、印刷なし。
Servo_Mount_Couponを最優先。次はHorn_Adapter_Test、Encoder_Alignment_Test、Bearing_Fit_Coupon。全て寸法確認専用で、モータ荷重を載せる製品ではない。
PLA+またはPETG、0.4mm候補/0.2mm層、外周4、底上面5層、couponは100%充填候補。広い平面をbedへ、穴軸はZ、基本supportなし。cradleは底をbedへ支持壁をZ、構造荷重は未認定。
window38.6×39.1とケース隙間を測る。slot3.4×20は独自クランプ用。horn OD30/t4/access5/PCD24は自作側だけ、メーカーhorn穴ではない。encoder32×32/t4/window18は汎用基板fixture、磁気性能試験は未実施。625coupon65×25×8の16.0/16.2/16.4はfit比較用。部品表のHOLD寸法は穴あけ/圧入しない。
補正は実測外形/穴/窓別に記録し、軸受は無理な圧入をしない。公差は印刷後測定で検証、JIS普通公差一律適用なし。
mm/STLmanifold/外形はmesh_validation.json。filament gと時間は未知のnozzle/material/profileのslicerが必要なためTBD。出力STLは印刷指示ではない。
全フレーム、cradleの荷重利用、motor envelope/REF datumの印刷はHOLD/禁止。元officialSTLを形状の正本として再利用する。
