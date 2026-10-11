# 実機なしの検証

公式SO101/new calibration URDF/MJCFを固定commitで保存。licenseを保持。meshesは未取得なので現コピーをそのままviewerへ読み込んでも完全な表示/衝突モデルは構成できない。
torque_envelope.pyはURDFの関節位置・RPY・各linkの質量/COMを読むFKと重力計算。姿勢範囲内の数値探索、保守的な姿勢非依存負荷上界を計算。proxyモデルの成立性screeningで、剛体物理エンジンの追従検証やIKは未実装。
将来：CAD確定→custom URDFとmesh/mass/inertiaを書き出す→joint range/FK/作業域→IK（5 arm axesなので任意6D姿勢は拘束）→机/自己/ケーブルcollision→limited simulated controller→offline record/replay→低速実機の順。
モデル改造時、mount offset、axis sign、motor/print/cable mass、COM、inertia、camera extrinsic、gripper jaw linkageを更新し、標準URDFを名前だけ変更して済ませない。
過去のSO101シミュレーションは本hybridの検証に流用しない。Sim-to-Sim・計算一致が実機の熱/バックラッシュ/通信/落下安全を証明することはない。
