# -*- coding: utf-8 -*-
"""11/26 17時台「ブラシを既存の広告セットで再開させてみた」
入力: meta_history_1126_1724_raw.json（Meta の変更履歴・11/26 UTC）／direct_brush_1721_raw.json（キャンペーンの直読）／
      brush_daily_1023_1126_raw.json（Meta・広告別の日別）／brush_sales_daily_1023_1126_raw.json（Shopify・日別）／w1125.py の原価・売価／data/relaunch-log.csv
見るもの: ①今日の操作（時刻）②いま配信される広告 ③ブラシの過去（週ごと・広告A/B）④クリック1回の粗利から出した線 ⑤型 A の過去"""
import json, csv, io, math, contextlib, datetime, statistics as st, os
B = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(B + '../../../..')
out = []
def P(s=''): print(s); out.append(s)
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1125.py').read(), g)
NM = '伸縮ワックス洗車ブラシ'; COST, PRICE = g['COST'][NM], g['PRICE'][NM]
# ---- ① 今日の操作 ----
H = json.load(open(B + 'meta_history_1126_1724_raw.json', encoding='utf-8'))['data']['data']['results']['platform_change_list']
jst = lambda t: (datetime.datetime.strptime(t[:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9)).strftime('%H:%M:%S')
IDS = {'52579156021612': 'キャンペーン', '52579156022012': '広告セット', '52579156021812': '広告A', '52585388644212': '広告B'}
P('■ ① 今日の操作（Meta の変更履歴・日本時間。操作した人の名前は書かない）')
bud = None; cre = None
for e in sorted(H, key=lambda e: e['timestamp']):
    if e['campaign_id'] not in IDS: continue
    v = e['change_values']; who = 'Meta' if e['actor_name'] == 'Meta' else 'ユーザー'
    if e['operation'] == 'UPDATE_AD_SET_BUDGET': bud = (v['old_value']['old_value'], v['new_value']['new_value']); txt = f"日予算 {bud[0]:,} → {bud[1]:,}"
    elif e['operation'] == 'UPDATE_AD_CREATIVE':
        o, n = v['old_value'], v['new_value']; cre = (o[-1], n[-1])
        same = [o[i] == n[i] for i in (1, 2)]; thumb = o[0].split('?')[0] == n[0].split('?')[0]
        txt = f"クリエイティブの更新: ID {o[-1]} → {n[-1]}｜見出し同じ={same[0]}・本文（1本目）同じ={same[1]}・サムネイルの画像同じ={thumb}"
    else: txt = f"{v.get('old_value')} → {v.get('new_value')}" + ('（審査後の状態の予約）' if 'AFTER_REVIEW' in e['operation'] else '')
    P(f"  {jst(e['timestamp'])} {IDS[e['campaign_id']]}: {txt}（{who}）")
# ---- ② 直読 ----
c = json.load(open(B + 'direct_brush_1721_raw.json', encoding='utf-8'))['data']['data']['results'][0]; ag = c['ad_groups'][0]
P(f"■ ② 直読（17:21）: キャンペーン {c['name']}（{c['campaign_id']}）{c['status']}・広告セット {ag['status']}・日予算 {ag['daily_budget']:,}円・開始日 {c['start_date']}")
assert ag['daily_budget'] == bud[1]
for ad in ag['ads']:
    cr = ad['creative']; f = cr['degrees_of_freedom_spec']['creative_features_spec']; post = [t['post'][0] for t in ad['platform_settings']['tracking_specs'] if 'post' in t][0]
    oth = [w for w in ('ノーズ', 'フック', 'インソール', 'ワイパー', 'ガラス', 'シート', 'ブランケット') if any(w in t for t in cr['descriptions'] + cr['headlines'])]
    P(f"  広告{ad['name']}（{ad['id']}）: {ad['status']}・審査 {ad['review']['status']}・動画 {cr['video_title']}（素材 {cr['asset_id']}）・クリエイティブ {ad['creative_id']}・投稿 {post}・ボタン {cr['call_to_action']}・見出し {len(cr['headlines'])}本・本文 {len(cr['descriptions'])}本（全部に「洗車ブラシ」={all('洗車ブラシ' in t for t in cr['descriptions'])}・他の商品の言葉 {oth or 'なし'}）・商品の拡張 {f['product_extensions']['enroll_status']}・商品閲覧 {f['product_browsing']['enroll_status']}・リンク先 {cr['final_urls'][0].split('/')[-1]}")
A_ = [a for a in ag['ads'] if a['name'] == 'A'][0]; assert A_['creative_id'] == cre[1]
# ---- ③ 過去 ----
raw = json.load(open(B + 'brush_daily_1023_1126_raw.json', encoding='utf-8'))['data']['data']
head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
M = {}
for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines))):
    d = dict(zip(cols, r)); M[(d['date'], d['ad_name'])] = {k: (0.0 if d[k] in ('null', '') else float(d[k])) for k in cols[3:]}
