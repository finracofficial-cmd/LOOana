# -*- coding: utf-8 -*-
"""11/25 13時台「今時点のパフォーマンスを分析した上でやるべきことを提示して」: 0〜12時台（〜12:59）で切り、11/4〜11/24 の同じ時刻と並べる（日中の数字では予算を提案しない）。
入力: sales_h12_raw.json・sess_h12_raw.json（Shopify・hour_of_day <= 12）・meta_h12_1104_1125_raw.json（Meta・時刻で絞った日別）
      meta_camp_h12_1125_raw.json／meta_camp_h12_1118_1124_raw.json（キャンペーン別・同じ時刻）・prod_h12_1125_raw.json／prod_h12_1118_1124_raw.json（商品別・同じ時刻）・sess_source_h12_1125_raw.json（入口別）"""
import json, os, statistics as st, math, datetime, re, collections
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
def table(f): return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
def pois_le(e, k): return sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(k + 1)) if e > 0 else 1.0
V = {r[0]: (int(r[1]), int(r[2]) + int(r[3])) for r in json.load(open(D0 + 'sales_h12_raw.json'))['rows']}
S = {r[0]: (int(r[1]), int(r[2]), int(r[4])) for r in json.load(open(D0 + 'sess_h12_raw.json'))['rows']}
M = {r[0]: (z(r[1]), z(r[2]), z(r[3])) for r in table('meta_h12_1104_1125_raw.json')}
T = '2026-11-25'; past = [d for d in sorted(V) if d < T]; assert len(past) == 21
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
def row(d): o, net = V[d]; ad, imp, clk = M[d]; s, c, done = S[d]; return dict(o=o, net=net, ad=ad, mer=net / ad, cvr=done / s, cart=c / s, aov=net / o, cpm=ad / imp * 1000, ses=s, spa=s / ad * 1000)
R = {d: row(d) for d in past + [T]}
P('■ 0〜12時台（〜12:59）: 今日 ↔ 11/4〜11/24 の同じ時刻（21日・祝日 11/23 を含む）')
for k, lab, f in (('net', '売上（値引後）', '{:,.0f}'), ('o', '注文', '{:,.0f}'), ('ad', '広告費', '{:,.0f}'), ('mer', '売上÷広告費', '{:.2f}'), ('ses', '来訪', '{:,.0f}'), ('spa', '広告費1,000円あたりの来訪', '{:.1f}'), ('cart', 'カート率', '{:.2%}'), ('cvr', '買う率', '{:.2%}'), ('aov', '1注文の売上', '{:,.0f}'), ('cpm', 'CPM', '{:,.0f}')):
    v = [R[d][k] for d in past]; t = R[T][k]
    P(f'  {lab}: 今日 {f.format(t)}｜21日 {f.format(min(v))}〜{f.format(max(v))}（中央値 {f.format(st.median(v))}）｜今日より低い日 {sum(x < t for x in v)}/21')
