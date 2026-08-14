# -*- coding: utf-8 -*-
"""自動推薦のまま出す場合、「推薦されうる商品」を減らすと上位4枠がどう入れ替わるかを試算する。

⚠️ これは実測ではなく【試算】。実測した各商品の上位10件から、除外した商品を落として
   上位4件を取り直しただけ。実際のShopifyは11位以下を繰り上げてくるので、
   除外数が多いケースほど誤差が出る（枠が埋まらない行数を併記する）。
"""
import json, collections

D = json.load(open('/tmp/reco_viz.json', encoding='utf-8'))
SRC, SLOT = D['sources'], D['slots']
def band(x):
    if not x['adv'] or x['roi'] is None: return 'none'
    r = x['roi']
    return 'neg' if r < 0 else 'low' if r < 0.25 else 'mid' if r < 0.60 else 'high'

# 2026-08-01〜13 に1件も売れていない商品（Shopify実測。広告も出していない）
DEAD = {'癒しの指圧マット', 'スタイルアップインナー', '姿勢サポートベルト',
        'ネックマッサージャー', '保温プレート', 'オートソープディスペンサー'}
SEASON = {s['name'] for s in SLOT if s['season']}

def simulate(drop, label):
    top = collections.Counter(); short = 0; total = 0
    for s in SRC:
        keep = [r for r in s['recs'] if r['name'] not in drop][:4]
        if len(keep) < 4: short += 1
        for r in keep: top[r['name']] += 1; total += 1
    seas = sum(v for n, v in top.items() if n in SEASON)
    noad = sum(v for n, v in top.items() if any(x['name'] == n and not x['adv'] for x in SLOT))
    win  = sum(v for n, v in top.items()
               if any(x['name'] == n and band(x) == 'high' for x in SLOT))
    print(f"\n■ {label}")
    print(f"   上位4枠 {total} 枠（10件から取り直したため枠が埋まらない行 {short}/{len(SRC)}）")
    print(f"   季節商品      {seas:>3}枠 = {seas/total:>5.1%}")
    print(f"   広告なし商品  {noad:>3}枠 = {noad/total:>5.1%}")
    print(f"   勝ち組(+0.60円以上) {win:>3}枠 = {win/total:>5.1%}")
    return top

simulate(set(), '① 今のまま自動推薦を出す【実測】')
simulate(DEAD, '② 13日間ゼロ販売の6商品をオンラインストアから外してから出す【試算】')
simulate(DEAD | SEASON, '③ 9月に季節商品も外したあと【試算】')

print('\n■ ②で外す6商品（8/01-13 販売ゼロ・広告ゼロ）が、いま持っている枠')
by = {s['name']: s for s in SLOT}
for n in sorted(DEAD, key=lambda x: -by.get(x, {}).get('top4', 0)):
    b = by.get(n, {'all': 0, 'top4': 0})
    print(f"   {n:<22} 上位4枠 {b['top4']:>2}回 / 全体 {b['all']:>2}回")
print(f"   計 上位4枠 {sum(by.get(n,{}).get('top4',0) for n in DEAD)} / 140 枠")