S = {}
for day, orders, gross, disc, net in json.load(open(B + 'brush_sales_daily_1023_1126_raw.json', encoding='utf-8'))['rows']:
    q = float(gross) / PRICE; assert abs(q - round(q)) < 1e-9, (day, gross)
    S[day[:10]] = dict(o=int(orders), q=round(q), gp=float(gross) + float(disc) - round(q) * COST)
def rng(a, b):
    a, b = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b); return [(a + datetime.timedelta(n)).isoformat() for n in range((b - a).days + 1)]
KEYS = ('cost', 'impressions', 'link_clicks', 'landing_page_views', 'action_video_view', 'offsite_conversions_fb_pixel_add_to_cart', 'offsite_conversions_fb_pixel_purchase')
def blk(days, ads=('A', 'B')):
    c_, i, k, l, v3, a, p = (sum(M.get((d, x), {}).get(f, 0) for d in days for x in ads) for f in KEYS)
    o = sum(S[d]['o'] for d in days if d in S); q = sum(S[d]['q'] for d in days if d in S); gp = sum(S[d]['gp'] for d in days if d in S)
    return dict(n=len(days), c=c_, i=i, k=k, o=o, q=q, gp=gp, p=p, cpm=c_ / i * 1000, ctr=k / i * 100, cpc=c_ / k, lpv=l / k, v3=v3 / i * 100, ok=o / k * 100, pm=p / k * 100, gpk=gp / k, m=gp / c_, gpo=gp / o if o else 0)
def show(nm, x):
    P(f"  {nm}（{x['n']}日）: 広告費 {x['c']:,.0f}（{x['c']/x['n']:,.0f}/日）・注文 {x['o']}・{x['q']}個・倍率 {x['m']:.2f}・利益 {(x['gp']-x['c'])/x['n']:+,.0f}/日｜CPM {x['cpm']:,.0f}・3秒まで見た÷表示 {x['v3']:.0f}%・クリック率 {x['ctr']:.2f}%・クリック1回 {x['cpc']:.0f}円・来訪÷クリック {x['lpv']:.2f}・注文÷クリック {x['ok']:.2f}%・クリック1回の粗利 {x['gpk']:.0f}円")
P(f'■ ③ ブラシの過去（原価 {COST:,}円・売価 {PRICE:,}円。注文・粗利は Shopify・その日の商品全体。広告は A＋B）')
W = [('10/23〜29', rng('2026-10-23', '2026-10-29')), ('10/30〜11/5', rng('2026-10-30', '2026-11-05')), ('11/6〜12', rng('2026-11-06', '2026-11-12')), ('11/13〜17', rng('2026-11-13', '2026-11-17'))]
for nm, ds in W: show(nm, blk(ds))
allx = blk(rng('2026-10-23', '2026-11-17')); good = blk(rng('2026-10-23', '2026-11-05')); late = blk(rng('2026-11-06', '2026-11-17')); show('通算 10/23〜11/17', allx); show('最初の2週', good); show('止める前の12日', late)
def ratio(x1, n1, x2, n2):
    r = (x1 / n1) / (x2 / n2); s = math.sqrt(1 / x1 + 1 / x2); return f"{r:.2f}倍（幅 {r * math.exp(-2 * s):.2f}〜{r * math.exp(2 * s):.2f}）"
