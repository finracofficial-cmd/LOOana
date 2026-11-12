# -*- coding: utf-8 -*-
"""11/12(木) 16:3x 「なんで最近パフォーマンスが悪すぎるのか？多面的に」
店と広告の実測を切り口ごとに並べる（終日・11/11まで）。入力: multi_1630_raw.json・ratings_1630_raw.json・cpc_acct_daily_1013_1111_raw.txt・日次CSV（代表原価の近似）。
原因の断定はしない。変わった数字／変わっていない数字を分けて出す。"""
import os, sys, csv, json, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, DATES, A, CAMP = g['S'], g['series'], g['DATES'], g['A'], g['CAMP']
SER = {n: {r['date']: r for r in series(n)} for n in S}
RAW = json.load(open(D + 'multi_1630_raw.json'))
SE = {r[0]: [int(x) for x in r[1:]] for r in RAW['sess_day']['rows']}; SA = {r[0]: [int(float(x)) for x in r[1:]] for r in RAW['sales_day']['rows']}
AC = {}
for l in open(D + 'cpc_acct_daily_1013_1111_raw.txt'):
    if l.startswith('2026-'): d, c, i, r, k = l.strip().split(','); AC[d] = [int(c), int(i), int(r), int(k)]
days = sorted(SE); assert len(days) == 30 and set(days) == set(SA) == set(AC)
adall = {d: sum(v.get(d, 0.0) for v in A.values()) for d in days}
net = {d: sum(SER[n][d]['sales'] for n in S) for d in days}; cogs = {d: sum((SER[n][d]['cost'] or 0) for n in S) for d in days}
for d in days: assert net[d] == SA[d][1] + SA[d][2], d
prof = {d: net[d] - cogs[d] - adall[d] for d in days}
W = [('10/13〜19', days[0:7]), ('10/20〜26', days[7:14]), ('10/27〜11/2', days[14:21]), ('11/3〜9', days[21:28]), ('11/10〜11', days[28:30])]
print('■① 週ごと（1日あたり・終日）')
f = [('利益（近似）', lambda ds: sum(prof[d] for d in ds) / len(ds), '{:,.0f}'), ('売上', lambda ds: sum(net[d] for d in ds) / len(ds), '{:,.0f}'), ('広告費', lambda ds: sum(adall[d] for d in ds) / len(ds), '{:,.0f}'),
     ('倍率', lambda ds: sum(net[d] - cogs[d] for d in ds) / sum(adall[d] for d in ds), '{:.2f}'), ('来訪', lambda ds: sum(SE[d][0] for d in ds) / len(ds), '{:,.0f}'), ('注文', lambda ds: sum(SA[d][0] for d in ds) / len(ds), '{:.0f}'),
     ('1クリック円', lambda ds: sum(AC[d][0] for d in ds) / sum(AC[d][3] for d in ds), '{:.1f}'), ('CPM', lambda ds: sum(AC[d][0] for d in ds) / sum(AC[d][1] for d in ds) * 1000, '{:,.0f}'), ('CTR%', lambda ds: sum(AC[d][3] for d in ds) / sum(AC[d][1] for d in ds) * 100, '{:.2f}'),
     ('来訪÷クリック', lambda ds: sum(SE[d][0] for d in ds) / sum(AC[d][3] for d in ds), '{:.2f}'), ('カゴ投入率%', lambda ds: sum(SE[d][1] for d in ds) / sum(SE[d][0] for d in ds) * 100, '{:.2f}'), ('カゴ→決済画面%', lambda ds: sum(SE[d][2] for d in ds) / sum(SE[d][1] for d in ds) * 100, '{:.0f}'),
     ('決済画面→完了%', lambda ds: sum(SE[d][3] for d in ds) / sum(SE[d][2] for d in ds) * 100, '{:.0f}'), ('購入完了÷来訪%', lambda ds: sum(SE[d][3] for d in ds) / sum(SE[d][0] for d in ds) * 100, '{:.2f}'), ('客単価', lambda ds: sum(net[d] for d in ds) / sum(SA[d][0] for d in ds), '{:,.0f}'),
     ('注文1件の広告費', lambda ds: sum(adall[d] for d in ds) / sum(SA[d][0] for d in ds), '{:,.0f}'), ('再購入の客の割合%', lambda ds: sum(SA[d][5] for d in ds) / sum(SA[d][4] + SA[d][5] for d in ds) * 100, '{:.1f}'), ('返品額÷売上%', lambda ds: -sum(SA[d][3] for d in ds) / sum(SA[d][1] for d in ds) * 100, '{:.2f}')]
