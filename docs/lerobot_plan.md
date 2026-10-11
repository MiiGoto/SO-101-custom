# LeRobot統合方針

Confirmed：固定main commitのDynamixelMotorsBusはProtocol 2.0、tables.pyにxl330-m288 model number1200 / resolution4096がある。FeetechMotorsBusはSTS3215向けでPWM Vstoneの制御/実角度取得には使えない。
旧パスcommon/robot_devicesや古いconfigure_motorコマンドをコピーしない。取得commitでは公式Followerはsrc/lerobot/robots/so_follower/so_follower.pyのSOFollower。main APIが公開Web版より先行するため版固定が必要。
Robot plugin候補はlerobot_robot_hybrid_so101という別package。RobotConfig派生HybridSO101Config、対応HybridSO101、observation_features/action_features/is_connected/is_calibrated、connect/disconnect/calibrate/get_observation/send_actionを現APIに合わせる。

内部共通API：

```python
read_joint_positions() -> JointSample
write_joint_targets(targets_rad, max_velocity, max_acceleration) -> AppliedTargets
```

全6軸同じjoint名、arm位置rad、gripper関節radを内部単位にする。観測にはactual position・取得時刻・valid・calibration ID・sensor source、指令は別target。
LeRobotの6つの*.pos featuresへ変換する際はarm degree/normalize mode、gripper0–100の開閉対応を明示し、unitsとcalibration versionをdataset metadataに保存。異なるgeometryに標準SO101 policyを直接適用しない。
PWM側は角度→校正済みパルス写像の独自制御とoutput encoder。外部encoderの観測で追従誤差を検出する。外付け高gain PIDを内蔵servo PIDに無条件に重ねない。
DXL側はDynamixelMotorsBus.sync_read(Present_Position)/sync_write(Goal_Position)を優先。原packetを通せるCDC-B/U2D2等と時刻整合が前提。packet-level TTL確認は将来単体タスク。
connectはデフォルトread-only/DISARMEDとし、自動校正・設定変更をしない。公式SOFollower.connect(calibrate=False)でもconfigure()を呼ぶのでread-only保証にはならない。
calibrateはユーザー開始によるホスト側zero/sign/range保存を基本にし、EEPROM/ID変更は別の明示手順。homeは既知安全経路。teleoperateは初期はGUI/keyboard joint jog + enable hold、次に手持ちjoystick。
record_dataset/replay/inferenceはRobot APIで接続後、公式ツールを利用。まず時刻・欠損・joint order・units・limitsをmockで確認し、カメラなしstate記録から段階拡張。実機での実行は今回未実施。
software/joint_contract.pyは依存なしoffline契約試作品。LeRobot subclassでもserial driverでもない。単体試験の合格は統合実行の証明ではない。
