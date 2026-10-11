# 公式参照と改訂記録

取得確認日：2026-10-11 JST。latest/mainは将来変わる。現在の実機/LeRobotインストール版はUNKNOWN。

| 参照 | 固定状態 |
|---|---|
| [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100/tree/a758567c3978dfeefe282ede0500085a48fe8f78) | commit a758567c3978dfeefe282ede0500085a48fe8f78、2026-10-06 07:26:52 UTC |
| [huggingface/lerobot](https://github.com/huggingface/lerobot/tree/b9cb121cb7d4e3e26ec5c906d08dda68d151ba52) | commit b9cb121cb7d4e3e26ec5c906d08dda68d151ba52、2026-10-08 21:24:13 UTC |
| LeRobot pyproject.toml | 0.6.2、Python >=3.12。インストール/実行はしていない |
| [SO101 guide](https://huggingface.co/docs/lerobot/en/so101)、[Custom hardware](https://huggingface.co/docs/lerobot/integrate_hardware) | Web閲覧時の版表示は0.4.3を含む。実装根拠は上記commitのdocs/source/*.mdxを保存して使用。公開サイトとmainの同一版を仮定しない |

Confirmed：5つのアーム回転関節と1つのグリッパ駆動軸、計6アクチュエータ。6D姿勢を自在に制御する6Rマニピュレータという意味ではない。
Followerは物体を操作する位置制御機、Leaderは人が動かして指令を取得する操作機。
Follower：STS3215 7.4 V版・減速1/345を6個。Leader：pan1/191、lift1/345、elbow1/191、wrist flex/rollとgripper1/147。
Feetech TTLシリアルバス、USB motor bus adapter（公式BOMはMotor Control Board）を各アームに1枚。DYNAMIXEL Protocol 2.0とは異なる。
公式BOMの7.4 V版は5 V給電を用いる構成。別売12 V版には12 V 5 A以上の電源を指定。12 V版と7.4 V版を混在させない。公式供給例は本ハイブリッドの必要電流の根拠にならない。
モータID/baud設定→組立→中間位置/範囲のキャリブレーションという手順。今回それらの実機操作は未実施。
カメラ：外部と手首のUVC等が候補、関節制御だけならカメラ不要。模倣学習時は実位置と画像の同期、操作記録、dataset、学習、policy評価が必要。

公式CAD：STEP/SO101/SO101 Assembly.step、個別STEP、STL/SO101にFollower/Leader別パーツ。SO100フォルダとMini（SO100）をSO101小型版として扱わない。
参照用にassembly・上腕/前腕STEP、SO101 new calibration URDF/MJCFを保存。STL全体は取得/印刷していない。
公式URDFはOnshapeから生成されたモデル。新旧キャリブレーションモデルに差があり、STEPとの完全な同一改訂・実機寸法はTBD。URDFのeffort=10、velocity=10はモータ許容値とみなさない。
関節間の原点移動ノルム：lift→elbow 116.00 mm、elbow→wrist flex 135.00 mm、wrist flex→roll 63.72 mm、roll→tool 98.45 mm。平行/斜交軸オフセットもあるためこの和は実作業空間半径ではない。
URDF質量・重心・関節limitsの抽出はofficial_geometry.json。質量は公式モデル値であり造形後の実測質量ではない。

両リポジトリのLICENSEはApache-2.0として取得。参照コピーにLICENSEを保持。派生物を配布する際は原著作権/ライセンス/変更表示等を維持し、第三者追加物の権利を別途確認する。今回は公開しない。
公式資料の改訂日時/commitとローカルSHA256はsource_versions.json / source_manifest.csvに記録。
