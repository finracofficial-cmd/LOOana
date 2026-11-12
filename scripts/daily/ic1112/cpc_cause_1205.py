# -*- coding: utf-8 -*-
"""11/12(木) 12:0x 「何が原因だ？対処はできないってこと？」
1クリックの値段（広告費÷リンククリック）が 11/5〜11/9 → 11/10〜11/11 で上がった理由を、終日の数字で4つの切り口から確認する。
 ①過去30日の中での位置（同じ曜日どうし）②広告セットごとの上昇と配分の変化 ③配置別 ④予算を動かした広告セットと動かしていない広告セット
入力（すべて Meta data_query fresh・11/12 12:0x取得）: cpc_acct_daily_1013_1111_raw.txt／cpc_adset_daily_1022_1111_raw.txt／cpc_placement_daily_1105_1111_raw.txt、data/budget-snapshots.csv
原因の断定はしない。データで言えること／言えないことを分けて出す。"""
import os, csv, collections, statistics as st, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
def rd(fn): return [next(csv.reader([l.strip()])) for l in open(D + fn) if l.strip().startswith('2026-')]
iv = lambda x: 0 if x in ('null', '') else int(x)
P1 = ['2026-11-05', '2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09']; P2 = ['2026-11-10', '2026-11-11']
WD = '月火水木金土日'; wd = lambda d: WD[dt.date.fromisoformat(d).weekday()]
HOL = {'2026-11-03'}   # 文化の日
# ---------- ① 過去30日 ----------
AC = {d: [iv(c), iv(i), iv(r), iv(k)] for d, c, i, r, k in rd('cpc_acct_daily_1013_1111_raw.txt')}; assert len(AC) == 30
cpc = lambda d: AC[d][0] / AC[d][3]; cpm = lambda d: AC[d][0] / AC[d][1] * 1000; ctr = lambda d: AC[d][3] / AC[d][1] * 100
print('■① 過去30日・アカウント合計（終日）: 日付(曜) 1クリック円／CPM／CTR%')
for d in sorted(AC): print(f"  {d[5:]}({wd(d)}{'祝' if d in HOL else ''}) {cpc(d):5.1f}／{cpm(d):5,.0f}／{ctr(d):.2f}" + ('  ←' if d in P1 + P2 else ''))
base = [d for d in sorted(AC) if d < P1[0]]
print(f"  10/13〜11/4（{len(base)}日）の1クリック: 中央値 {st.median(cpc(d) for d in base):.1f}円（{min(cpc(d) for d in base):.1f}〜{max(cpc(d) for d in base):.1f}）／11/5〜11/9 {sum(AC[d][0] for d in P1)/sum(AC[d][3] for d in P1):.1f}円／11/10〜11/11 {sum(AC[d][0] for d in P2)/sum(AC[d][3] for d in P2):.1f}円")
print(f"  10/13〜11/4 で 90円以上の日: {[d[5:] for d in base if cpc(d) >= 90]}・80円未満の日: {[d[5:] for d in base if cpc(d) < 80]}")
def same_wd(ds):   # 同じ曜日（祝日除く）の過去平均との比
    out = []
    for d in ds:
        ref = [cpc(x) for x in base if wd(x) == wd(d) and x not in HOL]; out.append((d, cpc(d), sum(ref) / len(ref), len(ref)))
    return out
for lab, ds in [('11/5〜11/9', P1), ('11/10〜11/11', P2)]:
    o = same_wd(ds); print(f"  {lab} 同じ曜日の過去平均（10/13〜11/4・祝日除く）との比: " + '・'.join(f"{d[5:]}({wd(d)}) {a:.1f} vs {b:.1f}（{(a/b-1)*100:+.0f}%・{n}日）" for d, a, b, n in o) + f" ／平均 {(sum(a/b for _, a, b, _ in o)/len(o)-1)*100:+.0f}%")
