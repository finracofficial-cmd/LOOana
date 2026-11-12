# -*- coding: utf-8 -*-
"""11/12(木) 12:2x 「なんで夏ってあんな売れたんだ」
7月〜11月（11/11まで）を月ごとに並べ、売上 = 広告費 ×（クリック÷広告費）×（来訪÷クリック）×（注文÷来訪）×（売上÷注文）に分ける。あわせて、月ごとにどの商品が稼いだかを出す。
入力: data/daily/daily_sales.csv・daily_ad.csv（6/29〜11/11・verify.py 通過）／summer_month_raw.json（Shopify 月別の来訪・注文、Meta 月別・11/12 12:2x取得）
原価は product_tabs.py の代表原価×個数（ナノガラス・ディスペンサーなどは加重平均の近似）。利益は 売上（gross−値引）−原価−広告費。返品は引かない。"""
import os, sys, csv, json, math, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g)
exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, A, CAMP, series, DATES = g['S'], g['A'], g['CAMP'], g['series'], g['DATES']
assert DATES[0] == '2026-06-29' and DATES[-1] == '2026-11-11'
SER = {n: {r['date']: r for r in series(n)} for n in S}
mapped = {CAMP.get(n, n) for n in S}
unm = collections.defaultdict(float)   # 商品に紐づかないキャンペーン（カタログなど）
for c, v in A.items():
    if c not in mapped:
        for d, x in v.items(): unm[d] += x
adall = {d: sum(v.get(d, 0.0) for v in A.values()) for d in DATES}
net = {d: sum(SER[n][d]['sales'] for n in S) for d in DATES}
cogs = {d: sum((SER[n][d]['cost'] or 0) for n in S) for d in DATES}
prof = {d: net[d] - cogs[d] - adall[d] for d in DATES}
noq = collections.defaultdict(int)
for n in S:
    for d in DATES:
        if SER[n][d]['qty'] is None and SER[n][d]['sales']: noq[n] += SER[n][d]['sales']
print('個数が解けず原価を入れていない売上（合計）:', dict(noq) or 'なし')
print(f"照合 11/11: 売上 {net['2026-11-11']:,}・広告費 {adall['2026-11-11']:,.0f}・利益 {prof['2026-11-11']:,.0f}（定例の値 62,422）")
RAW = json.load(open(D + 'summer_month_raw.json'))
MO = ['2026-07', '2026-08', '2026-09', '2026-10', '2026-11']; LAB = {'2026-07': '7月', '2026-08': '8月', '2026-09': '9月', '2026-10': '10月', '2026-11': '11月(〜11日)'}
SE = {r[0][:7]: [int(x) for x in r[1:]] for r in RAW['sess']['rows']}; SA = {r[0][:7]: [int(float(x)) for x in r[1:]] for r in RAW['sales']['rows']}
ME = {r[0].replace('|', '-'): [int(x) for x in r[1:]] for r in RAW['meta']['rows']}
M = {}
for m in MO:
    ds = [d for d in DATES if d[:7] == m]; n_ = len(ds)
    v = dict(days=n_, net=sum(net[d] for d in ds), ad=sum(adall[d] for d in ds), cogs=sum(cogs[d] for d in ds), prof=sum(prof[d] for d in ds),
             sess=SE[m][0], comp=SE[m][3], orders=SA[m][0], items=SA[m][3], clicks=ME[m][2], imp=ME[m][1], mcost=ME[m][0])
    assert v['net'] == SA[m][1] + SA[m][2], (m, v['net'], SA[m][1] + SA[m][2])          # CSVの売上 = Shopify 月別（gross−値引）
    assert abs(v['ad'] - v['mcost']) / v['mcost'] < 0.002, (m, v['ad'], v['mcost'])     # CSVの広告費 ≒ Meta 月別（差0.2%未満）
    M[m] = v
