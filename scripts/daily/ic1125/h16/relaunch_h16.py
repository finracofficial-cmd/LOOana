# -*- coding: utf-8 -*-
"""11/25 16:5x「広告で復活させた商品まだ売れないね…」: 出し直した4本（フィルム v2・チェア v2・ブランケット v2・シートボックス v2）の、出してから今までの数字。
日中の数字なので、倍率や買う率では判断しない。配信の数字・注文の件数と、「前の出稿の 購入÷クリック なら何件の見込みか」だけを見る。
入力: meta_ad_1125_h16_raw.json（今日・広告別・16時台の途中まで）／meta_hourly_v2_1123_1125_raw.json（v2 の4本の時間別）／meta_chair_0804_0812_raw.json（チェアの8月の出だし）
      sales_prod_1125_h16_raw.json・sess_landing_1124_1125_raw.json（Shopify）／../blanket/meta_ad_cta_0401_1124_raw.json（前の出稿の広告別の合計）"""
import json, csv, io, math, re, collections
B = 'scripts/daily/ic1125/h16/'
def table(path):
    raw = json.load(open(path, encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
    out = []
    for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines))):
        d = dict(zip(cols, r)); out.append({k: (v if not re.fullmatch(r'-?\d+(\.\d+)?|null|', v) else (0.0 if v in ('null', '') else float(v))) for k, v in d.items()})
    assert len(out) == int(head[1:head.index(']')]); return out
C, K, L, A, P = 'cost', 'link_clicks', 'landing_page_views', 'offsite_conversions_fb_pixel_add_to_cart', 'offsite_conversions_fb_pixel_purchase'
today = table(B + 'meta_ad_1125_h16_raw.json'); hourly = table(B + 'meta_hourly_v2_1123_1125_raw.json'); old = table('scripts/daily/ic1125/blanket/meta_ad_cta_0401_1124_raw.json'); chair8 = table(B + 'meta_chair_0804_0812_raw.json')
sales = {r[0]: (int(r[1]), float(r[2]), int(r[4])) for r in json.load(open(B + 'sales_prod_1125_h16_raw.json', encoding='utf-8'))['rows']}
sess = {r[0]: tuple(int(x) for x in r[1:]) for r in json.load(open(B + 'sess_landing_1124_1125_raw.json', encoding='utf-8'))['rows']}
def shop(name):
    hit = [v for t, v in sales.items() if name in t]; return (sum(h[0] for h in hit), sum(h[2] for h in hit))
def pois_le(k, mu): return sum(math.exp(-mu) * mu ** j / math.factorial(j) for j in range(k + 1))
# 前の出稿（広告別の合計）から 購入÷クリック・クリック1回 を出す
def prev(camp, adset=None):
    rs = [r for r in old if r['adcampaign_name'] == camp and (adset is None or r['adset_name'] == adset)]; assert rs, camp
    c, k, p, i = (sum(r[x] for r in rs) for x in (C, K, P, 'impressions')); return dict(c=c, k=k, p=p, rate=p / k, cpc=c / k, ctr=k / i * 100)
V2 = [('クリアビューレインガードフィルムv2', 'クリアビューレインガードフィルム', prev('クリアビューレインガードフィルム', 'クリアビューレインガードフィルム'), '/products/waterproof-film-for-car-rearview-mirror'),
      ('姿勢サポートチェアv2', '姿勢サポートチェア', prev('姿勢サポートチェア', '姿勢サポートチェア'), '/products/student-children-cushion-chair-waist-support'),
      ('3WAY着る電気ブランケットv2', '3WAY着る電気ブランケット', prev('3WAY着る電気ブランケット'), '/products/outdoor-warming-heated-blanket-shawl'),
      ('2WAYシートボックスv2', '2WAYシートボックス', prev('2WAYシートボックス'), '/products/car-seat-storage-box-with-lumbar-support')]
