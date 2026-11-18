# -*- coding: utf-8 -*-
"""11/18 「何が原因だったの？詳しく」: 11/17 のカート率の落ち込みを Meta 側の数字でも確かめる
①Meta のカート追加÷リンククリック（Shopify の来訪を分母にしない別の物差し）をキャンペーン別に 11/3〜16 と 11/17 で比べる
②Shopify の来訪元（instagram / facebook / 不明）別のカート率
③Shopify の入口ページ別の来訪 ÷ Meta のLPV（来訪が水増しされていないか）"""
import csv, json, collections, math
R = [l.strip().split(',') for l in open('ad_daily_1103_1117_raw.txt') if l[0] != '#']
num = lambda x: 0 if x == 'null' else float(x)
NEW = {'スマートノーズEMS美顔器v2', '快適マジックインソール v3', '携帯電動シェーバーv2', '3WAY着る電気ブランケット', '360°マルチクリップ車載スマホホルダー', '裏起毛タッチ防寒グローブ'}
OLD = {'伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', 'ワイド水切りワイパー', 'マグネットドアクッション', '4-in-1マルチクリーナー', '伸縮ワックス洗車ブラシ'}
agg = collections.defaultdict(lambda: [0.0] * 6)  # (camp, period) -> cost, imp, clk, lpv, atc, pur
for d, c, s, a, *v in R:
    p = '17' if d == '2026-11-17' else 'b'
    for i, x in enumerate(v): agg[(c, p)][i] += num(x)
    g = 'old' if c in OLD else 'new' if c in NEW else 'other'
    for i, x in enumerate(v): agg[(g, p)][i] += num(x)
def pois(o, e):  # 片側（下）ポアソン p
    return sum(math.exp(-e) * e ** k / math.factorial(k) for k in range(int(o) + 1))
print('■① Meta のカート追加÷リンククリック（11/3〜16 → 11/17）。期待＝11/17 のクリック×ふだんの率')
print(f'{"":<22}{"ふだん":>8}{"11/17":>8}{"差":>6}  カート 実際/期待  下側p  （クリック率 ふだん→11/17／CPM ふだん→11/17）')
for c in sorted(OLD, key=lambda c: -agg[(c, '17')][0]) + ['old'] + sorted(NEW, key=lambda c: -agg[(c, '17')][0]) + ['new']:
    b, t = agg[(c, 'b')], agg[(c, '17')]
    if t[2] == 0: continue
    rb = b[4] / b[2] if b[2] else float('nan'); rt = t[4] / t[2]; e = rb * t[2]
    ctrb = b[2] / b[1] * 100 if b[1] else float('nan'); ctrt = t[2] / t[1] * 100
    cpmb = b[0] / b[1] * 1000 if b[1] else float('nan'); cpmt = t[0] / t[1] * 1000
    lab = {'old': '＝前からの商品 計', 'new': '＝新しい商品 計'}.get(c, c[:20])
    print(f'{lab:<22}{rb*100:7.2f}%{rt*100:7.2f}%{(rt/rb-1)*100:+5.0f}%  {t[4]:4.0f}/{e:5.1f}  {pois(t[4], e) if e==e else float("nan"):.3f}  （{ctrb:.2f}→{ctrt:.2f}%／{cpmb:,.0f}→{cpmt:,.0f}）')
# 前からの商品の日別（ふだんの日ごとのぶれと比べる）
print('■①-2 前からの商品のカート追加÷リンククリック（Meta）日別')
day = collections.defaultdict(lambda: [0.0] * 6)
for d, c, s, a, *v in R:
    if c in OLD:
        for i, x in enumerate(v): day[d][i] += num(x)
for d in sorted(day): print(f'  {d[5:]}: {day[d][4]/day[d][2]*100:.2f}%（{day[d][4]:.0f}／{day[d][2]:.0f}）  LPV÷クリック {day[d][3]/day[d][2]*100:.0f}%')
xs = [day[d][4] / day[d][2] for d in sorted(day) if d != '2026-11-17']
print(f'  11/3〜16 の日別: 最小 {min(xs)*100:.2f}%・最大 {max(xs)*100:.2f}%・14日中 11/17 より低い日 {sum(x < day["2026-11-17"][4]/day["2026-11-17"][2] for x in xs)} 日')
# ② 来訪元
F = json.load(open('referrer_daily_1103_1117_raw.json'))['rows']
ref = collections.defaultdict(lambda: [0, 0, 0])
for d, r, s, ca, co in F:
    k = r if r in ('instagram', 'facebook', '') else 'その他'
    p = '17' if d == '2026-11-17' else 'b'
    ref[(k, p)][0] += int(s); ref[(k, p)][1] += int(ca); ref[(k, p)][2] += int(co)
