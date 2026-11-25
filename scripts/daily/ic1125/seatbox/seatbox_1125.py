# -*- coding: utf-8 -*-
"""11/25 15時台「シートボックスは同じ動画でいいかな？V2で。」
入力: seatbox_daily_0801_1124_raw.json（Meta・広告A の日別）／seatbox_sales_daily_0806_1124_raw.json（Shopify・日別）／direct_seatbox_old_1510_raw.json（旧キャンペーンの直読）／w1124.py の原価
見るもの: 動画（広告A・0806.mp4 の1本だけ）のクリックの数字が、止める前と短い再開（10/29・11/11）でどうだったか。倍率＝クリック1回の粗利 ÷ クリック1回の値段"""
import json, csv, io, math, contextlib
B = 'scripts/daily/ic1125/seatbox/'
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1124.py').read(), g)
COST, PRICE = g['COST']['2WAYシートボックス'], g['PRICE']['2WAYシートボックス']
raw = json.load(open(B + 'seatbox_daily_0801_1124_raw.json', encoding='utf-8'))['data']['data']
head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
M = {}
for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines))):
    d = dict(zip(cols, r)); M[d['date']] = {k: (0.0 if d[k] in ('null', '') else float(d[k])) for k in cols[3:]}
S = {}
sh = json.load(open(B + 'seatbox_sales_daily_0806_1124_raw.json', encoding='utf-8'))
for day, orders, gross, disc, net in sh['rows']:
    q = float(gross) / PRICE; assert abs(q - round(q)) < 1e-9, (day, gross)
    S[day[:10]] = dict(o=int(orders), q=round(q), net=float(gross) + float(disc), gp=float(gross) + float(disc) - round(q) * COST)
def blk(days):
    days = [d for d in days if d in M]
    c, i, k, l, v3, a, p = (sum(M[d][x] for d in days) for x in ('cost', 'impressions', 'link_clicks', 'landing_page_views', 'action_video_view', 'offsite_conversions_fb_pixel_add_to_cart', 'offsite_conversions_fb_pixel_purchase'))
    o = sum(S[d]['o'] for d in days if d in S); q = sum(S[d]['q'] for d in days if d in S); gp = sum(S[d]['gp'] for d in days if d in S)
    return dict(n=len(days), c=c, i=i, k=k, o=o, q=q, gp=gp, cpm=c / i * 1000, ctr=k / i * 100, cpc=c / k, lpv=l / k, v3=v3 / i * 100, kv=k / v3 * 100, atc=a / k * 100, pm=p / k * 100, ok=o / k * 100, gpk=gp / k, m=gp / c)
def show(nm, x):
    print(f"  {nm}（{x['n']}日）: 広告費 {x['c']:,.0f}・注文 {x['o']}・{x['q']}個・倍率 {x['m']:.2f}｜CPM {x['cpm']:,.0f}・3秒まで見た÷表示 {x['v3']:.0f}%・クリック÷3秒 {x['kv']:.1f}%・クリック率 {x['ctr']:.2f}%・クリック1回 {x['cpc']:.0f}円・来訪÷クリック {x['lpv']:.2f}・カート÷クリック {x['atc']:.1f}%・注文÷クリック {x['ok']:.2f}%・クリック1回の粗利 {x['gpk']:.0f}円")
import datetime
def rng(a, b):
    a, b = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b); return [(a + datetime.timedelta(n)).isoformat() for n in range((b - a).days + 1)]
print(f'■ ① 広告A（動画 0806.mp4）の週ごと（原価 {COST:,}円・売価 {PRICE:,}円。注文・粗利は Shopify・その日の商品全体）')
W = [('8/6〜12', rng('2026-08-06', '2026-08-12')), ('8/13〜19', rng('2026-08-13', '2026-08-19')), ('8/20〜26', rng('2026-08-20', '2026-08-26')), ('8/27〜9/2', rng('2026-08-27', '2026-09-02')), ('9/3〜9/9', rng('2026-09-03', '2026-09-09'))]
for nm, ds in W: show(nm, blk(ds))
good = blk(rng('2026-08-06', '2026-08-27')); weak = blk(rng('2026-08-28', '2026-09-09')); allx = blk(rng('2026-08-06', '2026-09-10'))
print('■ ② 良かった時期と、止める前の2週')
show('8/6〜8/27', good); show('8/28〜9/9', weak); show('8/6〜9/10 の通算', allx)
def ratio(x1, n1, x2, n2):
    r = (x1 / n1) / (x2 / n2); s = math.sqrt(1 / x1 + 1 / x2); return f"{r:.2f}倍（幅 {r * math.exp(-2 * s):.2f}〜{r * math.exp(2 * s):.2f}）"