print('■ ① 出し直した4本: 出してから今まで（Meta・11/25 は16時台の途中まで）と、前の出稿の 購入÷クリック なら何件の見込みか')
for camp, prod, pv, path in V2:
    hs = [r for r in hourly if r['adcampaign_name'] == camp]
    first = min((r['date'], r['hourly_stats_aggregated_by_advertiser_time_zone'][:2]) for r in hs)
    c, i, k, l, a, p = (sum(r[x] for r in hs) for x in (C, 'impressions', K, L, A, P))
    t = [r for r in today if r['adcampaign_name'] == camp]; ct, kt, pt = (sum(r[x] for r in t) for x in (C, K, P))
    hrs = len(hs); mu = k * pv['rate']; so, sq = shop(prod)
    s = sess.get(path, (0, 0, 0, 0))
    print(f"  {camp}: 最初の配信 {first[0][5:]} {first[1]}時台・配信のあった時間 {hrs}時間｜通算 広告費 {c:,.0f}・表示 {i:,.0f}・クリック {k:.0f}（クリック率 {k / i * 100:.2f}%・クリック1回 {c / k if k else 0:.0f}円）・来訪 {l:.0f}・カート {a:.0f}・購入 {p:.0f}（Meta）｜今日だけ 広告費 {ct:,.0f}・クリック {kt:.0f}・Meta 購入 {pt:.0f}・Shopify {so}注文 {sq}個")
    print(f"      前の出稿: 購入÷クリック {pv['rate'] * 100:.2f}%（{pv['p']:.0f}件／{pv['k']:,.0f}クリック）・クリック率 {pv['ctr']:.2f}%・クリック1回 {pv['cpc']:.0f}円 → 今のクリック {k:.0f} なら見込み {mu:.1f}件・{p:.0f}件以下になる確率 {pois_le(int(p), mu) * 100:.0f}%｜1件に要るクリック {1 / pv['rate']:.0f}回＝今のクリック1回の値段で {(c / k if k else 0) / pv['rate']:,.0f}円")
    print(f"      Shopify の商品ページに着いた来訪（11/24〜25）: {s[0]}・カート {s[1]}・決済画面 {s[2]}・購入 {s[3]}")
print('■ ② チェアの8月の出だし（広告セット「姿勢サポートチェア」・日別）: クリック1回の値段')
for r in chair8:
    if r['adset_name'] == '姿勢サポートチェア': print(f"  {r['date'][5:]}: 広告費 {r[C]:,.0f}・クリック {r[K]:.0f}・クリック1回 {r[C] / r[K]:.0f}円・クリック率 {r[K] / r['impressions'] * 100:.2f}%・購入 {r[P]:.0f}")
f4 = [r for r in chair8 if r['adset_name'] == '姿勢サポートチェア' and r['date'] <= '2026-08-07']
print(f"  最初の4日（8/4〜7）: クリック1回 {sum(r[C] for r in f4) / sum(r[K] for r in f4):.0f}円・購入 {sum(r[P] for r in f4):.0f}件／クリック {sum(r[K] for r in f4):.0f}")
st = {r['n']: r for r in json.load(open('scripts/daily/ic1125/blanket/stopped_1125.json', encoding='utf-8'))}['姿勢サポートチェア']
pc = prev('姿勢サポートチェア', '姿勢サポートチェア'); gpk = st['m'] * pc['cpc']
print(f"  チェアのクリック1回の粗利（通算の倍率 {st['m']:.2f} × 前の出稿のクリック1回 {pc['cpc']:.0f}円）: {gpk:.0f}円 → クリック1回 {gpk / 1.25:.0f}円まで 倍率1.25・{gpk / 1.5:.0f}円まで 1.5")
print('■ ③ 今日 0〜16時台の途中まで・広告費が出ている全商品（判断には使わない。件数だけ）')
agg = collections.defaultdict(lambda: [0, 0, 0])
for r in today:
    a = agg[r['adcampaign_name']]; a[0] += r[C]; a[1] += r[K]; a[2] += r[P]
tot = [0, 0]
for camp, (c, k, p) in sorted(agg.items(), key=lambda x: -x[1][0]):
    prod = re.sub(r'\s*v\d+$', '', camp); so, sq = shop(prod) if 'カタログ' not in camp else ('—', '—')
    print(f"  {camp}: 広告費 {c:,.0f}・クリック {k:.0f}・Meta 購入 {p:.0f}｜Shopify {so}注文 {sq}個"); tot[0] += c
allo = sum(v[0] for t, v in sales.items() if t and 'VIP' not in t and t != '優先配送')
print(f"  合計: 広告費 {tot[0]:,.0f}｜Shopify の注文（商品の行の合計・重なりあり）{allo}・広告なしで売れた商品: " + '・'.join(f"{t.split('LOOTY')[-1].split('【')[0].strip()} {v[0]}" for t, v in sales.items() if t and 'VIP' not in t and t != '優先配送' and not any(re.sub(r'\s*v\d+$', '', c) in t for c in agg)))
