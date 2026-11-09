# -*- coding: utf-8 -*-
"""11/10 01時台: クリーナー・車載・ドア・インソールの広告セット別（Meta計上・10/27-11/9）と商品別倍率（Shopify実測・CSV）"""
import io, contextlib, collections, json, sys
RAW = sys.argv[1]
rows = [l.strip().replace('null', '0').split(',') for l in json.load(open(RAW))['data']['data'].split('\n')[1:] if l.strip()]
A = collections.defaultdict(lambda: collections.defaultdict(lambda: [0]*7))
for d, c, s, *v in rows:
    A[(c, s)][d] = [int(x) for x in v]
assert len(rows) == 85
def per(key, days):
    t = [sum(A[key][d][i] for d in days) for i in range(7)]; return t
DAYS = sorted({r[0] for r in rows})
for c, s in sorted(A):
    print(f'== {c} / {s}')
    for lab, days in [('14日10/27-11/9', DAYS), ('7日11/3-9', DAYS[-7:]), ('3日11/7-9', DAYS[-3:]), ('11/8', ['2026-11-08']), ('11/9', ['2026-11-09'])]:
        cost, imp, clk, lpv, atc, pu, val = per((c, s), days)
        if not cost: continue
        print(f'  {lab}: 広告{cost:,} 購入{pu} CPA{(cost/pu if pu else 0):,.0f} ROAS{val/cost:.2f} CTR{clk/imp*100:.2f}% CPM{cost/imp*1000:,.0f} カート/LPV{atc/lpv*100 if lpv else 0:.1f}%')
    print('   日別CPA:', ' '.join(f"{d[5:]}:{A[(c,s)][d][0]//A[(c,s)][d][5] if A[(c,s)][d][5] else '-'}" for d in DAYS if A[(c, s)][d][0]))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1109.py').read(), g)
WIN, agg, Af, ALLD = g['WIN'], g['agg'], g['A'], g['ALLD']
def W(days):
    key = 'y' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
print('\n商品別（Shopify実測・倍率=(実売−原価)÷広告費）')
for n in ['伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'マグネットドアクッション', '快適マジックインソール']:
    out = []
    for lab, days in [('30日', ALLD[-30:]), ('14日', ALLD[-14:]), ('7日', ALLD[-7:]), ('3日', ALLD[-3:])]:
        N, Q, K = W(days); a = Af(days, n); out.append(f"{lab} {(N.get(n,0)-K.get(n,0))/a:.2f}（{Q.get(n,0)}個・広告{a:,.0f}・利益{N.get(n,0)-K.get(n,0)-a:+,.0f}）")
    print(n, ' / '.join(out))
    dd = []
    for d in ALLD[-14:]:
        N, Q, K = W([d]); a = Af([d], n)
        if a: dd.append(f"{d[5:]}:{(N.get(n,0)-K.get(n,0))/a:.2f}({Q.get(n,0)})")
    print('   日別:', ' '.join(dd))
# --- 追加: インソール 11/4-9（新CR後6日）と、クリーナー広告セット別「1日の広告費の大きさ別」CPA ---
N, Q, K = W(ALLD[-6:]); n = '快適マジックインソール'; a = Af(ALLD[-6:], n)
print('\nインソール 11/4-9（6日）', f"倍率{(N[n]-K[n])/a:.2f} 粗利{N[n]-K[n]:,} 広告{a:,.0f} 利益{N[n]-K[n]-a:+,.0f} {Q[n]}個", ALLD[-6])
for s in ['伸縮ガラスクリーナー', '伸縮ガラスクリーナー sabu']:
    b = collections.defaultdict(lambda: [0, 0, 0])
    for d, v in A[('伸縮ガラスクリーナー', s)].items():
        k = '〜14,999' if v[0] < 15000 else ('15,000〜19,999' if v[0] < 20000 else '20,000〜')
        b[k][0] += v[0]; b[k][1] += v[5]; b[k][2] += 1
    print(s, {k: f'{x[2]}日・広告{x[0]:,}・購入{x[1]}・CPA{x[0]//x[1]:,}' for k, x in sorted(b.items())})
w = {'主力': 0, 'sabu': 0}
for d in DAYS:
    m = A[('伸縮ガラスクリーナー', '伸縮ガラスクリーナー')][d]; sb = A[('伸縮ガラスクリーナー', '伸縮ガラスクリーナー sabu')][d]
    w['主力' if m[0] / m[5] < sb[0] / sb[5] else 'sabu'] += 1
print('14日でCPAが低かった日数', w)
