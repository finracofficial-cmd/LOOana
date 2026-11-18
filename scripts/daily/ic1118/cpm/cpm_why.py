# -*- coding: utf-8 -*-
"""11/18 「CPMの大小は需要の大小？ターゲットが広い商品ほど安い？」
商品ごとの CPM を ①誰に（年齢×性別）②どこで（配置）出たかの構成で決まる分と、③同じ層・同じ配置の中での値段の差 に分ける（10/19〜11/17）。
期待 CPM＝Σ その商品の表示の割合 × 店全体のその層の CPM。実際÷期待＝同じ層の中での高さ
あわせて、週ごとの広告費を増やしたときに CPM が上がるか（同じ商品の中・meta_weekly_raw）"""
import collections, math
num = lambda x: 0 if x == 'null' else float(x)
MAIN = ['ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '快適マジックインソール', '4-in-1マルチクリーナー', '伸縮ガラスクリーナー', '姿勢サポートチェア', 'コードレスダブルミスト加湿器', 'ワイド水切りワイパー', 'ポータブルヒートシーラー', 'マグネットドアクッション', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', '高見えレザーヘッドレストフック', '3WAY着る電気ブランケット']
def load(fn, nk):
    D = collections.defaultdict(lambda: [0.0] * 4)
    for l in open(fn):
        if l[0] == '#': continue
        p = l.strip().split(','); c = p[0]; seg = '|'.join(p[1:1 + nk]); v = [num(x) for x in p[1 + nk:]]
        for i in range(4): D[(c, seg)][i] += v[i]
    return D
for fn, nk, lab in (('agegender_raw.txt', 2, '年齢×性別'), ('placement_raw.txt', 2, '配置')):
    D = load(fn, nk)
    S = collections.defaultdict(lambda: [0.0, 0.0])
    for (c, s), v in D.items(): S[s][0] += v[0]; S[s][1] += v[1]
    tot = sum(v[0] for v in S.values()) / sum(v[1] for v in S.values()) * 1000
    print(f'■ {lab}（店全体の CPM {tot:,.0f}）。層ごとの CPM: ' + '・'.join(f'{s} {v[0]/v[1]*1000:,.0f}' for s, v in sorted(S.items(), key=lambda x: -x[1][0])[:10]))
    print(f'  商品: 実際の CPM ／ 層の構成だけで決まる CPM（{lab}）／ 同じ層の中での高さ')
    for c in MAIN:
        rows = [(s, v) for (cc, s), v in D.items() if cc == c]
        cost = sum(v[0] for s, v in rows); imp = sum(v[1] for s, v in rows)
        if imp == 0: continue
        exp = sum(v[1] / imp * S[s][0] / S[s][1] * 1000 for s, v in rows)
        top = sorted(rows, key=lambda x: -x[1][1])[:2]
        print(f'  {c[:14]:<14} {cost/imp*1000:>6,.0f} ／ {exp:>6,.0f}（店比 {exp/tot-1:+.0%}）／ {cost/imp*1000/exp-1:+.0%}  表示が多い層: ' + '・'.join(f'{s} {v[1]/imp:.0%}' for s, v in top))
# 同じ商品の中で、週の広告費と CPM（量を増やすと高くなるか）
def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0] * len(xs)
    for k, i in enumerate(o): r[i] = k
    return r
def rho(a, b):
    ra, rb = rank(a), rank(b); n = len(a); m = (n - 1) / 2
    return sum((x - m) * (y - m) for x, y in zip(ra, rb)) / (sum((x - m) ** 2 for x in ra) or 1)
W = collections.defaultdict(lambda: [0.0, 0.0])
for l in open('../life/meta_weekly_raw.txt'):
    if l[0] == '#': continue
    w, c, cost, imp, *_ = l.strip().split(',')
    W[(c, w)][0] += num(cost); W[(c, w)][1] += num(imp)
print('■ 同じ商品の中で、週の広告費が多い週ほど CPM が高いか（6/29〜11/15・広告費3万円以上の週が5週以上）')
for c in sorted({c for c, w in W}):
    ws = [(v[0], v[0] / v[1] * 1000) for (cc, w), v in W.items() if cc == c and v[0] >= 30000]
    if len(ws) >= 5:
        xs, ys = zip(*ws)
        print(f'  {c[:16]:<16} {len(ws):>2}週・広告費 {min(xs)/1000:,.0f}〜{max(xs)/1000:,.0f}千円・CPM {min(ys):,.0f}〜{max(ys):,.0f}・順位相関 {rho(list(xs), list(ys)):+.2f}')