print('■② Shopify の来訪元別カート率（11/3〜16 → 11/17）')
for k in ['instagram', 'facebook', '', 'その他']:
    b, t = ref[(k, 'b')], ref[(k, '17')]
    e = b[1] / b[0] * t[0]
    print(f'  {k or "来訪元なし":<10} 来訪/日 {b[0]/14:,.0f}→{t[0]:,}  カート率 {b[1]/b[0]*100:.2f}%→{t[1]/t[0]*100:.2f}%  カート {t[1]}／期待 {e:.1f}  下側p {pois(t[1], e):.3f}')
# ③ 来訪元 × 前からの商品のページ（同じページの中で、広告から来た人と来訪元なしの人を比べる）
import os
P = json.load(open('ref_page_raw.json'))
OLDP = {'nano-fine-fiber': 'ガラス', 'vacuum-adsorption': 'W', 'washable-reusable': 'ナノ', 'soft-silicone-car-squeegee': 'ワイパー', 'silicone-magnetic-door': 'ドア', 'portable-small-wireless': '4in1', 'car-wash-cotton': 'ブラシ'}
NEWP = {'high-end-nose': 'ノーズ', 'car-phone-holder-in-car': 'クリップ', 'soft-super-sports': 'インソール', 'outdoor-warming-heated': 'ブランケット', 'reciprocating-shaver': 'シェーバー'}
def grp(path):
    for k, v in OLDP.items():
        if k in path: return 'old'
    for k, v in NEWP.items():
        if k in path: return 'new'
B = {(r, p): (int(s), int(c)) for r, p, s, c in P['rowsb']}
print('■③ 来訪元 × ページのまとまり（11/3〜16 の上位60行・11/17 の上位45行にある組み合わせだけ。期待＝11/17 の来訪×同じ組み合わせのふだんの率）')
for g, gl in (('old', '前からの商品のページ'), ('new', '新しい商品のページ')):
    for refn, rl in (('instagram', 'instagram'), ('facebook', 'facebook'), ('', '来訪元なし')):
        s = c = e = 0
        for r, p, s1, c1 in P['rows17']:
            if r != refn or grp(p) != g or (r, p) not in B: continue
            bs, bc = B[(r, p)]
            s += int(s1); c += int(c1); e += int(s1) * bc / bs
        if s: print(f'  {gl} × {rl:<9}: 来訪 {s:4d}  カート {c:3d}／期待 {e:5.1f}（{(c/e-1)*100:+.0f}%）  下側p {pois(c, e):.3f}')
# ④ 日別（Shopify・広告から来た人＝instagram+facebook）
print('■④ Shopify の日別カート率（instagram+facebook から来た人／来訪元なしの人）')
dd = collections.defaultdict(lambda: [0, 0, 0, 0])
for d, r, s, ca, co in F:
    if r in ('instagram', 'facebook'): dd[d][0] += int(s); dd[d][1] += int(ca)
    elif r == '': dd[d][2] += int(s); dd[d][3] += int(ca)
for d in sorted(dd): print(f'  {d[5:]}: 広告から {dd[d][1]/dd[d][0]*100:.2f}%（{dd[d][1]}／{dd[d][0]}）  来訪元なし {dd[d][3]/dd[d][2]*100:.2f}%')
xs = [dd[d][1] / dd[d][0] for d in sorted(dd) if d != '2026-11-17']
t = dd['2026-11-17'][1] / dd['2026-11-17'][0]
print(f'  広告から: 11/3〜16 の日別 最小 {min(xs)*100:.2f}%・最大 {max(xs)*100:.2f}%・11/17 より低い日 {sum(x < t for x in xs)}/14')
w1 = [d for d in sorted(dd) if '2026-11-03' <= d <= '2026-11-09']; w2 = [d for d in sorted(dd) if '2026-11-10' <= d <= '2026-11-16']
for lab, ds in (('11/3〜9', w1), ('11/10〜16', w2), ('11/16〜17', ['2026-11-16', '2026-11-17'])):
    print(f'  広告から {lab}: {sum(dd[d][1] for d in ds)/sum(dd[d][0] for d in ds)*100:.2f}%')
# ⑤ 値段・在庫（11/18 09時台 graphql 直読）: 前からの7商品の値段 3,980（ブラシ4,980・4in1 6,980）・元値 9,980／12,890／15,980・全バリエーション販売中（4in1 シルバーパープルのみ 9/5 から在庫0）
# ⑥ 商品の記録（events・11/14〜）: グローブ・マルチクリップの作成と公開、11/15 に1商品削除のみ。前からの商品の記録なし（タイトル・説明の編集が残るかは未確認）
# ⑦ グローブ: Meta 11/17 2,715円・表示914・クリック31・LPV29・カート0・購入0／11/18 0〜8時台 2,659円・表示730・クリック25・LPV22・カート4・購入0
#    Shopify 入口ページ 11/17 34来訪・カート0／11/18 0〜8時台 25来訪・カート1・決済へ1・購入0。売上の行なし