P(f"  止める前の12日 ÷ 最初の2週: クリック率 {ratio(late['k'], late['i'], good['k'], good['i'])}・注文÷クリック {ratio(late['o'], late['k'], good['o'], good['k'])}・CPM {late['cpm']/good['cpm']:.2f}倍・クリック1回 {late['cpc']/good['cpc']:.2f}倍・3秒まで見た÷表示 {good['v3']:.0f}% → {late['v3']:.0f}%")
P('  広告別（11/13〜17。B は 11/13 に追加。Meta 計上の購入は広告別・Shopify の注文は分けられない）')
for ad in ('A', 'B'):
    x = blk(rng('2026-11-13', '2026-11-17'), (ad,)); tot = blk(rng('2026-11-13', '2026-11-17'))
    P(f"    {ad}: 広告費 {x['c']:,.0f}（{x['c']/tot['c']:.0%}）・クリック率 {x['ctr']:.2f}%・クリック1回 {x['cpc']:.0f}円・来訪÷クリック {x['lpv']:.2f}・購入（Meta）{x['p']:.0f}・購入÷クリック {x['pm']:.2f}%")
xa = blk(rng('2026-10-23', '2026-11-12'), ('A',)); xa2 = blk(rng('2026-11-13', '2026-11-16'), ('A',))
P(f"    A だけの流れ: 10/23〜11/12 クリック率 {xa['ctr']:.2f}%・クリック1回 {xa['cpc']:.0f}円・購入÷クリック（Meta）{xa['pm']:.2f}% → 11/13〜16 {xa2['ctr']:.2f}%・{xa2['cpc']:.0f}円・{xa2['pm']:.2f}%（{xa2['p']:.0f}件）")
last = [d for d in sorted(S) if d > '2026-11-17']; P(f"  広告を止めたあと（11/18〜26）の Shopify: {[(d[5:], S[d]['o'], S[d]['q']) for d in last]}（日・注文・個数）")
# ---- ④ 線 ----
P('■ ④ 再開の見方: クリック1回の値段がいくらまでなら届くか（倍率＝クリック1回の粗利 ÷ クリック1回の値段）')
for nm, x in (('通算', allx), ('最初の2週', good), ('止める前の12日', late)):
    P(f"  クリック1回の粗利 {x['gpk']:.0f}円（{nm}）→ クリック1回 {x['gpk']/1.25:.0f}円まで 倍率1.25・{x['gpk']/1.5:.0f}円まで 1.5・{x['gpk']/1.86:.0f}円まで 1.86")
P(f"  1注文の粗利: 通算 {allx['gpo']:,.0f}円（1注文 {allx['q']/allx['o']:.2f}個）・止める前の12日 {late['gpo']:,.0f}円")
b = ag['daily_budget']
for m_ in (1.25, 1.5):
    P(f"  日予算 {b:,}円を使い切る日に 倍率 {m_} に要る粗利 {b*m_:,.0f}円 ＝ 注文 {b*m_/allx['gpo']:.1f}件（1注文の粗利 {allx['gpo']:,.0f}円で）")
for m_ in (1.25, 1.5): P(f"  通算の倍率 {m_} ＝ 広告費 1万円あたり 注文 {10000*m_/allx['gpo']:.1f}件")
P(f"  事故停止の線（基準6・購入0のまま）: {(PRICE-COST)*3:,}円")
# ---- ⑤ 型 A の過去 ----
R = [r for r in csv.DictReader(open('data/relaunch-log.csv', encoding='utf-8', newline='')) if r['版'] == '旧キャンペーンで再開']
f_ = lambda s: None if s in ('', '—') else float(s)
d12 = [f_(r['1〜2日目の倍率']) for r in R if f_(r['1〜2日目の倍率']) is not None]; d7 = [f_(r['7日の倍率']) for r in R if f_(r['7日の倍率']) is not None]
P(f"■ ⑤ 型 A（旧キャンペーンで再開）の過去（data/relaunch-log.csv・{len(R)}回）: 1〜2日目の倍率 中央値 {st.median(d12):.2f}（{len(d12)}回）｜7日まで続いたのは {len(d7)}回・その7日の倍率 中央値 {st.median(d7):.2f}（{min(d7):.2f}〜{max(d7):.2f}）")
P(f"  ブラシの止める前: 通算 {allx['m']:.2f}・最後の7日（11/11〜17）{blk(rng('2026-11-11','2026-11-17'))['m']:.2f}・休ませた日数 {(datetime.date(2026,11,26)-datetime.date(2026,11,18)).days}日（最後にまとまった広告費が出たのは 11/17）")
open(B + 'brush_1126.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
