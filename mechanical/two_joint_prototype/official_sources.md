# 今回の一次資料と改訂状態

取得/確認日2026-10-11。元のSO-101/LeRobot pinとライセンス記録は既存docs/official_reference.mdを維持。今回の31部品は独自生成で、公式CADを縮尺変更したものではない。

- [Vstone VS-S092J公式](https://www.vstone.co.jp/robotshop/index.php?main_page=product_info&products_id=299): 商品掲載2007-12-05、現状販売終了、発売時仕様。19×38×38.5 mm、42 g、公称トルク/速度/電圧/PWMを確認。寸法付きホーン、連続トルク、PWMパルス端点、電流は未確認。
- [Flashforge Adventurer 5M Pro公式](https://www.flashforge.com/products/adventurer-5m-pro): 220×220×220 mm。現ユーザーのノズル・材料は現物TBD。
- [ST NUCLEO-G474RE](https://www.st.com/en/evaluation-tools/nucleo-g474re.html)、[UM2505](https://www.st.com/resource/en/user_manual/dm00556337.pdf): 現行製品/USB VCP候補。サイトのUM2505表示Rev7.0、2026-05-22。購入・ピン実装・ファーム書込みなし。
- [Autodesk XYZMomentsOfInertia](https://help.autodesk.com/cloudhelp/2024/ENU/Inventor-API/files/MassProperties_XYZMomentsOfInertia.htm): COMを原点とする慣性。ドキュメント2024、実際の実行server2026.2。使用interop2025はenumの定義用、サーバ版を別途照合。
- [Autodesk Angle Constraint](https://help.autodesk.com/cloudhelp/2024/ENU/Inventor-API/files/AssemblyConstraints_AddAngleConstraint.htm): 数値rad/文字列deg、一時角度拘束で姿勢検証。
- [Autodesk DOF API](https://help.autodesk.com/cloudhelp/2024/ENU/Inventor-API/files/ComponentOccurrence_GetDegreesOfFreedom.htm): 調査したがCOM出力取得は未成功。独立2回転の拘束構造と独立角度変更で検証し、数値取得TBDを維持。
- [Autodesk CloseAll](https://help.autodesk.com/cloudhelp/2024/ENU/Inventor-API/files/Documents_CloseAll.htm): 保存せず閉じる。今回生成した書類のみであることを確認した上で、保存済み形状のcold reloadに使用した。

AS5600/AS5048Aの旧メーカー配布URLには移転/404があった。公称方式は候補扱いとし、最終モジュールのdatasheet版、磁場条件、air gap、更新速度/フィルタ遅延はTBD。取得失敗を確認済み資料として記録しない。センサ仕様の確定は製作レビュー条件である。