print('\n■ 月ごと（1日あたり）')
rows = [('売上', lambda v: v['net'] / v['days'], '{:,.0f}'), ('広告費', lambda v: v['ad'] / v['days'], '{:,.0f}'), ('利益（原価は近似）', lambda v: v['prof'] / v['days'], '{:,.0f}'),
        ('売上÷広告費', lambda v: v['net'] / v['ad'], '{:.2f}'), ('倍率（(売上−原価)÷広告費）', lambda v: (v['net'] - v['cogs']) / v['ad'], '{:.2f}'), ('原価率%', lambda v: v['cogs'] / v['net'] * 100, '{:.1f}'),
        ('注文', lambda v: v['orders'] / v['days'], '{:.0f}'), ('来訪', lambda v: v['sess'] / v['days'], '{:,.0f}'), ('クリック', lambda v: v['clicks'] / v['days'], '{:,.0f}'),
        ('1クリック円', lambda v: v['mcost'] / v['clicks'], '{:.1f}'), ('CPM', lambda v: v['mcost'] / v['imp'] * 1000, '{:,.0f}'), ('CTR%', lambda v: v['clicks'] / v['imp'] * 100, '{:.2f}'),
        ('来訪÷クリック', lambda v: v['sess'] / v['clicks'], '{:.2f}'), ('注文÷来訪%', lambda v: v['orders'] / v['sess'] * 100, '{:.2f}'), ('購入完了÷来訪%', lambda v: v['comp'] / v['sess'] * 100, '{:.2f}'),
        ('客単価', lambda v: v['net'] / v['orders'], '{:,.0f}'), ('1注文の個数', lambda v: v['items'] / v['orders'], '{:.2f}'), ('注文1件の広告費', lambda v: v['ad'] / v['orders'], '{:,.0f}')]
print('  項目: ' + '／'.join(LAB[m] for m in MO))
for lab, f, fm in rows: print(f"  {lab}: " + '／'.join(fm.format(f(M[m])) for m in MO))
def decomp(a, b):
    x, y = M[a], M[b]; pd = lambda v: v['days']
    f = [('広告費（1日あたり）', lambda v: v['ad'] / pd(v)), ('クリック÷広告費', lambda v: v['clicks'] / v['ad']), ('来訪÷クリック', lambda v: v['sess'] / v['clicks']), ('注文÷来訪', lambda v: v['orders'] / v['sess']), ('客単価', lambda v: v['net'] / v['orders'])]
    tot = (x['net'] / pd(x)) / (y['net'] / pd(y)); pr = 1
    print(f"\n■ 分解: {LAB[a]} ÷ {LAB[b]}（1日あたりの売上 {x['net']/pd(x):,.0f} ÷ {y['net']/pd(y):,.0f} ＝ {tot:.2f}倍）")
    for lab, fn in f:
        r = fn(x) / fn(y); pr *= r; print(f"  {lab}: {r:.2f}倍（差 {(x['net']/pd(x)-y['net']/pd(y))*math.log(r)/math.log(tot):+,.0f}円/日）")
    assert abs(pr - tot) < 1e-9
decomp('2026-07', '2026-10'); decomp('2026-07', '2026-11'); decomp('2026-08', '2026-10')
# ---------- 商品別 ----------
def pm(n, ds):
    s = sum(SER[n][d]['sales'] for d in ds); c = sum((SER[n][d]['cost'] or 0) for d in ds); a = sum(SER[n][d]['ad'] for d in ds); q = sum((SER[n][d]['qty'] or 0) for d in ds)
    return s, c, a, s - c - a, q, sum(1 for d in ds if SER[n][d]['ad'] >= 3000)
print('\n■ 月ごとの商品別（利益の大きい順・上位8）: 売上／広告費（1日あたり・出稿日数）／利益／倍率')
for m in MO:
    ds = [d for d in DATES if d[:7] == m]; P = {n: pm(n, ds) for n in S}; tp = sum(v[3] for v in P.values()); ta = sum(v[2] for v in P.values())
    top = sorted(P, key=lambda n: -P[n][3])[:8]
    print(f"  【{LAB[m]}】商品別の利益の合計 {tp:,.0f}（商品に紐づかない広告費 {sum(unm[d] for d in ds):,.0f} を引く前）・上位3つで {sum(P[n][3] for n in top[:3])/tp*100:.0f}%・広告費の上位3つで {sum(sorted((v[2] for v in P.values()), reverse=True)[:3])/ta*100:.0f}%")
    for n in top:
        s, c, a, p_, q, nd = P[n]; print(f"    {n}: {s:,}／{a:,.0f}（{a/max(nd,1):,.0f}/日・{nd}日）／{p_:+,.0f}／{'—' if a < 1 else f'{(s-c)/a:.2f}'}")
    print(f"    月の広告費が50万円以上で倍率1.5以上の商品: " + ('・'.join(f"{n}（{P[n][2]/10000:,.0f}万・{(P[n][0]-P[n][1])/P[n][2]:.2f}）" for n in sorted(P, key=lambda n: -P[n][2]) if P[n][2] >= 500000 and (P[n][0] - P[n][1]) / P[n][2] >= 1.5) or 'なし'))
    big = [n for n in P if P[n][2] >= 500000]; print(f"    月の広告費が50万円以上の商品 {len(big)}本・その広告費の合計 {sum(P[n][2] for n in big)/10000:,.0f}万（全体の{sum(P[n][2] for n in big)/ta*100:.0f}%）")
