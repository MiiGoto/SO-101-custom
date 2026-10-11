# カスタム差分
固定公式commit `a758567c3978dfeefe282ede0500085a48fe8f78`、Apache-2.0。Rev Aは独自90/100 mmのP1として保存。Rev BとFollowerは別ディレクトリ。
1. 公式11部品は形状再利用、IPT化と拘束用datum追加のみ。リンク長変更なし。
2. Vstoneクレードル: 機体38×38.5×19 mm仮定、窓38.6×39.1 mm、左右4 mm支持壁、4 mm底板、独自3.4×20 mmクランプ長穴。メーカー耳穴ではない。干渉・固定・hornはHOLD。
3. XL330クレードル: 窓20.6×34.6 mm、同じ独自クランプ構造。公式holderと干渉し、現状は組立不能。底/側面への固定方式を再設計する必要あり。
4. Vstone4台・XL3302台の包絡体。メーカーCADをカスタムモデルへ転用せず、独自簡略ソリッドを使用。Vstone軸–ケース関係はAssumption。
5. 7個の非製造REF datum carrierは非表示・reference BOM、1e-9 kg質量。基準座標/拘束にのみ使い、物理部品として印刷しない。
6. 二関節Rev Bは公式Baseを追加し、Base Panを3面拘束で固定。肩・肘だけ回転する。panロックの実物締結部品はTBD。
7. Rev Aの4 couponをコピー保持。センサ実装・ホーン結合を成立した扱いにしない。
アダプタだけで成立した場合にADAPTER_ONLYへ変更する。現時点では部品表のUNMODIFIED_UPSTREAMとORIGINAL_CUSTOM_PARTを使い、MODIFIED_UPSTREAMは0。
必要な次変更は干渉しているクレードル/取付局所に限定する。実印刷重量・連続能力で不成立が示されるまでは、公式リンク全体の縮小をしない。
第三者機器入り公式アセンブリとROBOTIS資料はLOCAL_REFERENCE_ONLY、再配布権未確認。無断公開しない。出典・LICENSE・source_manifest.jsonを保持。
