# -*- coding: utf-8 -*-
"""11/19 11:5x 「こんなに悪い理由を分析してくれよ！」: 0〜10時台を過去21日（10/29〜11/18）の同じ時刻と比べ、
注文÷広告費 ＝ 表示÷広告費（1/CPM）× クリック率 × 着地÷クリック × カート÷着地（Meta）× 注文÷カート に分ける。日中の数字なので予算の判断には使わない"""
import statistics as st
O = {}; M = {}
for l in open('raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == 'O': O[p[1]] = int(p[2])
    elif p[0] == 'M': M[p[1]] = [None if x == 'null' else int(x) for x in p[2:]]
T = '2026-11-19'; past = [d for d in sorted(O) if d < T]; assert len(past) == 21
def met(d):
    c, i, k, lpv, atc, pu = M[d]; o = O[d]
    return {'注文': o, '広告費': c, '注文÷広告費1万円': o / c * 1e4, 'CPM': c / i * 1000, 'クリック率%': (k / i * 100) if k and d not in ('2026-11-16', '2026-11-17', '2026-11-18') else None,
            '着地÷広告費1万円': lpv / c * 1e4, 'カート÷着地%（Meta）': atc / lpv * 100, '注文÷カート%': o / atc * 100, '注文÷着地%': o / lpv * 100}
TM = met(T)
print('■ 0〜10時台・今日 と 過去21日（10/29〜11/18）の同じ時刻')
for k, v in TM.items():
    xs = [met(d)[k] for d in past if met(d)[k] is not None]
    lo = sum(x < v for x in xs); md = st.median(xs)
    out = '範囲の外（下）' if v < min(xs) else ('範囲の外（上）' if v > max(xs) else '範囲内')
    print(f'  {k}: 今日 {v:,.2f}・過去 {min(xs):,.2f}〜{max(xs):,.2f}（中央値 {md:,.2f}・{len(xs)}日）・今日より低い日 {lo}/{len(xs)} → {out}')
print('■ 直近7日の流れ（注文÷広告費1万円・CPM・カート÷着地・注文÷カート）')
for d in past[-7:] + [T]:
    m = met(d); print(f"  {d[5:]}: {m['注文']}件・{m['注文÷広告費1万円']:.2f}・CPM {m['CPM']:,.0f}・カート {m['カート÷着地%（Meta）']:.1f}%・注文÷カート {m['注文÷カート%']:.0f}%")
# ---- CPM が高いのは 新しく出した3本（11/18 の0〜10時台にはなかった）の分か ----
import collections
C = collections.defaultdict(dict)
for l in open('raw.txt'):
    if l.startswith('C,'): p = l.strip().split(','); C[p[1]][p[2]] = [int(x) for x in p[3:]]
NEW = ('ディスペンサーv2', 'ポータブルヒートシーラーv2', '高見えレザーヘッドレストフックv5')
print('■ キャンペーン別（0〜10時台）: 新しく出した3本と、それ以外')
for d in ('2026-11-18', '2026-11-19'):
    tc = sum(v[0] for v in C[d].values()); ti = sum(v[1] for v in C[d].values())
    nc = sum(v[0] for k, v in C[d].items() if k in NEW); ni = sum(v[1] for k, v in C[d].items() if k in NEW); npu = sum(v[4] for k, v in C[d].items() if k in NEW)
    print(f'  {d[5:]}: 全体 広告費 {tc:,}・CPM {tc/ti*1000:,.0f} ｜ 新しい3本 {nc:,}（{nc/tc:.0%}）・CPM {nc/ni*1000 if ni else 0:,.0f}・Meta 購入 {npu} ｜ それ以外 CPM {(tc-nc)/(ti-ni)*1000:,.0f}')
past_cpm = sorted(met(d)['CPM'] for d in past)
print(f'  過去21日の全体 CPM: {past_cpm[0]:,.0f}〜{past_cpm[-1]:,.0f}（中央値 {st.median(past_cpm):,.0f}）')
print('■ 前からのキャンペーンの CPM（0〜10時台）11/18 → 11/19')
for k in sorted(C['2026-11-19'], key=lambda k: -C['2026-11-19'][k][0]):
    if k in NEW or k not in C['2026-11-18']: continue
    a, b = C['2026-11-18'][k], C['2026-11-19'][k]
    print(f'  {k}: {a[0]/a[1]*1000:,.0f} → {b[0]/b[1]*1000:,.0f}（{b[0]/b[1]/(a[0]/a[1])-1:+.0%}）・Meta 購入 {a[4]} → {b[4]}')
