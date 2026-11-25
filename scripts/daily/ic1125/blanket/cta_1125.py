# -*- coding: utf-8 -*-
"""11/25 15時台「ブランケットを新広告で v2 として 8,000円で出した。ボタン（CTA）を『詳しくはこちら』にしたので、その差を他の広告と今後比べたい」
入力（どれも Meta・Shopify の結果をそのまま保存したもの）:
  meta_ad_cta_0401_1124_raw.json  広告ごとのボタンの種類と 4/1〜11/24 の合計（ボタンは「今の設定」で、途中で変えた履歴は出ない）
  direct_blanket_v2_1455_raw.json / direct_blanket_v1_1500_raw.json  ブランケット v2・前回（v1）の直読
出すもの: ①ボタンの種類ごとの本数と広告費 ②「購入する」以外の広告 ③同じ広告セットの中でボタンが違う例 ④ブランケット v1 の数字（比べる相手）⑤7日で見分けられる差の大きさ"""
import json, csv, io, math, collections
B = 'scripts/daily/ic1125/blanket/'
raw = json.load(open(B + 'meta_ad_cta_0401_1124_raw.json', encoding='utf-8'))['data']['data']
head, *lines = raw.split('\n')
cols = head[head.index('{') + 1:head.index('}')].split(',')
rows = []
for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines))):
    d = dict(zip(cols, r))
    for k in cols[5:]: d[k] = 0.0 if d[k] in ('null', '') else float(d[k])
    d['cta'] = d['creative_call_to_action_type'] or '（空）'
    rows.append(d)
assert len(rows) == int(head[1:head.index(']')]), (len(rows), head[:10])
JA = {'SHOP_NOW': '購入する', 'LEARN_MORE': '詳しくはこちら', 'SEE_DETAILS': '詳細を見る', '（空）': '（値なし）'}
def m(rs):
    c, i, k, l, a, p, v = (sum(r[x] for r in rs) for x in ('cost', 'impressions', 'link_clicks', 'landing_page_views', 'offsite_conversions_fb_pixel_add_to_cart', 'offsite_conversions_fb_pixel_purchase', 'offsite_conversion_value_fb_pixel_purchase'))
    return dict(c=c, i=i, k=k, p=p, ctr=k / i * 100 if i else 0, cpc=c / k if k else 0, cpm=c / i * 1000 if i else 0, lpv=l / k if k else 0, atc=a / k * 100 if k else 0, pur=p / k * 100 if k else 0, roas=v / c if c else 0, cpa=c / p if p else 0)
def line(x): return f"広告費 {x['c']:,.0f}・表示 {x['i']:,.0f}・クリック {x['k']:,.0f}・購入 {x['p']:,.0f}｜クリック率 {x['ctr']:.2f}%・クリック1回 {x['cpc']:.0f}円・CPM {x['cpm']:,.0f}・来訪÷クリック {x['lpv']:.2f}・カート÷クリック {x['atc']:.1f}%・購入÷クリック {x['pur']:.2f}%・Meta の売上÷広告費 {x['roas']:.2f}・1購入 {x['cpa']:,.0f}円"

print('■ ① ボタンの種類ごと（4/1〜11/24 に広告費があった広告 %d本・ボタンは今の設定）' % len(rows))
by = collections.defaultdict(list)
for r in rows: by[r['cta']].append(r)
tot = sum(r['cost'] for r in rows)
for k, rs in sorted(by.items(), key=lambda x: -sum(r['cost'] for r in x[1])):
    print(f"  {JA.get(k, k)}（{k}）: {len(rs)}本・広告費 {sum(r['cost'] for r in rs):,.0f}（{sum(r['cost'] for r in rs) / tot * 100:.1f}%）")

print('■ ② 「購入する」以外の広告（広告費の多い順）')
for r in sorted([r for r in rows if r['cta'] != 'SHOP_NOW'], key=lambda r: -r['cost']):
    print(f"  {r['adcampaign_name']}／{r['adset_name']}／{r['ad_name']}（{JA.get(r['cta'], r['cta'])}）: " + line(m([r])))

print('■ ③ 同じ広告セットの中でボタンが違う例: UV歯ブラシ除菌器「A０９１８」（動画が同じかは分からない・時期も広告ごとに違う）')
uv = [r for r in rows if r['adset_name'] == 'UV歯ブラシ除菌器 A０９１８']
b = [r for r in uv if r['cta'] == 'SEE_DETAILS']; o = [r for r in uv if r['cta'] == 'SHOP_NOW']
assert len(b) == 1 and len(o) == 3, (len(b), len(o))
mb, mo = m(b), m(o)
print('  詳細を見る（広告B・1本）: ' + line(mb))
print('  購入する（同じ広告セットの3本の合計）: ' + line(mo))
def ratio(x1, n1, x2, n2):   # 率の比と、偶然のぶれを含めた幅（±2σ・件数から）
    r = (x1 / n1) / (x2 / n2); s = math.sqrt(1 / x1 + 1 / x2); return r, r * math.exp(-2 * s), r * math.exp(2 * s)
