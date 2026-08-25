# -*- coding: utf-8 -*-
"""3D足臭 CR A/B — 「結局Aのほうが受注が取れているのでは」を検証する。"""
import math
from math import comb
# Meta実測（ad_name別）: date -> (cost, imp, clicks, Meta購入)
A = {'8/23': (9470, 1752, 35, 3), '8/24': (6805, 1154, 19, 2), '8/25(14:47)': (1994, 350, 5, 0)}
B = {'8/23': (852, 251, 2, 0),   '8/24': (3603, 1109, 17, 1), '8/25(14:47)': (3397, 1207, 17, 0)}
GPO = 3767          # 3D足臭の 粗利/注文（7日実測 48,973 ÷ 13注文）

print('■ 3D足臭 CR A/B（Bの投入 8/23〜・すべてMeta実測）')
print(f'  {"":<14}{"消化":>8}{"インプ":>8}{"クリック":>8}{"購入":>6}{"CPM":>8}{"CTR":>8}{"CPC":>7}{"CVR":>8}{"CPA":>9}')
tot = {}
for nm, D in [('A', A), ('B', B)]:
    for d, (c, i, k, p) in D.items():
        print(f'  {nm+" "+d:<14}{c:>8,}{i:>8,}{k:>8}{p:>6}{c/i*1000:>8,.0f}{k/i:>8.2%}'
              f'{(c/k if k else 0):>7,.0f}{(p/k if k else 0):>8.1%}{(f"{c/p:,.0f}" if p else "—"):>9}')
    c = sum(v[0] for v in D.values()); i = sum(v[1] for v in D.values())
    k = sum(v[2] for v in D.values()); p = sum(v[3] for v in D.values())
    tot[nm] = (c, i, k, p)
    print(f'  {nm+" 3日累計":<14}{c:>8,}{i:>8,}{k:>8}{p:>6}{c/i*1000:>8,.0f}{k/i:>8.2%}'
          f'{c/k:>7,.0f}{p/k:>8.1%}{(f"{c/p:,.0f}" if p else "—"):>9}\n')

(ca, ia, ka, pa), (cb, ib, kb, pb) = tot['A'], tot['B']
print('■ ★結論から: 受注はAのほうが取れている')
print(f'  A: 消化 {ca:,}円 → 購入 {pa}件 / CPA {ca/pa:,.0f}円 / 倍率 {GPO/(ca/pa):.2f}')
print(f'  B: 消化 {cb:,}円 → 購入 {pb}件 / CPA {cb/pb:,.0f}円 / 倍率 {GPO/(cb/pb):.2f}')
print(f'  分岐CPA {GPO:,}円 → **Aはほぼ分岐上、Bは分岐の{(cb/pb)/GPO:.1f}倍のコスト**')

print('\n■ Bの「CPMが安い」は本当だった。だが安いのはクリックまでで、そこで止まっている')
print(f'  CPM  A {ca/ia*1000:,.0f}円 vs B {cb/ib*1000:,.0f}円 → Bが {(cb/ib)/(ca/ia)-1:+.0%}')
print(f'  CTR  A {ka/ia:.2%} vs B {kb/ib:.2%} → Bが {(kb/ib)/(ka/ia)-1:+.0%}')
print(f'  CPC  A {ca/ka:,.0f}円 vs B {cb/kb:,.0f}円 → Bが {(cb/kb)/(ca/ka)-1:+.0%}（ここまではBの勝ち）')
print(f'  CVR  A {pa/ka:.1%} vs B {pb/kb:.1%} → Bが {(pb/kb)/(pa/ka)-1:+.0%}（ここで逆転する）')

# RPM/CPM
for nm, (c, i, k, p) in [('A', tot['A']), ('B', tot['B'])]:
    ctr = k/i; cvr = p/k; cpm = c/i*1000
    need = cpm/(GPO*1000)
    print(f'  {nm}: 実測CTR×CVR {ctr*cvr*10000:>5.2f}‱ vs 必要 {need*10000:>5.2f}‱ → RPM/CPM {(ctr*cvr)/need:.2f}')

print('\n■ ただし n が小さい。「Aが本当に強い」と言い切れるか（Fisherの正確確率検定）')
a1, a0, b1, b0 = pa, ka-pa, pb, kb-pb
n = a1+a0+b1+b0; r1 = a1+b1
def hp(x): return comb(ka, x)*comb(kb, r1-x)/comb(n, r1) if 0 <= r1-x <= kb else 0
obs = hp(a1); pval = sum(hp(x) for x in range(0, min(ka, r1)+1) if hp(x) <= obs + 1e-12)
print(f'  A {a1}/{ka} vs B {b1}/{kb} → 両側 p = {pval:.3f}')
print(f'  → {"有意ではない。偶然でこの差は普通に出る" if pval > 0.05 else "有意"}。**Bを「弱い」と断定はできない**')

print('\n■ それでも問題なのは「Metaが消化をBに寄せている」こと')
for d in ['8/23', '8/24', '8/25(14:47)']:
    sa, sb = A[d][0], B[d][0]
    print(f'  {d:<12} Bの消化シェア {sb/(sa+sb):>5.1%}（A {sa:,}円 / B {sb:,}円）')
print('  → 購入1件のBに、直近は消化の6割超が流れている。放置すると広告セット全体のCVRが薄まる')

print('\n■ 広告セット全体で見る（B投入の前後・Shopify実注文ベース）')
# 8/18-22 = B投入前 / 8/23-24 = B投入後（確定日） / 8/25 は部分日
PRE_C, PRE_O = 43334 - 10322 - 10408, 13 - 3 - 3
POST_C, POST_O = 10322 + 10408, 3 + 3
print(f'  B投入前 8/18-22: 消化 {PRE_C:,}円 / Shopify注文 {PRE_O}件 / CPA {PRE_C/PRE_O:,.0f}円 / 倍率 {GPO/(PRE_C/PRE_O):.2f}')
print(f'  B投入後 8/23-24: 消化 {POST_C:,}円 / Shopify注文 {POST_O}件 / CPA {POST_C/POST_O:,.0f}円 / 倍率 {GPO/(POST_C/POST_O):.2f}')
print(f'  （8/25は部分日・注文0・消化5,335円。全店CVRも当日−27.6%なので単独では読まない）')
print(f'  → 悪化はしているが {PRE_O}件 vs {POST_O}件。**単独では判定不能。宣言どおり8/30に広告セット全体で判定する**')