# ---------- ② 広告セット別 ----------
A = collections.defaultdict(dict)
for d, cp, s, c, i, r, k in rd('cpc_adset_daily_1022_1111_raw.txt'): A[d][s] = [iv(c), iv(i), iv(k), iv(r)]
for d in sorted(A):   # アカウント合計と一致するか（10/22〜）
    assert abs(sum(v[0] for v in A[d].values()) - AC[d][0]) <= 20, (d, sum(v[0] for v in A[d].values()), AC[d][0])
    assert sum(v[2] for v in A[d].values()) == AC[d][3], d
def agg(ds):
    t = collections.defaultdict(lambda: [0, 0, 0])
    for d in ds:
        for s, v in A[d].items(): t[s][0] += v[0]; t[s][1] += v[1]; t[s][2] += v[2]
    return {s: v for s, v in t.items() if v[0] > 0}
a, b = agg(P1), agg(P2)
T = lambda t: [sum(v[j] for v in t.values()) for j in range(3)]
(ca, ia, ka), (cb, ib, kb) = T(a), T(b)
print(f"\n■② 広告セット別（終日）11/5〜11/9 → 11/10〜11/11\n  全体: 1クリック {ca/ka:.1f} → {cb/kb:.1f}円（{(cb/kb/(ca/ka)-1)*100:+.0f}%）・CPM {ca/ia*1000:,.0f} → {cb/ib*1000:,.0f}（{(cb/ib/(ca/ia)-1)*100:+.0f}%）・CTR {ka/ia*100:.2f} → {kb/ib*100:.2f}%（{(kb/ib/(ka/ia)-1)*100:+.0f}%）")
common = [s for s in b if s in a and a[s][2] > 0 and b[s][2] > 0 and a[s][0] >= 20000 and b[s][0] >= 10000]
kmix = sum((b[s][0] / (a[s][0] / a[s][2])) if s in common else b[s][2] for s in b)   # 共通の広告セットは前の期間の単価、それ以外は実際のクリック
print(f"  各広告セットの1クリックの値段が前の期間のままで、配分だけ今の形だった場合: {cb/kmix:.1f}円 ＝ 配分の変化ぶん {cb/kmix-ca/ka:+.1f}円／広告セットごとの上昇ぶん {cb/kb-cb/kmix:+.1f}円（合計 {cb/kb-ca/ka:+.1f}円）")
print('  広告セット: 1クリック円（前→後・変化）｜CPM（前→後）｜CTR%（前→後）｜後の期間の広告費')
up = [0, 0, 0]
for s in sorted(common, key=lambda s: -b[s][0]):
    x, y = a[s], b[s]; r = [(y[0] / y[2]) / (x[0] / x[2]), (y[0] / y[1]) / (x[0] / x[1]), (y[2] / y[1]) / (x[2] / x[1])]
    up[0] += r[0] > 1; up[1] += r[1] > 1; up[2] += r[2] < 1
    print(f"  {s}: {x[0]/x[2]:.0f}→{y[0]/y[2]:.0f}（{(r[0]-1)*100:+.0f}%）｜{x[0]/x[1]*1000:,.0f}→{y[0]/y[1]*1000:,.0f}（{(r[1]-1)*100:+.0f}%）｜{x[2]/x[1]*100:.2f}→{y[2]/y[1]*100:.2f}（{(r[2]-1)*100:+.0f}%）｜{y[0]:,}")
