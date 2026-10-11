"""Build local planning summary tables and reference provenance; no network or hardware."""
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'docs/torque_results.csv').open(encoding='utf-8-sig')))
def table(variants,payload,joints=None):
    s='| 案 | 関節 | 探索静的 Nm | 静的上界 Nm | 動作上界 Nm | 1.25倍設計目標 Nm |\n|---|---|---:|---:|---:|---:|\n'
    for r in rows:
        if r['variant'] not in variants or float(r['payload_kg'])!=payload or (joints and r['joint'] not in joints):continue
        s+='| '+r['variant']+' | '+r['joint']+' | '+' | '.join(f"{float(r[k]):.3f}" for k in ['sampled_static_Nm','conservative_static_Nm','motion_required_Nm','design_target_Nm'])+' |\n'
    return s
text='''# 全6関節の初期トルク計算

Confirmed：公式SO101 URDFから関節位置/RPY、質量、重心を抽出。抽出値はofficial_geometry.json。motor_compatibility.mdの長さは軸間原点移動のノルム。
Assumption：Hybridは同じ関節構造を基に質量・幾何を置換したproxy。Inventor確定CADの質量/COMではない。動的値は仮定された低速運転に対する保守的上界で、実機の必要電流や連続許容値を測定した結果ではない。

## 質量・負荷・範囲の仮定

Hybrid可動group：shoulder 80 g、upper 80 g、lower 85 g、wrist 53 g、fixed gripper48 g、moving jaw12 g。
upper=42 g Vstone+28 g print/fastener+10 g sensor/mount、lower=42+33+10、wrist=18 g XL330+35 g holder等、gripper=18 g XL330+30 g holder等、jaw12 g。motorをlink親側に置くSO101構造を仮定。motor massは候補公式値、残りは質量予算。センサ/mount/ケーブルの実重量はTBD。
肩groupは42 g Vstone+38 g fixture/sensor等。基部pan motorはbase側なのでlift荷重に含まれず、panは全可動groupを駆動。
Hybrid COMは公式各link COMをproxyとして保持し、Bでは幾何offsetを縮小、Cでは対応リンク長比で移動。新motor COMの実位置を保証しない。Bでもmassは固定、s³軽量化を仮定しない。慣性テンソル上界も公式値と0.0002 kg m²の大きい方という予算仮定で、CADの実inertiaではない。
payload=0/50/100 g、接触力5 N、jaw有効lever35 mm。把持トルク0.175 Nmをgripperへ加算。payloadはgripper_frameに置き、gripper bodyが保持するためmoving jawへ二重計上しない。指の偏心/接触分担はTBD。
|速度|<=0.5 rad/s、|加速度|<=1 rad/s²、摩擦/ケーブル抵抗予算PWM0.02 Nm、XL3300.01 Nm、設計余裕1.25。
joint limitsは入力JSON参照。全軸同時の加速を許す保守評価。外界衝突/把持物の引っ掛かり、基部傾き、弾性/gear衝撃、motor自身の反射慣性は未モデル化で、追加評価が必要。

## 計算方法

静的：各bodyのworld COMとjoint軸をFKで変換し、tau_j = axis_j · Σ[(COM_i-origin_j) × (0,0,-m_i g)]。
範囲内30,000姿勢/条件を固定乱数seed101で探索し、座標探索で精密化。各jointの最悪候補姿勢はCSVのsampled_worst_q_rad（順序pan/lift/elbow/wrist flex/roll/gripper）。これはglobal maximumの証明ではない。
姿勢依存の最大を過小評価しないため、別にR_ji=joint経路長の和+body COM normという半径上界を計算し、静的上界 gΣm_iR_ji を使用。直立基部panの重力トルクは0、rollは偏心の最悪を含むこの上界を用いる。
動的：body線加速度上界 a_i <= Σ(alpha_k R_ki)+(Σ|omega_k|)^2 R_0i。joint負荷にΣm_iR_ji a_iとbody回転慣性トルク上界を加える。動作上界=静的上界+慣性上界+摩擦予算。姿勢/加速の最大を同時に足すので実際より大きくなることがある。精密なM(q)ddq+C(q,dq)+g(q)を実CADから作る段階は未実施。
数値の上界はこの仮定モデルに対しての上界であり、不明な質量/COM/外力を含む現物の保証値ではない。

## 50 g負荷：A/B/C比較（肩）

'''+table(['A','B80','B85','B90','C'],.05,['shoulder_lift'])+'''
標準幾何Aの動作上界は候補Vstone公称0.9022 Nmを超える。B85は動作上界0.894 Nmで公称にほぼ等しく、1.25倍目標では超える。Cでも設計目標0.977 Nmで公称より大きい。公称自体が連続値ではないので「動作上界が公称以下なら合格」と判断しない。
単純80–90%縮小だけの案Bは不採用方向。Cもそのまま6軸製作を承認する結果ではなく、肩補助/追加軽量化/要求payload低減/別motorの評価が必要。

## C：全6関節、50 g負荷

'''+table(['C'],.05)+'''
panは重力が0でも全linkの慣性を受ける。rollも斜め保持/偏心payloadで0とは限らない。gripperは自重だけを比較せず接触力を含める。
Cの最大radius経路は約305 mm（90+100+45+70）。これは安全な到達距離やcollision-free workspaceではない。

## C：無payload（把持力仮定は残る）

'''+table(['C'],0)+'''
## D：短い肩・肘、無payload、手首/グリッパなし

'''+table(['D'],0,['shoulder_lift','elbow_flex'])+'''
Dはupper72 g/lower25 g、upper COM35 mm、lower COM30 mm、軸間50/60 mmの独立した仮定。肩設計目標約0.085 Nmと肘約0.036 Nmから始める。実機定格は不明なので合格を保証しない。CSVのDの残り軸はモデル計算列であり、存在する試作motorではない。

## 把持能力の条件式

F_jaw <= tau_gripper_usable / (0.035 m) （伝達効率/構造が直結の場合）。tau_usableはUNKNOWN。
滑り条件はm_payload*g <= friction_coefficient*Σnormal_force。5 Nという接触力目標でも、摩擦係数/片指か両指か/把持重心/衝撃が不明なので50 gを保持できるとは断定しない。jaw開口と指先位置はgeometry/角度から別計算。

## 判定と次に必要な証拠

全軸のusable continuous/peak torqueと熱・gear条件が未確認のため最終適合はTBD。メーカー連続データか、将来の安全な負荷/温度/電流/実角度試験で許容envelopeを確認して比較。
外付けencoderはbacklash/追従誤差の観測を可能にするが保持トルクを増やさない。停電時保持を保証するブレーキは確認されていない。低い位置・受け台・必要なら釣合い機構。
再計算はsimulation/torque_envelope.py、検証はtests/test_offline.py。出力126行、7モデル×3payload×6関節。重力の位置エネルギー微分照合/半径上界/zero mass/単位変換はテスト合格。動的上界は簡略モデルであり実機との照合未実施。
'''
(ROOT/'docs/torque_report.md').write_text(text,encoding='utf-8')
manifest=[]
versions=json.loads((ROOT/'docs/source_versions.json').read_text(encoding='utf-8-sig'))
for folder,repo,commit in [('mechanical/reference','TheRobotStudio/SO-ARM100',versions['hardware_commit']),('docs/upstream/lerobot','huggingface/lerobot',versions['lerobot_commit'])]:
    for p in sorted((ROOT/folder).rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT/folder).as_posix()
        manifest.append({'local_path':p.relative_to(ROOT).as_posix(),'commit':commit,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'source_url':f'https://github.com/{repo}/blob/{commit}/{rel}' if rel!='tree.json' else f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'})
with (ROOT/'docs/source_manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
print('Wrote torque_report.md and',len(manifest),'source SHA256 records.')
