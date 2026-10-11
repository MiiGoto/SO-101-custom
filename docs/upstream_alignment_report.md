# 公式SO-101との整合・2026-10-11
Confirmed / Assumption / TBDを区別する。固定commit `a758567c3978dfeefe282ede0500085a48fe8f78`。
公式STEPアセンブリをInventor 2026.2に読み込み、実個別STEPからネイティブIPTを生成した。既存Rev Aは変更しない。
出典: https://github.com/TheRobotStudio/SO-ARM100/tree/a758567c3978dfeefe282ede0500085a48fe8f78/STEP/SO101

| 比較 | 既存Rev A | 今回基準 | 差 |
|---|---:|---:|---:|
| Shoulder Lift–Elbow Flex軸間 | 90 mm | 116.000021 mm | +26.000021 mm (+28.89%) |
| Elbow Flex–Wrist Flex相当 | 100 mm（payload点まで） | 135.000185 mm（手首軸まで） | +35.000185 mm (+35.00%); 終端の意味は異なる |
| 二リンク長合計 | 190 mm | 251.000206 mm | +61.000206 mm (+32.11%); collision-free reachではない |

これはSTEPモデル全長の外形をリンク長と呼んだ値ではなく、公式URDFの関節座標から求めた軸間距離。
Upper_armの肩出力円筒軸、Under_armの肘出力円筒軸を実STEPで抽出し、URDF基準に対する軸直交方向誤差は約0.00005 mm（URDF丸め誤差）だった。
サーボ取付側はモータ出力軸の円筒穴を必ずしも持たない。最寄りの別穴を出力軸として採用していない。実データは`mechanical/release_review/axis_alignment.json`。
追加測定されたWrist_Roll_Pitch軸の整合は同JSONを参照。CAD内の基準座標と現物軸位置の一致は別確認。

個別STEP由来のUpper外形は約142.17×24.50×67.30 mm、Underは約130.80×24.02×64.40 mm（各部品座標）。旧板状Upper90×22×5 / Forearm100×20×5とは支持構造も異なる。
公式全体STEPには歴史的SO100表記が残る部品名がある。SO101ディレクトリの固定データという出所を優先し、SO100の別ファイルに置換していない。

再利用: Followerに公式造形部品11種類、二関節Rev Bに8種類。公式STEP/STLの形状は変更・縮尺変更していない。追加datumは形状を変更しない。
ADAPTER_ONLYは組立適合を示す言葉としてまだ認定しない。現状は原形＋追加クレードルの干渉検討モデル。
公式モータ中心・ホーン出力位置は関節基準として保持。Vstoneケース軸位置・ホーン面・メーカー穴はTBD。XL330はメーカー図面の20×34×26 mm・PCD12・4×φ1.6 DP3 max/M2タッピングを確認、ケース包絡体の内部COMや取付実装はAssumption。
公式6関節とtool frameの座標、RPY、元limitsはkinematic_reference.json。元limitsをPWM180°機へ無条件適用しない。暫定評価範囲PWM各±75°、roll±90°、gripper0..90°はAssumption。

支持、穴、配線、モータ包絡体、実質量/COM、干渉は別表に記録。全到達空間、連続干渉、締結アクセス、ケーブル曲げ半径はTBD。
取り込み全アセンブリの初期材料は現物材料と一致しないためその質量を本Hybridへ流用せず、カスタムCADの材料・overrideを明記する。