print('  項目: ' + '／'.join(w for w, _ in W))
for lab, fn, fm in f: print(f"  {lab}: " + '／'.join(fm.format(fn(ds)) for _, ds in W))
print('  日別の利益（近似）: ' + ' '.join(f"{d[5:]} {prof[d]/1000:.0f}" for d in days) + '（千円）')
# ② 商品別の利益: 10/13〜11/8 と 11/9〜11
b0 = days[0:27]; b1 = days[27:30]
def pp(n, ds): return sum(SER[n][d]['sales'] - (SER[n][d]['cost'] or 0) - SER[n][d]['ad'] for d in ds) / len(ds), sum(SER[n][d]['ad'] for d in ds) / len(ds)
rows = sorted(((n, pp(n, b0), pp(n, b1)) for n in S), key=lambda z: z[2][0] - z[1][0])
print(f"\n■② 商品別の利益/日（広告費/日）: 10/13〜11/8（27日）→ 11/9〜11/11（3日）。全体 {sum(prof[d] for d in b0)/27:,.0f} → {sum(prof[d] for d in b1)/3:,.0f}（差 {sum(prof[d] for d in b1)/3-sum(prof[d] for d in b0)/27:+,.0f}）")
for n, x, y in rows[:8]: print(f"  ▼{n}: {x[0]:+,.0f}（{x[1]:,.0f}）→ {y[0]:+,.0f}（{y[1]:,.0f}）差 {y[0]-x[0]:+,.0f}")
for n, x, y in rows[-6:][::-1]: print(f"  ▲{n}: {x[0]:+,.0f}（{x[1]:,.0f}）→ {y[0]:+,.0f}（{y[1]:,.0f}）差 {y[0]-x[0]:+,.0f}")
# ナノの月内推移
print('  ナノガラス脱毛パッドの週ごと 広告費/日・倍率・利益/日: ' + ' ｜ '.join(f"{w} {sum(SER['ナノガラス脱毛パッド'][d]['ad'] for d in ds)/len(ds):,.0f}・{sum(SER['ナノガラス脱毛パッド'][d]['sales']-(SER['ナノガラス脱毛パッド'][d]['cost'] or 0) for d in ds)/sum(SER['ナノガラス脱毛パッド'][d]['ad'] for d in ds):.2f}・{pp('ナノガラス脱毛パッド', ds)[0]:+,.0f}" for w, ds in W))
# ③ 年齢×性別
def ag(k):
    out = {}
    for r in RAW[k]['rows']:
        a, s, c, i, cl, pu, pv = r.split(','); 
        if s == 'unknown' or a == 'Unknown': continue
        out[(a, s)] = [int(c), int(i), int(cl), 0 if pu == 'null' else int(pu)]
    return out
x, y = ag('age_gender_1105_1109'), ag('age_gender_1110_1111'); tx = sum(v[0] for v in x.values()); ty = sum(v[0] for v in y.values())
print('\n■③ 年齢×性別（Meta・終日）11/5〜11/9 → 11/10〜11/11: 広告費の割合%｜CPM｜1クリック円｜購入÷クリック%')
up = 0
for k in sorted(x, key=lambda k: -x[k][0]):
    a, b = x[k], y[k]; up += (b[0] / b[1]) > (a[0] / a[1])
    print(f"  {k[0]} {'男' if k[1]=='male' else '女'}: {a[0]/tx*100:.0f}→{b[0]/ty*100:.0f}｜{a[0]/a[1]*1000:,.0f}→{b[0]/b[1]*1000:,.0f}（{((b[0]/b[1])/(a[0]/a[1])-1)*100:+.0f}%）｜{a[0]/a[2]:.0f}→{b[0]/b[2]:.0f}｜{a[3]/a[2]*100:.2f}→{b[3]/b[2]*100:.2f}")
ta = [sum(v[j] for v in x.values()) for j in range(4)]; tb = [sum(v[j] for v in y.values()) for j in range(4)]
print(f"  CPMが上がった層 {up}/{len(x)}・全体の購入÷クリック {ta[3]/ta[2]*100:.2f} → {tb[3]/tb[2]*100:.2f}%・45歳以上の男性の割合 {sum(v[0] for k, v in x.items() if k[1]=='male' and k[0] in ('45-54','55-64','65+'))/tx*100:.0f} → {sum(v[0] for k, v in y.items() if k[1]=='male' and k[0] in ('45-54','55-64','65+'))/ty*100:.0f}%")
# ④ 表示回数（同じ人に何回見せたか）
print('\n■④ 同じ人に見せた回数（frequency）')
print('  月ごと: ' + ' '.join(f"{r.split(',')[0].replace('2026|','')}月 {float(r.split(',')[4]):.2f}" for r in RAW['freq_month']['rows']))
fa = {r.split(',')[0]: float(r.split(',')[4]) for r in RAW['freq_adset_1029_1104']['rows']}; fb = {r.split(',')[0]: (float(r.split(',')[4]), int(r.split(',')[1])) for r in RAW['freq_adset_1105_1111']['rows']}
print('  広告セット別（7日）10/29〜11/4 → 11/5〜11/11: ' + '・'.join(f"{n} {fa.get(n, 0):.2f}→{v[0]:.2f}" for n, v in sorted(fb.items(), key=lambda z: -z[1][1])[:12]))
# ⑤ 品質評価
print('\n■⑤ Metaの広告の評価（品質／反応率／購入率の順位）: 10/22〜10/28 → 11/5〜11/11')
def q(k):
    o = {}
    for r in RAW[k]['rows']:
        p = next(csv.reader([r])); o[(p[0], p[1])] = (p[2], p[3], p[4], int(p[5]))
    return o
