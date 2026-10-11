# 未通電の制御構成

PC Python → USB(ST-LINK VCP) → STM32 UART → 独立timer PWM×2。Encoder×2 → 3.3 V基準の別I2Cバス2本 → STM32 → PC。AS5048AならSPI共通＋別CS。今回は通信・PWM出力コード、書込み、電源接続を実施していない。

第一候補NUCLEO-G474RE: supercapプロジェクトのSTM32G474RET6と系統を合わせられる。倒立振子はG431RBT6を使用するためG4 HAL/開発環境の共通化も候補。基板の流用はしない。[ST公式NUCLEO-G474RE](https://www.st.com/en/evaluation-tools/nucleo-g474re.html)、[UM2505](https://www.st.com/resource/en/user_manual/dm00556337.pdf)を参照。ST-LINK VCPとターゲットnative USBを区別する。選定は未購入、リビジョン/ピン/ジャンパはTBD。F446REもUSB VCP、PWM、2本のI2Cを条件に代替候補。

PWM周期/端点/ロジック入力閾値はメーカー確認TBD。50 Hz、1000–2000 usを確定値にしない。joint_config.pyは未校正のpulse変換を拒否し、初期角度への自動送信を行わない。

Vstone用外部DCを4–9 V定格内で用意し、評価候補7.4 Vとする。PC USBはサーボへ給電しない。連続/ピーク電流が不明なので電源A値、ヒューズA値、配線径、コネクタの最終選定はTBD。2台の実測Ipeak、Imoving、Iholdから供給容量と選択遮断を決定。停止トルク試験は今回の計画に含めない。

外部DC → 主ヒューズ → 独立非常停止で駆動電源を切るスイッチ → 各軸分岐ヒューズ/電流測定 → サーボ。MCU/センサは独立低電力系とし、スターGNDで信号基準を共有、駆動電流の帰路をUSB/信号線に通さない。PC側の接地ループが生じる場合はUSB絶縁等を検討する。PWM線は無通電サーボへの逆給電を防ぐバッファ/enable構成を選び、reset/USB切断/観測staleでdisableを要求する。

E-stopで電源を遮断しても位置を保持できない。落下受け、机固定、実ストッパの成立が先。現在のJoint_Stopだけでは完成した落下防止にならない。

将来XL330は別の推奨5 V電源＋half-duplex TTL Protocol2.0。Vstoneの7.4 V/PWM経路へ混接しない。LeRobotは既存DynamixelMotorsBusを優先し、独自Robotのget_observation/send_actionを共通position read/writeと時刻/validityへ接続する。今回ソフトはI/Oのない2関節運動学のみ。
