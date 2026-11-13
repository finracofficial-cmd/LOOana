# -*- coding: utf-8 -*-
"""11/14 08:3x 「CVRがここ数日悪化してない？なんでだ」
①終日の購入率（注文÷来訪）が偶然の範囲か（前の30日・祝日除く・noise_band と同じやり方）②どの段階で落ちたか ③商品の入れ替わり（入口ページの構成）で説明できる分と、同じページの中で落ちた分 ④流入元別"""
import json, csv, math, statistics as st, datetime
D = 'scripts/daily/ic1114/'
HOL = {'2026-09-21', '2026-09-22', '2026-09-23', '2026-10-12', '2026-11-03'}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'sess_daily_1001_1113.json'))['rows']}
OR = {r['date']: int(r['orders']) for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
days = sorted(d for d in SE if d in OR)
cvr = {d: OR[d] / SE[d][0] for d in days}
def band(d):
    base = [x for x in days if x < d and x not in HOL][-30:]
    lv = [math.log(cvr[x]) for x in base]; mu, sd = st.median(lv), st.stdev(lv); z = (math.log(cvr[d]) - mu) / sd
    return math.exp(mu), math.exp(mu - sd), math.exp(mu + sd), z, len(base)
print('■ 終日の購入率（注文÷来訪）と、前の30日のふだんの範囲（±σ）')
for d in days[-10:]:
    m, lo, hi, z, n = band(d)
    v = '範囲内' if abs(z) <= 1 else ('端（' + ('上' if z > 0 else '下') + '）' if abs(z) <= 2 else '偶然では起きにくい（' + ('上' if z > 0 else '下') + '）')
    print(f"  {d}: {cvr[d]*100:.2f}%（{OR[d]}注文／{SE[d][0]}来訪）・ふだん {lo*100:.2f}〜{hi*100:.2f}%（中央値 {m*100:.2f}%）→ {v}")
R3 = ['2026-11-11', '2026-11-12', '2026-11-13']; P14 = [d for d in days if '2026-10-28' <= d <= '2026-11-10']
def agg(ds): return [sum(SE[d][i] for d in ds) for i in range(4)] + [sum(OR[d] for d in ds)]
a, b = agg(R3), agg(P14)
print(f"■ 直近3日（11/11〜13）と前の14日（10/28〜11/10）")
for lab, f in [('購入率（注文÷来訪）', lambda x: x[4] / x[0]), ('カート投入率', lambda x: x[1] / x[0]), ('決済画面÷カート', lambda x: x[2] / x[1]), ('決済完了÷決済画面', lambda x: x[3] / x[2])]:
    print(f"  {lab}: {f(a)*100:.2f}% ← {f(b)*100:.2f}%（{(f(a)/f(b)-1)*100:+.0f}%）")
# 入口ページの構成
def lp(fn):
    out = {}
    for r in json.load(open(D + fn))['rows']: out[r[0]] = [int(x) for x in r[1:]]
    return out
L3, L14 = lp('lp_1111_1113.json'), lp('lp_1028_1110.json')
t3 = [sum(v[i] for v in L3.values()) for i in range(4)]; t14 = [sum(v[i] for v in L14.values()) for i in range(4)]
base_rate = t14[3] / t14[0]
exp = sum(v[0] * (L14[p][3] / L14[p][0] if p in L14 and L14[p][0] >= 100 else base_rate) for p, v in L3.items())
act = t3[3]
print(f"■ 入口ページの構成（上位ページ・決済完了÷来訪）: 直近3日 {act}/{t3[0]}＝{act/t3[0]*100:.2f}% ／ 前の14日の各ページの率で直近3日の来訪を数えると {exp:.0f}＝{exp/t3[0]*100:.2f}% ／ 前の14日 {t14[3]/t14[0]*100:.2f}%")
print(f"  → 前の14日からの差 {act/t3[0]*100 - t14[3]/t14[0]*100:+.2f}pt のうち、構成の入れ替わりで {exp/t3[0]*100 - t14[3]/t14[0]*100:+.2f}pt・同じページの中で {act/t3[0]*100 - exp/t3[0]*100:+.2f}pt")
NAME = {'nano-fine-fiber': 'クリーナー', 'vacuum-adsorption': 'W固定', 'washable-reusable-fuzz': 'ナノ', 'soft-silicone-car-squeegee': 'ワイパー', 'portable-small-wireless-mini-dust': '4-in-1', 'car-wash-cotton-thread': 'ブラシ',
        'soft-super-sports-shock': 'インソール', 'silicone-magnetic-door': 'ドア', 'winter-sweatwear': 'パンツ', 'waterproof-film-for-car': 'レインガード', 'small-portable-mini-sealing': 'ヒートシーラー', 'student-children-cushion': 'チェア', '/': 'トップ'}
def nmz(p):
    if p == '/': return 'トップ'
    for k, v in NAME.items():
        if k != '/' and k in p: return v
    return None
print('  ページ別（決済完了÷来訪・来訪の割合）: 直近3日 ← 前の14日')
for p in sorted(set(L3) | set(L14), key=lambda p: -(L3.get(p, [0])[0] + L14.get(p, [0])[0] / 5)):
    n = nmz(p)
    if not n: continue
    x, y = L3.get(p, [0, 0, 0, 0]), L14.get(p, [0, 0, 0, 0])
    f = lambda v: f"{v[3]/v[0]*100:.1f}%" if v[0] >= 50 else '—'
    print(f"    {n}: {f(x)}（来訪 {x[0]}・{x[0]/t3[0]*100:.0f}%）← {f(y)}（来訪 {y[0]}・{y[0]/t14[0]*100:.0f}%）")
# 流入元
RF = {}
for r in json.load(open(D + 'ref_daily_1028_1113.json'))['rows']:
    RF.setdefault(r[1], {})[r[0]] = [int(x) for x in r[2:]]
print('■ 流入元別（決済完了÷来訪・来訪の割合）: 直近3日 ← 前の14日')
for src in ('social', 'direct'):
    x = [sum(RF[src].get(d, [0]*4)[i] for d in R3) for i in range(4)]; y = [sum(RF[src].get(d, [0]*4)[i] for d in P14) for i in range(4)]
    print(f"  {src}: {x[3]/x[0]*100:.2f}%（来訪 {x[0]}・{x[0]/a[0]*100:.0f}%）← {y[3]/y[0]*100:.2f}%（来訪 {y[0]}・{y[0]/b[0]*100:.0f}%）・カート投入率 {x[1]/x[0]*100:.2f}% ← {y[1]/y[0]*100:.2f}%・決済完了÷決済画面 {x[3]/x[2]*100:.0f}% ← {y[3]/y[2]*100:.0f}%")
