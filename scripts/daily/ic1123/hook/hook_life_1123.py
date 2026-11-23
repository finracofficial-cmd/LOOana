# -*- coding: utf-8 -*-
"""11/23 18時台「とめたわ。もうこの商品はダメかな？」: フックの利益を時期ごとに並べる（広告を出していない日の売れ方も）。
入力: data/daily/daily_sales.csv・daily_variant.csv・daily_ad.csv（〜11/22）・hook_v5_1123_1802_raw.json（Meta・11/23 は 18:02 取得＝停止後の当日分）・
hook_ad_video_daily_0909_1123_raw.json（クリック数）。11/23 の Shopify のフックの注文は 0（18:02 の ShopifyQL が行なし）。原価は 10/7 から 732円"""
import json, os, csv, collections, datetime
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D0 + '../../../../'
MAIN = '高見えレザーヘッドレストフック'
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
def table(f): return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
S = collections.defaultdict(lambda: [0, 0]); VG = collections.defaultdict(dict); AD = collections.defaultdict(int); CL = collections.defaultdict(int)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == MAIN: S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_variant.csv')):
    if r['name'] == MAIN: VG[r['date']][r['cost_group']] = int(r['gross'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if MAIN in r['campaign']: AD[r['date']] += int(r['cost'])
for r in table('hook_ad_video_daily_0909_1123_raw.json'):
    if r[0] <= '2026-11-22': CL[r[0]] += z(r[6])
t = table('hook_v5_1123_1802_raw.json'); assert len(t) == 1 and t[0][0] == '2026-11-23'
AD['2026-11-23'] = z(t[0][2]); CL['2026-11-23'] = z(t[0][4])
def gp(d):
    g, dc = S[d]
    if not g: return 0, 0
    if d >= '2026-10-07': cg = g // 3980 * 732
    else: v = VG[d]; cg = v.get('黒', 0) // 3980 * 1275 + v.get('茶灰', 0) // 3980 * 1344
    return g - abs(dc) - cg, g // 3980
def span(a, b):
    x = datetime.date.fromisoformat(a); o = []
    while x <= datetime.date.fromisoformat(b): o.append(x.isoformat()); x += datetime.timedelta(1)
    return o
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P('■ ① 時期ごとの フック: 日数・広告費・個数・粗利・利益（粗利−広告費）・倍率｜クリック1回の値段・クリック1回の粗利')
PER = [('9/9〜10/15（0909 の動画）', '2026-09-09', '2026-10-15'), ('10/16〜11/3（0909・-sub・フック２）', '2026-10-16', '2026-11-03'), ('11/4〜11/10（広告なし）', '2026-11-04', '2026-11-10'),
       ('11/11〜11/12（0909 の出し直し）', '2026-11-11', '2026-11-12'), ('11/13〜11/14（広告なし）', '2026-11-13', '2026-11-14'), ('11/15〜11/16（v2・v4）', '2026-11-15', '2026-11-16'),
       ('11/17（広告なし）', '2026-11-17', '2026-11-17'), ('11/18〜11/23（v5・11/23 は停止まで）', '2026-11-18', '2026-11-23')]
tot = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for nm, a, b in PER:
    ds = span(a, b); c = sum(AD[d] for d in ds); g = sum(gp(d)[0] for d in ds); u = sum(gp(d)[1] for d in ds); k = sum(CL[d] for d in ds)
    P('  %s: %d日・%s・%d個・%s・%s・%s｜%s' % (nm, len(ds), f'{c:,}', u, f'{g:,}', f'{g - c:+,}', ('%.2f' % (g / c)) if c else '—', ('%d円・%d円' % (round(c / k), round(g / k))) if k else '—'))
    key = 'A' if b <= '2026-10-15' else 'B'
    for i, v in enumerate((len(ds), c, u, g, k)): tot[key][i] += v
for key, nm in (('A', '9/9〜10/15'), ('B', '10/16〜11/23（止めていた日も含む）')):
    n, c, u, g, k = tot[key]
    P('  計 %s: %d日・広告費 %s・%d個・粗利 %s・利益 %s（1日 %s）・倍率 %.2f｜クリック1回 %d円・粗利 %d円' % (nm, n, f'{c:,}', u, f'{g:,}', f'{g - c:+,}', f'{round((g - c) / n):+,}', g / c, round(c / k), round(g / k)))
P('■ ② 10/16 以降の広告ごと（hook_video_1123.txt から）: クリック1回 0909 156円・-sub 93円（購入÷クリック 1.3%）・フック２ 248円・0909 出し直し 185円・1115 (3).mp4 143円・1118.mp4 250円。続けてよい線は 150円')
P('■ ③ 広告を出していない日のフック（Shopify）')
nd = [d for d in span('2026-11-04', '2026-11-23') if AD[d] == 0]
P('  %d日（%s）で %d個' % (len(nd), '・'.join(x[5:] for x in nd), sum(gp(d)[1] for d in nd)))
P('■ ④ 直読（18:02）: v5 のキャンペーンは PAUSED。11/23 の広告費 %s・クリック %d・Shopify の注文 0' % (f'{AD["2026-11-23"]:,}', CL['2026-11-23']))
open(D0 + 'hook_life_1123.txt', 'w').write('\n'.join(out) + '\n')

# ⑤ 区切り直し: 10/16〜26 と 10/27 以降・通算
P('■ ⑤ 区切り直し')
for nm, a, b in (('10/16〜10/26', '2026-10-16', '2026-10-26'), ('10/27〜11/23（止めていた日も含む 28日）', '2026-10-27', '2026-11-23'), ('通算 9/9〜11/23', '2026-09-09', '2026-11-23')):
    ds = span(a, b); c = sum(AD[d] for d in ds); g = sum(gp(d)[0] for d in ds); u = sum(gp(d)[1] for d in ds); k = sum(CL[d] for d in ds)
    P('  %s: 広告費 %s・%d個・粗利 %s・利益 %s・倍率 %.2f｜クリック %s・1回 %d円・クリック1回の粗利 %d円' % (nm, f'{c:,}', u, f'{g:,}', f'{g - c:+,}', g / c, f'{k:,}', round(c / k), round(g / k)))
ds = span('2026-10-27', '2026-11-23'); days_on = [d for d in ds if AD[d] > 0]
P('  10/27〜11/23 のうち広告を出した日 %d日。出し方ごとの倍率: 0909（10/27〜11/3・フック２を含む）%.2f・0909 の出し直し 0.43・v2／v4 0.86・v5 1.01' % (len(days_on), sum(gp(d)[0] for d in span('2026-10-27', '2026-11-03')) / sum(AD[d] for d in span('2026-10-27', '2026-11-03'))))
open(D0 + 'hook_life_1123.txt', 'w').write('\n'.join(out) + '\n')
