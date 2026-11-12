# -*- coding: utf-8 -*-
"""11/12(木) 11:5x 「来訪が少ないのは広告費を掛けてないから？」
0〜10時台（確定した11時間）で、来訪 = 広告費 × (クリック÷広告費) × (来訪÷クリック) に分けて、今日と過去7日（11/5〜11/11）を比べる。
入力: meta_hour_0011_raw.txt（Meta 時間別・fresh）／cvr_hour_1148_raw.json の b（Shopify 0〜10時台の来訪）／sess_ref_0010_raw.json（流入元別）／data/budget-snapshots.csv
今日の10時台の広告費は取得時点（11:5x）でまだ増える可能性がある。日中の数字なので判定・予算提案には使わない。"""
import os, json, csv, math, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
M = collections.defaultdict(lambda: [0, 0, 0, 0])   # date -> cost, imp, link_clicks, LPV（0〜10時台）
Hc = {}
for l in open(D + 'meta_hour_0011_raw.txt'):
    if not l.startswith('2026-'): continue
    d, hb, c, i, k, lp, pu = next(csv.reader([l.strip()]))
    h = int(hb[:2]); Hc[(d, h)] = [int(c), int(i), int(k), int(lp)]
    if h <= 10:
        for j, v in enumerate((c, i, k, lp)): M[d][j] += int(v)
b = json.load(open(D + 'cvr_hour_1148_raw.json'))['b']; assert 'hour_of_day <= 10' in b['query']
S = {r[0]: int(r[1]) for r in b['rows']}
ref = json.load(open(D + 'sess_ref_0010_raw.json')); RF = collections.defaultdict(dict)
for d, s, n in ref['rows']: RF[d][s or '(空)'] = int(n)
T = '2026-11-12'; P7 = sorted(d for d in M if d < T); assert len(P7) == 7 and P7[0] == '2026-11-05'
for d in P7 + [T]: assert sum(RF[d].values()) == S[d], (d, sum(RF[d].values()), S[d])   # 流入元別の合計 = 来訪の合計
# 予算（その日の最後のスナップショットの合計）
BS = collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open(R + 'data/budget-snapshots.csv')): BS[r['snapshot_date']][(r['campaign'], r['adset'])] += int(r['daily_budget'])
def budget(d):
    ks = sorted(k for k in BS if k[:10] == d); return (sum(BS[ks[-1]].values()), len(BS[ks[-1]]), ks[-1]) if ks else None
print('■ 0〜10時台・日別')
print('  日付   来訪  広告費  クリック  1クリック円  CPM   CTR%  来訪÷クリック  social  direct  ｜その日の最後の予算合計')
for d in P7 + [T]:
    c, i, k, lp = M[d]; bg = budget(d)
    print(f"  {d[5:]}  {S[d]:5,} {c:7,} {k:6,}   {c/k:6.1f}  {c/i*1000:6,.0f}  {k/i*100:.2f}   {S[d]/k:.2f}     {RF[d].get('social',0):4}   {RF[d].get('direct',0):4}  ｜{'—' if not bg else f'{bg[0]:,}（{bg[1]}セット・{bg[2]}）'}")
avg = lambda f: sum(f(d) for d in P7) / 7
def line(lab, f, fm):
    t = f(T); xs = [f(d) for d in P7]
    print(f"  {lab}: 今日 {fm.format(t)} ／ 過去7日 平均{fm.format(sum(xs)/7)}・中央値{fm.format(st.median(xs))}（{fm.format(min(xs))}〜{fm.format(max(xs))}）・今日より低い日 {sum(x < t for x in xs)}/7")
print('\n■ 今日と過去7日')
line('来訪', lambda d: S[d], '{:,.0f}'); line('広告費', lambda d: M[d][0], '{:,.0f}'); line('クリック', lambda d: M[d][2], '{:,.0f}')
line('1クリックあたり広告費', lambda d: M[d][0] / M[d][2], '{:.1f}'); line('CPM', lambda d: M[d][0] / M[d][1] * 1000, '{:,.0f}'); line('CTR%', lambda d: M[d][2] / M[d][1] * 100, '{:.2f}')
line('来訪÷クリック', lambda d: S[d] / M[d][2], '{:.2f}')
def decomp(lab, days):
    n = len(days); s0 = sum(S[d] for d in days) / n; c0 = sum(M[d][0] for d in days) / n; k0 = sum(M[d][2] for d in days) / n; i0 = sum(M[d][1] for d in days) / n
    s1, c1, k1, i1 = S[T], M[T][0], M[T][2], M[T][1]
    r = [c1 / c0, (k1 / c1) / (k0 / c0), (s1 / k1) / (s0 / k0)]; tot = s1 / s0
    assert abs(r[0] * r[1] * r[2] - tot) < 1e-9
    L = [math.log(x) for x in r]; LT = math.log(tot)
    print(f"  {lab}: 来訪 {s0:,.0f} → {s1:,}（{(tot-1)*100:+.0f}%）＝ 広告費 {(r[0]-1)*100:+.0f}% × クリック÷広告費 {(r[1]-1)*100:+.0f}% × 来訪÷クリック {(r[2]-1)*100:+.0f}%")
    print(f"      差 {s1-s0:+,.0f} 来訪の内訳（対数で按分）: 広告費 {(s1-s0)*L[0]/LT:+,.0f}／1クリックの値段 {(s1-s0)*L[1]/LT:+,.0f}／来訪÷クリック {(s1-s0)*L[2]/LT:+,.0f}")
    cp = [(c1 / i1) / (c0 / i0), (k1 / i1) / (k0 / i0)]
    print(f"      1クリックの値段 {c0/k0:.1f} → {c1/k1:.1f}円（{(c1/k1/(c0/k0)-1)*100:+.0f}%）＝ CPM {c0/i0*1000:,.0f} → {c1/i1*1000:,.0f}（{(cp[0]-1)*100:+.0f}%）÷ CTR {k0/i0*100:.2f} → {k1/i1*100:.2f}%（{(cp[1]-1)*100:+.0f}%）")
    print(f"      もし1クリックの値段が比較期間と同じだったら、今日の広告費 {c1:,}円でクリック {c1/(c0/k0):,.0f}（実際 {k1:,}）")
print('\n■ 分解（今日 vs 比較期間の1日平均）')
decomp('過去7日（11/5〜11/11）', P7); decomp('11/5〜11/9（5日）', P7[:5]); decomp('11/10〜11/11（2日）', P7[5:]); decomp('前日（11/11）', P7[6:])
print('\n■ 3日ずつ（0〜10時台の1日平均）')
for lab, ds in [('11/5〜11/9', P7[:5]), ('11/10〜11/12', P7[5:] + [T])]:
    n = len(ds); print(f"  {lab}: 来訪 {sum(S[d] for d in ds)/n:,.0f}・広告費 {sum(M[d][0] for d in ds)/n:,.0f}・クリック {sum(M[d][2] for d in ds)/n:,.0f}・1クリック {sum(M[d][0] for d in ds)/sum(M[d][2] for d in ds):.1f}円・CPM {sum(M[d][0] for d in ds)/sum(M[d][1] for d in ds)*1000:,.0f}・CTR {sum(M[d][2] for d in ds)/sum(M[d][1] for d in ds)*100:.2f}%")
print('\n■ 今日の時間別 広告費（昨日→今日）: ' + ' '.join(f"{h}時 {Hc[(P7[-1],h)][0]:,}→{Hc[(T,h)][0]:,}" for h in range(12)))
print('  ※今日の11時台は途中。10時台も取得時点でまだ増える可能性あり')