print(f"  {len(common)}セット中: 1クリックが上がった {up[0]}・CPMが上がった {up[1]}・CTRが下がった {up[2]}")
gone = sorted((s for s in a if s not in b or b[s][0] < 10000), key=lambda s: -a[s][0]); new = sorted((s for s in b if s not in common), key=lambda s: -b[s][0])
print('  前の期間だけ（止めた／ほぼ止まった）: ' + '・'.join(f"{s} {a[s][0]:,}円・{a[s][0]/a[s][2]:.0f}円/クリック" for s in gone if a[s][2]))
print('  後の期間だけ／少額: ' + '・'.join(f"{s} {b[s][0]:,}円" + (f"・{b[s][0]/b[s][2]:.0f}円/クリック" if b[s][2] else '') for s in new))
# 3週間ずっと出ている広告セットだけで、同じ量のクリック／表示を買う値段（固定バスケット）
days = sorted(A); fixed = [s for s in A[days[0]] if all(A[d].get(s, [0])[0] >= 5000 for d in days)]
qk = {s: sum(A[d][s][2] for d in days) / len(days) for s in fixed}; qi = {s: sum(A[d][s][1] for d in days) / len(days) for s in fixed}
fx_cpc = lambda d: sum(qk[s] * A[d][s][0] / A[d][s][2] for s in fixed) / sum(qk.values()); fx_cpm = lambda d: sum(qi[s] * A[d][s][0] / A[d][s][1] for s in fixed) / sum(qi.values()) * 1000
print(f"\n  ■ 10/22〜11/11 の21日ずっと出ている{len(fixed)}セット（{'・'.join(fixed)}）で、毎日同じ量を買った場合の値段")
print('   1クリック円: ' + ' '.join(f"{d[5:]}({wd(d)}) {fx_cpc(d):.0f}" for d in days))
print('   CPM: ' + ' '.join(f"{d[5:]} {fx_cpm(d):,.0f}" for d in days))
b0 = [d for d in days if d < P1[0]]
for lab, f, fm in [('1クリック円', fx_cpc, '{:.1f}'), ('CPM', fx_cpm, '{:,.0f}')]:
    m0 = st.mean(f(d) for d in b0); m1 = st.mean(f(d) for d in P1); m2 = st.mean(f(d) for d in P2)
    print(f"   {lab}: 10/22〜11/4 平均 {fm.format(m0)}（{fm.format(min(f(d) for d in b0))}〜{fm.format(max(f(d) for d in b0))}）／11/5〜11/9 {fm.format(m1)}（{(m1/m0-1)*100:+.0f}%）／11/10〜11/11 {fm.format(m2)}（{(m2/m0-1)*100:+.0f}%）・11/10〜11より高い日 {sum(f(d) > m2 for d in b0)}/{len(b0)}")
# 新しく出した商品の、出してからの日数とCTR・CPM
print('\n  ■ 出してからの日数と CTR%／CPM／1クリック円（広告費3,000円以上の日）')
for s in ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', 'マグネットドアクッション', '伸縮ワックス洗車ブラシ']:
    ds = [d for d in days if A[d].get(s, [0])[0] >= 3000]
    print(f"   {s}（{ds[0][5:]}〜）: " + ' '.join(f"{d[5:]} {A[d][s][2]/A[d][s][1]*100:.1f}/{A[d][s][0]/A[d][s][1]*1000:,.0f}/{A[d][s][0]/A[d][s][2]:.0f}" for d in ds))
# ---------- ③ 配置別 ----------
PL = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for d, pp, pos, c, i, k in rd('cpc_placement_daily_1105_1111_raw.txt'):
    for j, v in enumerate((c, i, k)): PL['P1' if d in P1 else 'P2'][f'{pp}/{pos}'][j] += iv(v)
for d in P1 + P2: assert abs(sum(iv(r[3]) for r in rd('cpc_placement_daily_1105_1111_raw.txt') if r[0] == d) - AC[d][0]) <= 20, d
print('\n■③ 配置別（終日）11/5〜11/9 → 11/10〜11/11: 広告費の割合%｜CPM｜CTR%｜1クリック円')
t1 = sum(v[0] for v in PL['P1'].values()); t2 = sum(v[0] for v in PL['P2'].values()); nup = 0; big = []
for k_ in sorted(PL['P2'], key=lambda k_: -PL['P2'][k_][0]):
    x, y = PL['P1'][k_], PL['P2'][k_]
    if y[0] / t2 < 0.02: continue
    big.append(k_); nup += (y[0] / y[1]) > (x[0] / x[1])
    print(f"  {k_}: {x[0]/t1*100:.0f}→{y[0]/t2*100:.0f}｜{x[0]/x[1]*1000:,.0f}→{y[0]/y[1]*1000:,.0f}（{((y[0]/y[1])/(x[0]/x[1])-1)*100:+.0f}%）｜{x[2]/x[1]*100:.2f}→{y[2]/y[1]*100:.2f}｜{x[0]/x[2]:.0f}→{y[0]/y[2]:.0f}（{((y[0]/y[2])/(x[0]/x[2])-1)*100:+.0f}%）")