r1 = ratio(mb['k'], mb['i'], mo['k'], mo['i']); r2 = ratio(mb['p'], mb['k'], mo['p'], mo['k'])
print(f"  詳細を見る ÷ 購入する: クリック率 {r1[0]:.2f}倍（幅 {r1[1]:.2f}〜{r1[2]:.2f}）・購入÷クリック {r2[0]:.2f}倍（幅 {r2[1]:.2f}〜{r2[2]:.2f}）・CPM {mb['cpm'] / mo['cpm']:.2f}倍・クリック1回 {mb['cpc'] / mo['cpc']:.2f}倍・1購入の広告費 {mb['cpa'] / mo['cpa']:.2f}倍")

print('■ ④ ブランケット（比べる相手＝前回 v1・ボタン 購入する・11/13〜18）')
v1 = [r for r in rows if r['adcampaign_name'] == '3WAY着る電気ブランケット']; assert len(v1) == 1
m1 = m(v1); print('  v1 広告A: ' + line(m1))
def ad(f):
    c = json.load(open(B + f, encoding='utf-8'))['data']['data']['results'][0]; g = c['ad_groups'][0]; a = g['ads'][0]; cr = a['creative']; fs = cr['degrees_of_freedom_spec']['creative_features_spec']
    on = lambda k: (fs.get(k) or {}).get('enroll_status', '—')
    return f"{c['name']}（{c['campaign_id']}・{c['status']}）／広告セット {g['ad_group_id']}・日予算 {g['daily_budget']:,}／広告 {a['name']}（{a['id']}・審査 {a['review']['status']}）｜ボタン {cr['call_to_action']}・動画 {cr['video_title']}（素材 {cr['asset_id']}）・見出し {len(cr['headlines'])}本・本文 {len(cr['descriptions'])}本・商品の拡張 {on('product_extensions')}・商品閲覧 {on('product_browsing')}・CTA の強化 {on('enhance_cta')}・Advantage+ クリエイティブ {on('advantage_plus_creative')}"
print('  v1 の設定: ' + ad('direct_blanket_v1_1500_raw.json'))
print('  v2 の設定: ' + ad('direct_blanket_v2_1455_raw.json'))
c1 = json.load(open(B + 'direct_blanket_v1_1500_raw.json', encoding='utf-8'))['data']['data']['results'][0]['ad_groups'][0]['ads'][0]['creative']
c2 = json.load(open(B + 'direct_blanket_v2_1455_raw.json', encoding='utf-8'))['data']['data']['results'][0]['ad_groups'][0]['ads'][0]['creative']
txt = ' '.join(c2['headlines'] + c2['descriptions'])
other = [w for w in ('ワイパー', 'ノーズ', 'フック', 'インソール', 'クリーナー', 'ホルダー', 'ドア', 'フィルム', 'チェア', '加湿', '脱毛', 'ガラス') if w in txt]
print(f"  v2 の見出し・本文にほかの商品の言葉: {other if other else 'なし'}｜v1 と同じ本文 {len(set(c1['descriptions']) & set(c2['descriptions']))}本・同じ見出し {len(set(c1['headlines']) & set(c2['headlines']))}本｜リンク先は同じ: {c1['final_urls'] == c2['final_urls']}")

print('■ ⑤ 7日（8,000円/日）でどこまで見分けられるか（v1 のクリック1回の値段・率が続いた場合の件数から。±2σ）')
k2 = 8000 * 7 / m1['cpc']; p2 = k2 * m1['pur'] / 100; a2 = k2 * m1['atc'] / 100
for nm, x1, x2 in (('クリック率', m1['k'], k2), ('カート÷クリック', m1['k'] * m1['atc'] / 100, a2), ('購入÷クリック', m1['p'], p2)):
    s = math.sqrt(1 / x1 + 1 / x2); print(f"  {nm}: v1 {x1:.0f}件・v2 の見込み {x2:.0f}件 → ×{math.exp(-2 * s):.2f}〜×{math.exp(2 * s):.2f} の中は偶然と区別できない")

print('■ ⑥ ブランケット v1 のクリック1回の粗利（Shopify の粗利 ÷ Meta のリンククリック。stopped_1125.json・11/13〜18）')
st = {r['n']: r for r in json.load(open(B + 'stopped_1125.json', encoding='utf-8'))}['3WAY着る電気ブランケット']
gpc = st['gp'] / m1['k']
print(f"  広告費 {st['ad']:,.0f}・粗利 {st['gp']:,.0f}・倍率 {st['m']:.2f}・クリック {m1['k']:,.0f} → クリック1回の粗利 {gpc:.0f}円｜同じ買われ方なら クリック1回 {gpc / 1.25:.0f}円まで 倍率1.25・{gpc / 1.5:.0f}円まで 1.5・{gpc / 1.86:.0f}円まで 1.86（v1 は {m1['cpc']:.0f}円）")