tue = [d for d in past if datetime.date.fromisoformat(d).weekday() == 2]
P('  水曜（' + '・'.join(d[5:] for d in tue) + '）: ' + '・'.join(f"{d[5:]} 売上 {R[d]['net']:,}・注文 {R[d]['o']}・{R[d]['mer']:.2f}" for d in tue))
rate = sum(R[d]['o'] for d in past) / sum(R[d]['ses'] for d in past); e = rate * R[T]['ses']; k = R[T]['o']
P(f'  注文の見込み（21日の 注文÷来訪 {rate:.2%} × 今日の来訪 {R[T]["ses"]:,}）{e:.1f}件 → 実際 {k}件・この数以下になる確率 {pois_le(e, k):.0%}')
rate2 = sum(R[d]['o'] for d in past) / sum(R[d]['ad'] for d in past); e2 = rate2 * R[T]['ad']
P(f'  注文の見込み（21日の 注文÷広告費 × 今日の広告費 {R[T]["ad"]:,}）{e2:.1f}件 → 実際 {k}件・この数以下になる確率 {pois_le(e2, k):.0%}')
v = sorted(R[d]['mer'] for d in past)
j = '偶然の範囲内' if v[0] <= R[T]['mer'] <= v[-1] else '偶然でも起きるが端'
P(f'  → 売上÷広告費 {R[T]["mer"]:.2f} は 21日の範囲 {v[0]:.2f}〜{v[-1]:.2f} の中・低いほうから {sum(x < R[T]["mer"] for x in v)+1}番目 → {j}')
P('  日ごと（0〜12時台の 売上÷広告費）: ' + '・'.join(f"{d[5:]} {R[d]['mer']:.2f}" for d in past + [T]))
# 商品別: 今日 ↔ 11/17〜11/23 の同じ時刻（Shopify の注文・個数、Meta の広告費）
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
cn = lambda c: re.sub(r'\s*v\d+$', '', c).strip()
p1 = {nm(r[0]): (int(r[1]), int(r[4]), int(r[2]) + int(r[3])) for r in json.load(open(D0 + 'prod_h12_1125_raw.json'))['rows'] if 'LOOTY' in r[0]}
p7 = collections.defaultdict(lambda: [0, 0, 0])
for r in json.load(open(D0 + 'prod_h12_1118_1124_raw.json'))['rows']:
    if 'LOOTY' in r[0 + 1]:
        a = p7[nm(r[1])]; a[0] += int(r[2]); a[1] += int(r[5]); a[2] += int(r[3]) + int(r[4])
c1 = collections.defaultdict(lambda: [0, 0]); c7 = collections.defaultdict(lambda: [0, 0, 0]); c7days = collections.defaultdict(set)
for r in table('meta_camp_h12_1125_raw.json'):
    c1[cn(r[0])][0] += z(r[1]); c1[cn(r[0])][1] += z(r[3])
for r in table('meta_camp_h12_1118_1124_raw.json'):
    if z(r[2]) > 0: c7days[cn(r[1])].add(r[0])
    c7[cn(r[1])][0] += z(r[2]); c7[cn(r[1])][1] += z(r[4]); c7[cn(r[1])][2] += z(r[5])
P('■ 商品別（広告費が出ているキャンペーン全部＋カタログ）: 今日 0〜12時台 ↔ 11/18〜11/24 の同じ時刻')
P('  見込み＝7日（同じ時刻・広告を出した日だけ）の 注文÷広告費 × 今日の広告費。Shopify の注文は広告以外からの分も入る')
tot_e = 0
for c, (ad, clk) in sorted(c1.items(), key=lambda x: -x[1][0]):
    if ad == 0: continue
    if c.startswith('カタログ'):
        P(f'  {c}: 広告費 {ad:,}・{clk}クリック（商品に分けられない）'); continue
    o, q, net = p1.get(c, (0, 0, 0)); a7 = c7.get(c, [0, 0, 0]); po = p7.get(c, [0, 0, 0])
    days = len(c7days.get(c, ()))
    if a7[0] > 2000 and days >= 3:
        e = po[0] / a7[0] * ad; tot_e += e
        lo, hi = pois_le(e, o), 1 - pois_le(e, o - 1) if o > 0 else 1.0
        side = f'この数以下 {lo:.0%}' if o <= e else f'この数以上 {hi:.0%}'
        P(f'  {c}: 広告費 {ad:,}（7日の同じ時刻 平均 {a7[0]/days:,.0f}）・{o}注文{q}個・売上÷広告費 {net/ad:.2f}｜見込み {e:.1f}注文 → {side}｜7日 {po[0]}注文・{po[2]/a7[0]:.2f}（{days}日）')
    else:
        P(f'  {c}: 広告費 {ad:,}・{o}注文{q}個・売上÷広告費 {net/ad:.2f}｜7日の同じ時刻 広告費 {a7[0]:,}・{po[0]}注文（{days}日・比べるには少ない）')