kmixp = sum(PL['P2'][k_][0] / (PL['P1'][k_][0] / PL['P1'][k_][2]) for k_ in big)
print(f"  広告費2%以上の{len(big)}配置すべてでCPMが上がった: {nup}/{len(big)}・配置の割合だけ変わった場合の1クリック {sum(PL['P2'][k_][0] for k_ in big)/kmixp:.1f}円（前の期間 {sum(PL['P1'][k_][0] for k_ in big)/sum(PL['P1'][k_][2] for k_ in big):.1f}・実際 {sum(PL['P2'][k_][0] for k_ in big)/sum(PL['P2'][k_][2] for k_ in big):.1f}）")
# ---------- ④ 予算を動かしたかどうか ----------
BS = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/budget-snapshots.csv')): BS[r['snapshot_date']][r['adset']] = int(r['daily_budget'])
def last(d):
    ks = sorted(k for k in BS if k[:10] == d); return BS[ks[-1]] if ks else {}
print('\n■④ 予算（その日の最後の記録）と1クリックの変化')
grp = {'動かしていない': [], '下げた': [], '上げた': []}
for s in sorted(common, key=lambda s: -b[s][0]):
    bud = [last(d).get(s) for d in ['2026-11-04'] + P1 + P2]
    b1 = [x for x in bud[:6] if x]; b2 = [x for x in bud[6:] if x]
    if not b1 or not b2: continue
    m1, m2 = st.mean(b1), st.mean(b2); g = '動かしていない' if len(set(x for x in bud if x)) == 1 else ('下げた' if m2 < m1 else '上げた')
    r = (b[s][0] / b[s][2]) / (a[s][0] / a[s][2]); grp[g].append((s, r, a[s], b[s]))
    print(f"  {s}: 予算 {'→'.join('—' if x is None else f'{x//1000}' for x in bud)}（千円・11/4〜11/11）｜{g}｜1クリック {(r-1)*100:+.0f}%")
for g, xs in grp.items():
    if not xs: continue
    c1 = sum(x[2][0] for x in xs); k1 = sum(x[2][2] for x in xs); c2 = sum(x[3][0] for x in xs); k2 = sum(x[3][2] for x in xs); i1 = sum(x[2][1] for x in xs); i2 = sum(x[3][1] for x in xs)
    print(f"  【{g}】{len(xs)}セット: 1クリック {c1/k1:.1f}→{c2/k2:.1f}円（{(c2/k2/(c1/k1)-1)*100:+.0f}%）・CPM {c1/i1*1000:,.0f}→{c2/i2*1000:,.0f}（{((c2/i2)/(c1/i1)-1)*100:+.0f}%）・上がったセット {sum(x[1] > 1 for x in xs)}/{len(xs)}")
# ---------- ⑤ 長く出している8セット／最近出した4商品／その他 に分けた実際の値段 ----------
HIT = ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', 'マグネットドアクッション', '伸縮ワックス洗車ブラシ']
print('\n■⑤ グループ別の実際の値段（終日）11/5〜11/9 → 11/10〜11/11')
for lab, f in [(f'長く出している{len(fixed)}セット', lambda s: s in fixed), ('最近出した4商品', lambda s: s in HIT), ('その他', lambda s: s not in fixed and s not in HIT)]:
    x = [sum(v[j] for s, v in a.items() if f(s)) for j in range(3)]; y = [sum(v[j] for s, v in b.items() if f(s)) for j in range(3)]
    print(f"  {lab}: 広告費の割合 {x[0]/ca*100:.0f}→{y[0]/cb*100:.0f}%・1クリック {x[0]/x[2]:.1f}→{y[0]/y[2]:.1f}円（{(y[0]/y[2]/(x[0]/x[2])-1)*100:+.0f}%）・CPM {x[0]/x[1]*1000:,.0f}→{y[0]/y[1]*1000:,.0f}（{((y[0]/y[1])/(x[0]/x[1])-1)*100:+.0f}%）・CTR {x[2]/x[1]*100:.2f}→{y[2]/y[1]*100:.2f}%")
