# -*- coding: utf-8 -*-
"""11/22 「売れてる商品・そうでない商品がある。安定して毎日売れ続けさせるには」
商品ごとの利益（売上−原価−広告費）を日別に積み、①7日ごとの「柱」の本数と店の利益 ②10/1 以降に広告を始めた商品の当たり外れ ③当たりの利益が何週続いたか を出す。
入力: data/daily/*.csv（scripts/daily/w1121.py の積み直し関数）。期間 8/31〜11/21"""
import io, contextlib, os, collections, datetime
D0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(D0, '..', '..', '..', '..'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1121.py').read(), g)
WIN, agg, A, ALLD, MAP, CAT, ACCT = g['WIN'], g['agg'], g['A'], g['ALLD'], g['MAP'], g['CAT'], g['ACCT']
days = [d for d in ALLD if d >= '2026-08-31']; assert days[-1] == '2026-11-21' and len(days) == 83
PR = collections.defaultdict(dict); ADS = collections.defaultdict(dict); SL = collections.defaultdict(dict)
for d in days:
    WIN['life' + d] = [d]; N, DC, Q, K = agg([d], 'life' + d)
    for n in set(N) | set(MAP):
        a = A([d], n); s = N.get(n, 0); k = K.get(n, 0)
        if a or s: PR[n][d] = s - k - a; ADS[n][d] = a; SL[n][d] = s - k
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
blocks = [days[i:i + 7] for i in range(len(days) - 7 * 11 - 6 - 0, len(days), 7)][-11:] if False else [days[-7 * (k + 1):len(days) - 7 * k] for k in range(11, -1, -1)]
blocks = [b for b in blocks if len(b) == 7]
P('■ ① 7日ごと: 店の利益/日・広告費/日・「1万円/日以上」「2万円/日以上」の商品の本数・いちばん大きい商品とその割合（広告を出した商品だけ・カタログの広告費は店の利益に入れる）')
for b in blocks:
    pp = {n: sum(PR[n].get(d, 0) for d in b) for n in PR}; adv = {n: v for n, v in pp.items() if sum(ADS[n].get(d, 0) for d in b) > 0}
    store = sum(pp.values()) - CAT(b); top = max(adv, key=adv.get)
    P(f"  {b[0][5:]}〜{b[-1][5:]}: 利益 {store/7:,.0f}/日・広告費 {ACCT(b)/7:,.0f}/日・1万円以上 {sum(1 for v in adv.values() if v >= 70000)}本・2万円以上 {sum(1 for v in adv.values() if v >= 140000)}本・広告を出した商品 {len(adv)}本・最大 {top[:10]} {adv[top]/7:,.0f}/日（{adv[top]/store:.0%}）")
P('')
first = {n: min(d for d in ADS[n] if ADS[n][d] > 0) for n in ADS if any(v > 0 for v in ADS[n].values())}
all_first = {}
for n in first:   # 8/31 より前から広告が出ていたか（CSV 全体で見る）
    all_first[n] = next((d for d in ALLD if A([d], n) > 0), None)
new = sorted([n for n in first if all_first[n] >= '2026-10-01'], key=lambda n: first[n])
P(f'■ ② 10/1 以降に広告を始めた商品（{len(new)}本・出し直しの ノーズ v2 も含む）: 開始日・広告を出した日数・広告費・利益（開始〜11/21）・最初の7日の倍率')
hit = []
for n in new:
    ds = [d for d in days if d >= first[n]]; ad = sum(ADS[n].get(d, 0) for d in ds); pr = sum(PR[n].get(d, 0) for d in ds); act = sum(1 for d in ds if ADS[n].get(d, 0) > 0)
    w1 = ds[:7]; a1 = sum(ADS[n].get(d, 0) for d in w1); m1 = sum(SL[n].get(d, 0) for d in w1) / a1 if a1 else 0
    on = '配信中' if ADS[n].get('2026-11-21', 0) > 0 else '停止'
    P(f'  {n}: {first[n][5:]}〜・{act}日・広告費 {ad:,.0f}・利益 {pr:+,.0f}・最初の7日 {m1:.2f}・{on}')
    if pr >= 50000: hit.append(n)
tot = sum(sum(PR[n].get(d, 0) for d in days if d >= first[n]) for n in new)
P(f'  合計 {tot:+,.0f}円・利益 5万円以上（当たり） {len(hit)}本／{len(new)}本・赤字の商品の合計 {sum(min(0, sum(PR[n].get(d, 0) for d in days if d >= first[n])) for n in new):+,.0f}円')
P('')
P('■ ③ 当たりの商品の利益は何週続いたか（開始からの週ごとの 利益/日・倍率）')
for n in hit + ['ナノガラス脱毛パッド', '伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '快適マジックインソール', '4-in-1マルチクリーナー']:
    ds = [d for d in days if d >= first[n]]; out = []
    for i in range(0, len(ds), 7):
        w = ds[i:i + 7]
        if len(w) < 4: break
        a = sum(ADS[n].get(d, 0) for d in w); p = sum(PR[n].get(d, 0) for d in w); s = sum(SL[n].get(d, 0) for d in w)
        out.append(f'{p/len(w)/1000:+.0f}千（{s/a:.2f}）' if a else '停止')
    P(f"  {n}（{first[n][5:]}〜{'' if all_first[n] >= '2026-08-31' else '・それ以前から'}）: " + '・'.join(out))
open(os.path.join(D0, 'life_1122.txt'), 'w').write('\n'.join(L) + '\n')
