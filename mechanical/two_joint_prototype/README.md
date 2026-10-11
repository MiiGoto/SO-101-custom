# 肩・肘2関節試作 P1

今回の成果はInventor 2026.2で保存した実ソリッドCAD、寸法確認用STL、拘束/干渉/質量の検証、オフラインソフト。製作・通電の承認とは別である。

- [最終レビュー](review_report.md): Confirmed / Assumption / TBD、トルク、補償、製作ゲート。
- [ネイティブアセンブリ](iam/SO101_TwoJoint_Prototype.iam): 32構成部品、91拘束。`ipt/`に31種類。
- `idw/`と`pdf/`: 部品とアセンブリのレビュー図面。加工・公差・全ねじ接続まで承認した製造図ではない。
- `step/`と`stl/`: 実際に生成した中立形式。Envelopeは現物部品を表す仮包絡で、印刷しない。
- [最初のSTL](stl/Servo_Mount_Coupon.stl)、[印刷条件](print_plan.md)、[BOM](mechanical_bom.csv)、[追加BOM](additional_bom.md)。
- `mass_properties.json`、`torque_analysis.json`、`gravity_compensation.json`、[干渉結果](interference_report.md)、`analysis/`の原記録。
- `joint_config.py`、`kinematics.py`、`tests/`: 実機I/Oなし。7件のオフライン制御テストと計算成果物の追加チェック。

再生成は`powershell.exe`またはPowerShellから`scripts/build_inventor.ps1`を実行する。Inventor 2026の既存セッションが必要。変更前に現在のネイティブCADを保存/バックアップし、Inventor書類を閉じる。スクリプトは既存の原計画や他プロジェクトを変更しないが、このP1生成物は更新する。ネイティブユーザーパラメータへの全フィーチャ連動は未実装、寸法はスクリプトで管理。

生成後は`scripts/audit_inventor.ps1`、Pythonの`scripts/validate_meshes.py`、`scripts/analyze.py`、`scripts/finalize_report.py`。図面は`scripts/drawings.ps1`。これらはCAD内の姿勢変更だけを行い、実機を動かさない。LeRobot接続やSTM32書込みはない。

`GetDegreesOfFreedom`の数値APIはCOM型変換で未取得。軸mate/軸方向flush構造と肩のみ・肘のみの角度変更で独立した2回転軸を検証。本拘束は姿勢試験後も残し、一時角度拘束は削除した。

原計画の6軸FollowerとLeader拡張は保留維持。今回終了後は次Taskを自動開始しない。
