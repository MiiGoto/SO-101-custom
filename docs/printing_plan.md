# 3Dプリント計画（今回は印刷しない）

Confirmed：個人プリンタが使用可能。モデル・bed・nozzle・filament・精度TBD。
公式の初期条件：PLA+、0.4 mm nozzle/0.2 mm layerまたは0.6/0.4、15% infill。支持と穴へのsupport回避は固定commitのREADME参照。実際のcustom構造に必要な周壁/リブを15% infillだけで保証しない。
PLA+：取付試験と低熱初期試験候補。PETG：靱性候補だがクリープ/寸法/糸引き/支持性を別評価。servo周辺の温度が上がる場合は材料を再選定。

| 優先/部品 | 数候補 | 向き/支持候補 | 使用量・時間 | 受入 |
|---|---:|---|---|---|
| 1 Vstone hole/horn/反対軸coupon | 1 | 大きな固定面をbed、穴支持回避 | TBD：CAD/材料/slicer未確定 | 現物ネジ深さ・着座・すきま |
| 2 XL330 mount coupon | 1 | 固定面をbed | TBD | body/horn/ケーブル/ねじ |
| 3 encoder固定/磁石carrier coupon | 1組 | sensor座面flat、gap shim別体 | TBD | output軸の共線/非接触/診断 |
| 4 D shoulder clevis / upper50 / forearm60 | 各1 | 曲げ方向が層間剥離を招かない配置 | TBD | 重量/剛性/可動域/軸受 |
| 5 C full follower構造 | mechanical_plan参照 | 各部品の応力/overhangから決定 | TBD | D受入とCAD全sweep後 |

すきまcouponは例0.1/0.2/0.3 mm系列（仮定）、穴径と挿入/ねじ締結を測って確定。ホーン接合を弱い圧入だけで保持しない。
質量/時間を架空のslicer値で埋めない。CAD確定後、同じprofileで各STLをsliceしg/時間/サポート量をCSVへ保存、秤で比較。
組立順：coupon適合→支持軸/ベース固定→肩→短上腕→肘→短前腕→encoder/ケーブル→無通電手動range確認。6軸拡張は遠位部から取付誤差を検査し、motor軸に無理な横荷重を掛けない。
最初に印刷する候補はVstone取付coupon。型番/寸法未確認の現在はSTL製造を凍結する。