print(f"  止める前の2週 ÷ 良かった時期: クリック率 {ratio(weak['k'], weak['i'], good['k'], good['i'])}・注文÷クリック {ratio(weak['o'], weak['k'], good['o'], good['k'])}・CPM {weak['cpm'] / good['cpm']:.2f}倍・クリック1回 {weak['cpc'] / good['cpc']:.2f}倍・来訪÷クリック {weak['lpv'] / good['lpv']:.2f}倍・クリック1回の粗利 {weak['gpk'] / good['gpk']:.2f}倍")
print('■ ③ 短い再開（旧キャンペーンのまま・同じ投稿＝型 A。どちらも10時間未満）と、最初の日')
re = blk(['2026-10-29', '2026-11-11']); d1 = blk(['2026-08-06'])
show('10/29', blk(['2026-10-29'])); show('11/11', blk(['2026-11-11'])); show('10/29＋11/11', re); show('8/6（最初の日）', d1)
print(f"  再開の2日 ÷ 良かった時期: クリック率 {ratio(re['k'], re['i'], good['k'], good['i'])}・クリック1回 {re['cpc'] / good['cpc']:.2f}倍・CPM {re['cpm'] / good['cpm']:.2f}倍｜再開の2日 ÷ 最初の日（8/6）: クリック率 {ratio(re['k'], re['i'], d1['k'], d1['i'])}・クリック1回 {re['cpc'] / d1['cpc']:.2f}倍")
exp = re['k'] * good['ok'] / 100
print(f"  再開の2日のクリック {re['k']:.0f} に、良かった時期の 注文÷クリック {good['ok']:.2f}% を掛けると {exp:.1f}件。実際は {re['o']}件（ポアソンで {re['o']}件以下になる確率 {sum(math.exp(-exp) * exp ** j / math.factorial(j) for j in range(re['o'] + 1)) * 100:.0f}%）")
print('■ ④ 出し直しの見方: クリック1回の値段がいくらまでなら届くか')
for nm, x in (('通算', allx), ('良かった時期', good), ('止める前の2週', weak)):
    print(f"  クリック1回の粗利 {x['gpk']:.0f}円（{nm}）→ クリック1回 {x['gpk'] / 1.25:.0f}円まで 倍率1.25・{x['gpk'] / 1.5:.0f}円まで 1.5・{x['gpk'] / 1.86:.0f}円まで 1.86")
print(f"  事故停止の線（購入0のまま）: {(PRICE - COST) * 3:,}円")
a = json.load(open(B + 'direct_seatbox_old_1510_raw.json', encoding='utf-8'))['data']['data']['results'][0]; ad = a['ad_groups'][0]['ads'][0]; cr = ad['creative']
print(f"■ ⑤ 旧キャンペーンの広告（直読 15:1x）: {a['name']}（{a['campaign_id']}・{a['status']}）・広告 {ad['name']}（{ad['id']}）は1本だけ・動画 {cr['video_title']}（素材 {cr['asset_id']}）・ボタン {cr['call_to_action']}・見出し {len(cr['headlines'])}本・本文 {len(cr['descriptions'])}本・商品の拡張 {cr['degrees_of_freedom_spec']['creative_features_spec']['product_extensions']['enroll_status']}・リンク先 {cr['final_urls'][0]}")
odd = [w for w in ('忘れろ', '収纳', 'つれ込み', 'ストレスケアはもう終わり') if any(w in t for t in cr['descriptions'])]
print(f"  本文の候補に入っている不自然な言い回し: {odd}（{sum(any(w in t for w in odd) for t in cr['descriptions'])}本／{len(cr['descriptions'])}本）")
