# -*- coding: utf-8 -*-
"""11/13(金) 15:5x 「売れそうな商品をこれまでのデータから見つけてきて」
①保温プレートの月別（2026年1〜6月・Shopify＋Meta・原価3,703円＝元の商品の unitCost）②9/15以降に再開した過去の当たり（data/daily）"""
import os, csv, sys, json, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
RAW = json.load(open(D + 'candidates_1550_raw.json'))
COST, PRICE = 3703, 8990
ME = {}
for r in RAW['meta_month_hoon_nanobubble_blanket']['rows']:
    ym, c, co, im, cl, pu = r.split(',')
    if c == '保温プレート': ME[ym.replace('|', '-')] = (int(co), int(im), int(cl))
print('■ 保温プレート（8,990円・原価3,703円）月別')
tot = [0, 0, 0]
for m, g, dsc, n, o in RAW['shop_hoon_month']['rows']:
    ym = m[:7]; g, dsc = int(g), -int(dsc); u = g // PRICE; assert g % PRICE == 0, (m, g)
    if ym not in ME: continue
    co, im, cl = ME[ym]; gp = g - dsc - u * COST
    if '2026-01' <= ym <= '2026-03': tot[0] += gp; tot[1] += co
    print(f"  {ym}: {u}個・実売 {g-dsc:,}・広告費 {co:,}・倍率 {gp/co:.2f}・利益 {gp-co:+,}・クリック率 {cl/im*100:.2f}%")
print(f"  1〜3月: 倍率 {tot[0]/tot[1]:.2f}・利益 {tot[0]-tot[1]:+,}（{(tot[0]-tot[1])/90:+,.0f}/日）")
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
print('\n■ 9/15以降に再開した、春夏の当たり（広告費500円以上の日だけ）')
for n in ['姿勢サポートチェア', '携帯電動シェーバー', 'ナノバブルシャワーヘッド', 'バランスケアスリッパ', 'UV歯ブラシ除菌器', 'ネックマッサージャー', '壁掛けディスペンサー', 'ムダ毛シェーバー', '健康サンダル']:
    runs = [r for r in g['series'](n) if r['date'] >= '2026-09-15' and r['ad'] >= 500]
    ad = sum(r['ad'] for r in runs); gp = sum(r['sales'] - (r['cost'] or 0) for r in runs)
    print(f"  {n}: {len(runs)}日・広告費 {ad:,.0f}・倍率 {gp/ad:.2f}・利益 {gp-ad:+,.0f}")
