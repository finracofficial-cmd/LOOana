# -*- coding: utf-8 -*-
"""11/12 09:4x: ヘッドレストフックが儲からなくなった経過（週別）と、すき間ポケットのここまで（読み取りのみ）。
Meta の Yearweek は日曜始まり（日次CSVの広告費と週ごとに照合して確認・差は端数の数円）。Shopify の倍率も同じ日曜始まりで積む。
着地ページの来訪（Shopify sessions GROUP BY week）は月曜始まりなので、1日ずれた参考値。
フックの原価: 10/7以降732円。それ以前は 黒1,275／茶・灰1,344 の中間1,300円で近似（倍率は参考）。"""
import os, csv, json, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
AD = collections.defaultdict(float); S = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if 'ヘッドレストフック' in r['campaign']: AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == '高見えレザーヘッドレストフック': S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
def sun(d):
    x = datetime.date.fromisoformat(d); return (x - datetime.timedelta(days=(x.weekday() + 1) % 7)).isoformat()
W = collections.defaultdict(lambda: [0, 0, 0.0, 0])
cost = lambda d: 732 if d >= '2026-10-07' else 1300
for d, (g, dc) in S.items():
    if d >= '2026-09-06': assert g % 3980 == 0; W[sun(d)][0] += g; W[sun(d)][1] += dc; W[sun(d)][3] += g // 3980 * cost(d)
for d, a in AD.items():
    if d >= '2026-09-06': W[sun(d)][2] += a
M = collections.defaultdict(dict)
for ln in open(D + 'hook_meta_week_raw.txt'):
    if ln.startswith('#') or not ln.strip(): continue
    yw, n, *v = ln.strip().split(','); v = [int(float(x)) for x in v]
    y, w = yw.split('|'); s = (datetime.date.fromisocalendar(int(y), int(w), 1) - datetime.timedelta(days=1)).isoformat()   # ISO週の月曜の前日＝日曜
    M[s][n] = v
for s in sorted(M): assert abs(sum(v[0] for v in M[s].values()) - W[s][2]) <= 10, (s, sum(v[0] for v in M[s].values()), W[s][2])   # Meta週計 = CSV週計
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'hook_sess_week_raw.json'))['rows']}
print('■ ヘッドレストフック 週別（日曜始まり）: 広告費 ｜ 表示1,000回の単価・クリック率・1クリックの広告費・Meta購入1件の広告費 ｜ Shopify 個数・値引率・倍率')
for s in sorted(M):
    g, dc, a, k = W[s]
    for n, v in M[s].items():
        if not v[1]: continue
        c, im, rc, cl, lp, atc, pu = v
        tag = '' if n == '高見えレザーヘッドレストフック' else '【' + n.replace('高見えレザーヘッドレストフック', '').strip() + '】'
        line = f"  {s[5:]}週{tag}: {c:,} ｜ {c/im*1000:,.0f}・{cl/im*100:.2f}%・{c/cl:.0f}円・{(f'{c/pu:,.0f}円' if pu else '—')}（{pu}件）"
        if not tag: line += f" ｜ {g//3980}個・{(dc/g*100 if g else 0):.1f}%・{((g-dc-k)/a if a else float('nan')):.2f}"
        print(line)
print('  着地ページの来訪→購入完了（月曜始まりの週）: ' + '・'.join(f"{k[5:]} {v[0]}→{v[3]}（{v[3]/v[0]*100:.1f}%）" for k, v in sorted(SE.items())))
# 9月の好調期と停止前の比較（主力セット）
def agg(ws):
    t = [sum(M[s]['高見えレザーヘッドレストフック'][i] for s in ws) for i in range(7)]
    return t[0] / t[1] * 1000, t[3] / t[1] * 100, t[0] / t[3], t[0] / t[6] if t[6] else float('nan'), t[6] / t[4] * 100
a = agg(['2026-09-13', '2026-09-20', '2026-09-27']); b = agg(['2026-10-18', '2026-10-25'])
print(f"  9/13〜10/3（3週）→ 10/18〜10/31（2週）: 表示単価 {a[0]:,.0f}→{b[0]:,.0f}（{(b[0]/a[0]-1)*100:+.0f}%）・クリック率 {a[1]:.2f}→{b[1]:.2f}%（{(b[1]/a[1]-1)*100:+.0f}%）・1クリック {a[2]:.0f}→{b[2]:.0f}円（{(b[2]/a[2]-1)*100:+.0f}%）・Meta購入1件 {a[3]:,.0f}→{b[3]:,.0f}円・着地→Meta購入 {a[4]:.1f}→{b[4]:.1f}%")
print('  倍率1.25になる注文1件の広告費: (6,203−1.70×732)÷1.25 =', round((6203 - 1.70 * 732) / 1.25))
print('\n■ すき間収納シートポケット（11/11 22:30開始〜11/12 09:3x）')
tot = [0] * 6
for ln in open(D + 'gap_meta_hour_raw.txt'):
    if ln.startswith('#') or not ln.strip(): continue
    parts = ln.strip().split(',')
    tot = [x + int(y) for x, y in zip(tot, parts[-6:])]
print(f"  Meta: 広告費 {tot[0]:,}・表示 {tot[1]}・クリック {tot[2]}（クリック率 {tot[2]/tot[1]*100:.2f}%）・表示単価 {tot[0]/tot[1]*1000:,.0f}・1クリック {tot[0]/tot[2]:.0f}円・着地 {tot[3]}・Metaカート {tot[4]}・Meta購入 {tot[5]}")
gs = json.load(open(D + 'gap_sess_day_raw.json'))['rows']; ns = json.load(open(D + 'new_sales_day_raw.json'))['rows']
print('  Shopify 着地ページ: ' + '・'.join(f"{r[0][5:]} 来訪{r[1]}・カート{r[2]}・チェックアウト{r[3]}・完了{r[4]}" for r in gs))
print('  販売: ' + '／'.join(f"{r[0][5:]} {'すき間' if 'すき間' in r[1] else 'パンツ'} 注文{r[2]}・{r[3]}個・{int(r[4])+int(r[5]):,}円" for r in ns))
print(f"  すき間のここまでの倍率: (3,980−760)×1 ÷ {tot[0]:,} = {(3980-760)/tot[0]:.2f} ／ 倍率1.25になる1個あたり広告費 {(3980-760)/1.25:,.0f}円")
