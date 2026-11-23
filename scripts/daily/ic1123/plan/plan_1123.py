# -*- coding: utf-8 -*-
"""11/23 13時台「今の悪さを改善するには具体的にどうすればいいか」の数字。
入力: ic1122/plan/life_1122.txt の ②（10/1 以降に広告を始めた23本・開始〜11/21。同じフォルダの life_1122.py の出力をそのまま読む）・ic1123/cpc/acct_agegender_1026_1122_raw.json（Meta）。
商品の分け方（車まわり／身につける・防寒／家の道具／美容・健康）はこのスクリプトでの分類（Claude の判断）"""
import os, re, json, collections, math
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
CAT = {'伸縮ワックス洗車ブラシ': '車まわり', 'マグネットドアクッション': '車まわり', 'ワイド水切りワイパー': '車まわり', 'クリアビューレインガードフィルム': '車まわり', '高見えレザードアポケット': '車まわり', 'すき間収納シートポケット': '車まわり', '360°マルチクリップ車載スマホホルダー': '車まわり',
       'ハイウエストシェイプパンツ': '身につける・防寒', 'ふわとろ高密度ブランケット': '身につける・防寒', 'シリコンホールド膝サポーター': '身につける・防寒', 'アーチフィット逆ヒールサンダル': '身につける・防寒', '防風あったか裏起毛パンツ': '身につける・防寒', '3WAY着る電気ブランケット': '身につける・防寒', '裏起毛タッチ防寒グローブ': '身につける・防寒',
       'ポータブルヒートシーラー': '家の道具', 'ロングニトリル家事手袋': '家の道具', 'コードレスダブルミスト加湿器': '家の道具', 'ファスナー修理キット': '家の道具', 'コードレス毛玉クリーナー': '家の道具', '充電式ダブルミスト卓上加湿器': '家の道具',
       'ネックマッサージャー': '美容・健康', '携帯電動シェーバー': '美容・健康', 'スマートノーズEMS美顔器': '美容・健康'}
rows = []; on = False
for l in open(D0 + '../../ic1122/plan/life_1122.txt'):
    if l.startswith('■ ②'): on = True; continue
    if l.startswith('■ ③'): break
    m = re.match(r'^  (.+?): (\d\d-\d\d)〜・(\d+)日・広告費 ([\d,]+)・利益 ([+\-][\d,]+)・最初の7日 ([\d.]+)・(停止|配信中)', l)
    if on and m: rows.append(dict(n=m.group(1), start=m.group(2), days=int(m.group(3)), ad=int(m.group(4).replace(',', '')), p=int(m.group(5).replace(',', '').replace('+', '')), f7=float(m.group(6)), st=m.group(7)))
assert len(rows) == 23 and all(r['n'] in CAT for r in rows), [r['n'] for r in rows if r['n'] not in CAT]
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P('■ ① 10/1 以降に広告を始めた23本を種類で分ける（開始〜11/21・当たり＝利益5万円以上）')
for c in ('車まわり', '身につける・防寒', '家の道具', '美容・健康'):
    v = [r for r in rows if CAT[r['n']] == c]; hit = [r for r in v if r['p'] >= 50000]
    P(f"  {c}: {len(v)}本・当たり {len(hit)}本・広告費 {sum(r['ad'] for r in v):,}・利益 {sum(r['p'] for r in v):+,}・最初の7日の倍率 " + '／'.join(f"{r['f7']:.2f}" for r in sorted(v, key=lambda r: -r['f7'])))
    P('    ' + '・'.join(f"{r['n']} {r['p']:+,}" for r in sorted(v, key=lambda r: -r['p'])))
car = [r for r in rows if CAT[r['n']] == '車まわり']; wear = [r for r in rows if CAT[r['n']] == '身につける・防寒']
h = sum(1 for r in car + wear if r['p'] >= 50000); n1, n2 = len(car), len(wear); hc = sum(1 for r in car if r['p'] >= 50000)
pv = sum(math.comb(n1, k) * math.comb(n2, h - k) for k in range(hc, min(n1, h) + 1)) / math.comb(n1 + n2, h)
P(f'  車まわり {hc}/{n1} と 身につける・防寒 0/{n2} の差が偶然で出る確率: {pv:.1%}')
P('■ ② 最初の7日の倍率と、その後')
hi = [r for r in rows if r['f7'] >= 1.5]; lo = [r for r in rows if r['f7'] < 1.5]
P(f"  最初の7日が 1.5 以上: {len(hi)}本 → 当たり {sum(1 for r in hi if r['p']>=50000)}本・利益の合計 {sum(r['p'] for r in hi):+,}")
P(f"  最初の7日が 1.5 未満: {len(lo)}本 → 当たり {sum(1 for r in lo if r['p']>=50000)}本・利益の合計 {sum(r['p'] for r in lo):+,}（広告費 {sum(r['ad'] for r in lo):,}）")
P('■ ③ 出した時期ごと')
for lab, a, b in (('10/1〜10/31', '10-01', '10-31'), ('11/1〜11/7', '11-01', '11-07'), ('11/8〜11/21', '11-08', '11-21')):
    v = [r for r in rows if a <= r['start'] <= b]; cc = collections.Counter(CAT[r['n']] for r in v)
    P(f"  {lab}: {len(v)}本・当たり {sum(1 for r in v if r['p']>=50000)}本・利益 {sum(r['p'] for r in v):+,}｜" + '・'.join(f'{k} {n}本' for k, n in cc.most_common()))
P('■ ④ 買っている人（Meta 計上の購入・アカウント全体・10/26〜11/22）')
seg = {}
for l in json.load(open(D0 + '../cpc/acct_agegender_1026_1122_raw.json'))['data']['data'].split('\n')[1:]:
    r = l.strip().split(',')
    if len(r) == 6 and r[1] in ('female', 'male') and r[0] != 'Unknown': seg[(r[1], r[0])] = int(r[5]) if r[5] != 'null' else 0
T = sum(seg.values()); old = sum(v for (g, a), v in seg.items() if a in ('45-54', '55-64', '65+')); male = sum(v for (g, a), v in seg.items() if g == 'male'); mo = sum(v for (g, a), v in seg.items() if g == 'male' and a in ('45-54', '55-64', '65+'))
P(f'  購入 {T:,}件: 45歳以上 {old/T:.0%}・男性 {male/T:.0%}・男性の45歳以上 {mo/T:.0%}・女性の45歳以上 {(old-mo)/T:.0%}')
open(D0 + 'plan_1123.txt', 'w').write('\n'.join(out) + '\n')
