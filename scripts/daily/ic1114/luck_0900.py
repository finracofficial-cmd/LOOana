# -*- coding: utf-8 -*-
"""11/14 09:0x ユーザー「つまり全てが偶然。運の悪さの重なりこんなところ？」
入力: data/daily（実測）と product_tabs.py の原価。
1) 週別（金〜木）の倍率を、固定の基準（9/2〜10/1・祝日除く）の日ごとのぶれで判定。10/2週→10/23週の下がりが偶然で起きる大きさか
2) 柱（7日平均 利益2万円/日以上）の本数を週ごとに数え、柱がどこから来たか（出して何日目か）
3) 新商品（広告を初めて出した日）の本数と当たり方を2週ごとに数える＝「打席が減った」のか「当たらなくなった」のか"""
import csv, sys, math, collections, datetime, statistics as st
R = __file__.rsplit('/scripts/', 1)[0] + '/'
HOL = {'2026-07-20', '2026-08-11', '2026-09-21', '2026-09-22', '2026-09-23', '2026-10-12', '2026-11-03', '2026-11-23'}
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
NET = collections.defaultdict(int); AD = collections.defaultdict(float); ADC = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    AD[r['date']] += float(r['cost']); ADC[r['campaign']][r['date']] = ADC[r['campaign']].get(r['date'], 0) + float(r['cost'])
CO = collections.defaultdict(float); P = {}   # 商品別 日次利益
for n in g['S']:
    P[n] = {}
    for r in g['series'](n):
        CO[r['date']] += r['cost'] or 0
        P[n][r['date']] = r['sales'] - (r['cost'] or 0) - r['ad']
# 売上0件で daily_sales にない商品（広告費だけ）も商品として入れる
mapped = {g['CAMP'].get(n, n) for n in g['S']}
for c, v in ADC.items():
    if c not in mapped and 'カタログ' not in c: P[c] = {d: -x for d, x in v.items()}
D = lambda s: datetime.date.fromisoformat(s)
iso = lambda d: d.isoformat()
LAST = '2026-11-13'
assert LAST in AD and LAST in NET
# 照合: 商品利益の合計 − カタログ広告費 = 全店利益（全期間）
cat = sum(v for c, v in ADC.items() if 'カタログ' in c for v in v.values())
tot = sum(NET[d] - CO[d] - AD[d] for d in AD)
assert abs(sum(sum(v.values()) for v in P.values()) - cat - tot) < 5, (sum(sum(v.values()) for v in P.values()) - cat, tot)

# ---- 1) 週別の倍率を固定の基準で判定 ----
base = [iso(D('2026-09-02') + datetime.timedelta(k)) for k in range(30)]
base = [d for d in base if d not in HOL]
lv = [math.log((NET[d] - CO[d]) / AD[d]) for d in base]; mu, sd = st.median(lv), st.stdev(lv)
print(f'■1 週別（金〜木）の倍率。基準 9/2〜10/1（祝日除く{len(base)}日）中央値 {math.exp(mu):.2f}・日ごとのぶれ ±{(math.exp(sd)-1)*100:.0f}% → 7日平均のぶれ ±{(math.exp(sd/math.sqrt(7))-1)*100:.1f}%')
wk = {}
s = D('2026-09-04')
while iso(s + datetime.timedelta(6)) <= '2026-11-12':
    ds = [iso(s + datetime.timedelta(k)) for k in range(7)]
    m = (sum(NET[d] for d in ds) - sum(CO[d] for d in ds)) / sum(AD[d] for d in ds)
    prof = sum(NET[d] - CO[d] - AD[d] for d in ds) / 7
    z = (math.log(m) - mu) / (sd / math.sqrt(7))
    wk[ds[0]] = (m, ds)
    print(f'  {ds[0][5:]}〜{ds[-1][5:]}: 倍率 {m:.2f}（基準比 z={z:+.1f}）・利益 {prof:+,.0f}/日・広告費 {sum(AD[d] for d in ds)/7:,.0f}/日')
    s += datetime.timedelta(7)
a, b = wk['2026-10-02'][0], wk['2026-10-23'][0]
zd = (math.log(a) - math.log(b)) / (sd / math.sqrt(7) * math.sqrt(2))
print(f'  10/2週 {a:.2f} → 10/23週 {b:.2f}（{(b/a-1)*100:+.0f}%）: 2つの週の差のぶれ ±{(math.exp(sd/math.sqrt(7)*math.sqrt(2))-1)*100:.1f}% → z={zd:.1f}')
# 4週連続で下がる確率（偶然なら各週の上下は半々）

# ---- 2) 柱の本数と出どころ ----
FIRST = {}
for n in P:
    camp = g['CAMP'].get(n, n)
    ds = sorted(d for d, v in ADC.get(camp, {}).items() if v > 0)
    if ds: FIRST[n] = ds[0]