noad = {n: v for n, v in p1.items() if n not in c1}
P('  広告を出していない商品（今日）: ' + ('・'.join(f'{n} {v[0]}注文{v[1]}個' for n, v in noad.items()) or 'なし'))
open(D0 + 'today_h12.txt', 'w').write('\n'.join(L) + '\n')
# 0〜18時台が終日の注文の何割か（11/17〜23・終日は data/daily/daily_order_bands.csv）
import csv
FULL = {r['date']: int(r['orders']) for r in csv.DictReader(open(D0 + '../../../../data/daily/daily_order_bands.csv'))}
w = [d for d in past if d >= '2026-11-18']
sh = sum(R[d]['o'] for d in w) / sum(FULL[d] for d in w)
P(f'■ 0〜12時台は終日の注文の {sh:.0%}（11/18〜24・' + '・'.join(f"{d[5:]} {R[d]['o']}/{FULL[d]}" for d in w) + '）')
open(D0 + 'today_h12.txt', 'w').write('\n'.join(L) + '\n')

# 入口別（今日 0〜12時台）と、クリック1回の値段
SRC = json.load(open(D0 + 'sess_source_h12_1125_raw.json'))['rows']
P('■ 入口別（今日 0〜12時台）: ' + '・'.join(f"{r[0]} 来訪 {r[1]}・カート {r[2]}・購入 {r[4]}（{int(r[4])/int(r[1]):.2%}）" for r in SRC if int(r[1]) >= 10))
ck = [(d, M[d][0] / M[d][2]) for d in past + [T] if M[d][2]]
P(f"■ クリック1回の値段（0〜12時台）: 今日 {dict(ck)[T]:.0f}円｜クリックが取れている {len(ck)-1}日 {min(v for d, v in ck if d != T):.0f}〜{max(v for d, v in ck if d != T):.0f}円（中央値 {st.median(v for d, v in ck if d != T):.0f}円）")
mp = sum(z(r[5]) for r in table('meta_camp_h12_1125_raw.json')); P(f'  Meta の購入（今日 0〜12時台・全キャンペーン）: {mp}件 ↔ Shopify の注文 {R[T]["o"]}件')
# 11/24 の広告費の確定値（13時台の取り直し）
fin = sum(z(r[1]) for r in table('meta_camp_1124_final_raw.json')); P(f'■ 11/24 の広告費: 0時台の暫定 196,086 → 13時台の取り直し {fin:,}（{fin-196086:+,}）※ CSV は明日の定例で直す')
open(D0 + 'today_h12.txt', 'w').write('\n'.join(L) + '\n')
# 広告費の出方: 0〜12時台までに、その日の広告費の何割を使ったか（終日は data/daily/daily_ad.csv。11/24 は 13時台の取り直し）
import csv as _csv
FULLAD = collections.Counter()
for r in _csv.DictReader(open(D0 + '../../../../data/daily/daily_ad.csv')): FULLAD[r['date']] += float(r['cost'])
FULLAD['2026-11-24'] = fin
w7 = [d for d in past if d >= '2026-11-18']
P('■ 広告費の出方（0〜12時台 ÷ 終日）: ' + '・'.join(f"{d[5:]} {M[d][0]/FULLAD[d]:.0%}" for d in w7) + f"｜今日 0〜12時台 {M[T][0]:,} ÷ 日予算の合計 186,000（00:2x の直読）＝{M[T][0]/186000:.0%}")
c1b = {cn(r[0]): z(r[1]) for r in table('meta_camp_h12_1125_raw.json')}
same = ('伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '快適マジックインソール', '4-in-1マルチクリーナー', '360°マルチクリップ車載スマホホルダー', 'カタログ全部（テスト）')   # 11/18 以降に日予算を変えていない（ガラスは 11/23 に +3,000）
P('  日予算をほぼ変えていない商品の 0〜12時台の広告費（今日 ÷ 7日の同じ時刻の平均）: ' + '・'.join(f"{n} {c1b[n]/(c7[n][0]/len(c7days[n])):.0%}" for n in same))
open(D0 + 'today_h12.txt', 'w').write('\n'.join(L) + '\n')