# 7月の全商品（売上順）
ds7 = [d for d in DATES if d[:7] == '2026-07']
print('\n■ 7月の売上（上位20）: ' + '・'.join(f"{n} {pm(n, ds7)[0]/10000:,.0f}万" for n in sorted(S, key=lambda n: -pm(n, ds7)[0])[:20]))
# ---------- 夏物（暑さ・日差し・虫よけ向けの商品。名前で分類＝こちらの判断）の割合 ----------
SUMMER = ['4WAY', '害虫ブロッカー', '形状記憶日傘', '完全遮光・形状記憶', '接触冷感UVパーカー', '偏光・調光サングラス', '卓上冷感クーラー', '接触冷感UVアームカバー', '3WAYサーキュレーター',
          '5WAY腰掛けファン', '瞬間冷感ポンチョ', '完全遮光・接触冷感UVハット', '瞬間冷却ハンディファン']
assert all(n in S for n in SUMMER), [n for n in SUMMER if n not in S]
print('\n■ 夏物13本（' + '・'.join(SUMMER) + '）の月別')
for m in MO:
    ds = [d for d in DATES if d[:7] == m]; P = {n: pm(n, ds) for n in S}
    s = sum(P[n][0] for n in SUMMER); a = sum(P[n][2] for n in SUMMER); p_ = sum(P[n][3] for n in SUMMER); c = sum(P[n][1] for n in SUMMER)
    o = [n for n in S if n not in SUMMER]; s2 = sum(P[n][0] for n in o); a2 = sum(P[n][2] for n in o); p2 = sum(P[n][3] for n in o); c2 = sum(P[n][1] for n in o)
    print(f"  {LAB[m]}: 夏物 売上 {s/len(ds):,.0f}/日（全体の{s/M[m]['net']*100:.0f}%）・広告費 {a/len(ds):,.0f}/日・利益 {p_/len(ds):+,.0f}/日・倍率 {'—' if a < 1 else f'{(s-c)/a:.2f}'} ｜ それ以外 売上 {s2/len(ds):,.0f}/日・広告費 {a2/len(ds):,.0f}/日・利益 {p2/len(ds):+,.0f}/日（カタログ等の広告費を引く前）・倍率 {(s2-c2)/a2:.2f}")
print('\n■ 広告費の大きい上位4商品（1日あたりの広告費・倍率）')
for m in MO:
    ds = [d for d in DATES if d[:7] == m]; P = {n: pm(n, ds) for n in S}
    print(f"  {LAB[m]}: " + '・'.join(f"{n} {P[n][2]/len(ds):,.0f}円（{(P[n][0]-P[n][1])/P[n][2]:.2f}）" for n in sorted(P, key=lambda n: -P[n][2])[:4]))
print('\n■ 夏物の週ごとの売上と倍率（月曜始まり）')
wk = collections.defaultdict(list)
for d in DATES:
    dd = datetime.date.fromisoformat(d); wk[(dd - datetime.timedelta(days=dd.weekday())).isoformat()].append(d)
for w, ds in sorted(wk.items()):
    if len(ds) < 7: continue
    P = {n: pm(n, ds) for n in SUMMER}; s = sum(v[0] for v in P.values()); a = sum(v[2] for v in P.values()); c = sum(v[1] for v in P.values())
    print(f"  {w[5:]}週: 売上 {s/7:,.0f}/日・広告費 {a/7:,.0f}/日・倍率 {'—' if a < 7000 else f'{(s-c)/a:.2f}'}")
# ---------- 寒い時期向けに出した商品（名前で分類＝こちらの判断）のこれまで ----------
print('\n■ 寒い時期向けに出した商品の通算（広告を出した日・〜11/11）')
for n in ['コードレスダブルミスト加湿器', 'ふわとろ高密度ブランケット', '防風あったか裏起毛パンツ']:
    ds = [d for d in DATES if SER[n][d]['ad'] > 0] if n in S else []
    if not ds: print(f"  {n}: 売上の記録なし（広告費 {sum(A[CAMP.get(n, n)].values()):,.0f}円）"); continue
    s, c, a, p_, q, nd = pm(n, ds); print(f"  {n}: {ds[0][5:]}〜{ds[-1][5:]}・広告を出した日 {len(ds)}日・{q}個・売上 {s:,}・広告費 {a:,.0f}・利益 {p_:+,.0f}・倍率 {(s-c)/a:.2f}")