qa, qb = q('quality_1022_1028'), q('quality_1105_1111')
for k, v in sorted(qb.items(), key=lambda z: -z[1][3]):
    if v[3] < 40000: continue
    print(f"  {k[0]}／{k[1]}: {qa.get(k, ('—',))[0]} → {v[0]}｜反応率 {v[1]}｜購入率 {v[2]}")
print(f"  11/5〜11/11 で品質が「平均より下」の広告: {[k[0] for k, v in qb.items() if 'Below' in v[0]]}／10/22〜10/28: {[k[0]+'/'+k[1] for k, v in qa.items() if 'Below' in v[0]]}")
# ⑥ サイト内の評価
RT = json.load(open(D + 'ratings_1630_raw.json'))['rows']
print(f"\n■⑥ サイト内の評価（Judge.me・有効な商品60件）: 評価 {min(float(r[1]) for r in RT):.2f}〜{max(float(r[1]) for r in RT):.2f}・件数 1商品あたり {min(int(r[2]) for r in RT)}〜{max(int(r[2]) for r in RT)}件（合計 {sum(int(r[2]) for r in RT)}件）・在庫切れの商品 {sum(1 for r in RT if not r[4])}")
print('  主力: ' + '・'.join(f"{r[0]} {r[1]}（{r[2]}件）" for r in RT if any(k in r[0] for k in ['伸縮ガラスクリーナー', 'ワイド水切り', 'W固定', 'ナノガラス', '洗車ブラシ', 'ドアクッション', 'レインガード', '4-in-1', 'インソール'])))
# ⑦ 返品・端末・去年
print('\n■⑦ 返品額÷売上（月）: ' + ' '.join(f"{r[0][5:7]}月 {-float(r[4])/float(r[2])*100:.2f}%" for r in RAW['returns_month']['rows']))
dv = collections.defaultdict(dict)
for r in RAW['device_week']['rows']: dv[r[1]][r[0]] = [int(x) for x in r[2:]]
print('  スマホの割合と購入完了÷来訪（週）: ' + ' '.join(f"{w[5:]}週 {v['mobile'][0]/sum(x[0] for x in v.values())*100:.0f}%・{v['mobile'][3]/v['mobile'][0]*100:.2f}%" for w, v in sorted(dv.items())))
print('  去年（2025年）の同じ時期: 注文は ' + '・'.join(f"{r[0][5:]}週 {r[1]}件" for r in RAW['sales_2025_week']['rows'] if int(r[1]) or r[0] >= '2025-12-01') + ' ＝ 店の販売開始は2025年12月。去年の11月のデータはない')
# ⑧ 利益の差を「広告費の額」と「倍率」に分ける（利益 = 広告費 ×（倍率−1））
def pa(ds): a = sum(adall[d] for d in ds) / len(ds); p_ = sum(prof[d] for d in ds) / len(ds); return a, p_, p_ / a
A0 = days[0:14]; B0 = days[28:30]; (a0, p0, m0), (a1, p1, m1) = pa(A0), pa(B0)
print(f"\n■⑧ 10/13〜10/26（14日）→ 11/10〜11/11: 利益/日 {p0:,.0f} → {p1:,.0f}（差 {p1-p0:+,.0f}）・広告費/日 {a0:,.0f} → {a1:,.0f}（{(a1/a0-1)*100:+.0f}%）・倍率 {m0+1:.2f} → {m1+1:.2f}")
print(f"  差の内訳: 広告費が減った分 {(a1-a0)*(m0+m1)/2:+,.0f}／倍率が下がった分 {(m1-m0)*(a0+a1)/2:+,.0f}（合計 {(a1-a0)*(m0+m1)/2+(m1-m0)*(a0+a1)/2:+,.0f}）")
print('  広告費/日の差の内訳（商品別・上位）: ' + '・'.join(f"{n} {y-x:+,.0f}" for n, x, y in sorted(((n, sum(SER[n][d]['ad'] for d in A0) / 14, sum(SER[n][d]['ad'] for d in B0) / 2) for n in S), key=lambda z: z[2] - z[1])[:6]) + ' ／増えた: ' + '・'.join(f"{n} {y-x:+,.0f}" for n, x, y in sorted(((n, sum(SER[n][d]['ad'] for d in A0) / 14, sum(SER[n][d]['ad'] for d in B0) / 2) for n in S), key=lambda z: z[1] - z[2])[:5]))
mo = {r[0][:7]: (int(r[1]), ) for r in RAW['returns_month']['rows']}
print(f"  計測: Metaが数えた購入 10月 3,113・11月(〜11日) 947 ／ Shopifyの注文 10月 {mo['2026-10'][0]:,}・11月 {mo['2026-11'][0]:,}（summer_month_raw.json のMeta月別より）")