print()
print('■2 柱（7日平均 利益2万円/日以上）の本数（各週の木曜まで7日）。カッコ内は出して何日目か（6/29以前からの商品は「既存」）')
pill = {}
for w0, (m, ds) in wk.items():
    ps = []
    for n in P:
        pr = sum(P[n].get(d, 0) for d in ds) / 7
        if pr >= 20000:
            f = FIRST.get(n)
            age = (D(ds[-1]) - D(f)).days + 1 if f and f > '2026-06-29' else None
            ps.append((n, pr, age))
    pill[w0] = ps
    print(f'  {w0[5:]}週: {len(ps)}本 ' + '・'.join(f"{n}{pr/1e4:.1f}万({'既存' if a is None else str(a)+'日目'})" for n, pr, a in sorted(ps, key=lambda x: -x[1])))

# ---- 3) 新商品の本数と当たり方 ----
print()
print('■3 新しく広告を始めた商品（初めて広告費が出た日・6/30以降・カタログ除く）を2週ごとに。当たり＝出してから14日の利益合計が +10万円以上、柱になった＝どこかの7日平均で2万円/日以上')
def pillar_ever(n):
    ds = sorted(P[n])
    for i in range(6, len(ds)):
        if sum(P[n].get(d, 0) for d in ds[i-6:i+1]) / 7 >= 20000: return True
    return False
grp = collections.defaultdict(list)
for n, f in FIRST.items():
    if f <= '2026-06-29' or n not in P: continue
    k = (D(f) - D('2026-06-30')).days // 14
    w14 = [iso(D(f) + datetime.timedelta(j)) for j in range(14)]
    p14 = sum(P[n].get(d, 0) for d in w14)
    full = w14[-1] <= LAST
    grp[k].append((n, f, p14, pillar_ever(n), full))
for k in sorted(grp):
    st0 = D('2026-06-30') + datetime.timedelta(14 * k)
    xs = grp[k]
    hits = [x for x in xs if x[2] >= 100000]; pil = [x for x in xs if x[3]]
    print(f'  {iso(st0)[5:]}〜{iso(st0+datetime.timedelta(13))[5:]}: {len(xs)}本・当たり {len(hits)}・柱になった {len(pil)} … ' + '・'.join(f"{n}({f[5:]} 14日{p:+,.0f}{'' if full else '途中'}{'★' if pe else ''})" for n, f, p, pe, full in sorted(xs, key=lambda x: x[1])))

# ---- 4) 10/2週 → 10/23週 → 11/6週: 商品別の利益/日と広告費/日の変化（動いた順）----
print()
print('■4 10月に倍率が下がった中身: 商品別 利益/日・広告費/日・倍率（10/2週 → 10/23週 → 11/6週）。利益の変化が±5,000/日以上の商品')
W3 = ['2026-10-02', '2026-10-23', '2026-11-06']
def pw(n, w0):
    ds = wk[w0][1]
    pr = sum(P[n].get(d, 0) for d in ds) / 7
    camp = g['CAMP'].get(n, n); ad = sum(ADC.get(camp, {}).get(d, 0) for d in ds) / 7
    return pr, ad, (pr + ad) / ad if ad else float('nan')
rows = []
for n in P:
    v = [pw(n, w) for w in W3]
    if max(abs(v[1][0] - v[0][0]), abs(v[2][0] - v[1][0])) >= 5000: rows.append((n, v))
for n, v in sorted(rows, key=lambda x: x[1][1][0] - x[1][0][0]):
    print(f'  {n}: 利益 {v[0][0]:+,.0f} → {v[1][0]:+,.0f} → {v[2][0]:+,.0f}／広告費 {v[0][1]:,.0f} → {v[1][1]:,.0f} → {v[2][1]:,.0f}／倍率 ' + ' → '.join('—' if v[i][1] == 0 else f'{v[i][2]:.2f}' for i in range(3)))
cat = lambda w0: sum(v for c, x in ADC.items() if 'カタログ' in c for d, v in x.items() if d in wk[w0][1]) / 7
print(f'  カタログ: 広告費 ' + ' → '.join(f'{cat(w):,.0f}' for w in W3))
for w in W3:
    ds = wk[w][1]
    assert abs(sum(sum(P[n].get(d, 0) for d in ds) for n in P) - cat(w) * 7 - sum(NET[d] - CO[d] - AD[d] for d in ds)) < 5

# ---- 5) 直近3日を 9月の水準（固定の基準）と、ふだんの判定（前日までの30日）の両方で ----
print()
print('■5 直近3日の倍率を2つの基準で')
for d in ['2026-11-11', '2026-11-12', '2026-11-13']:
    m = (NET[d] - CO[d]) / AD[d]
    b30 = [iso(D(d) - datetime.timedelta(k)) for k in range(1, 31)]; b30 = [x for x in b30 if x not in HOL]
    l30 = [math.log((NET[x] - CO[x]) / AD[x]) for x in b30]; m30, s30 = st.median(l30), st.stdev(l30)
    print(f'  {d[5:]}: 倍率 {m:.2f}／9月の水準（中央値 {math.exp(mu):.2f}）比 z={(math.log(m)-mu)/sd:+.2f}／前日までの30日（中央値 {math.exp(m30):.2f}）比 z={(math.log(m)-m30)/s30:+.2f}')
