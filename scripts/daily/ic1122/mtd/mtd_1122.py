# -*- coding: utf-8 -*-
"""11/22 「11月の21日時点までの売上、原価、広告費、利益、手数料控除後利益は？」
11/1〜11/21 の合計。売上・原価は scripts/daily/w1121.py の積み直し（data/daily/*.csv）。広告費は CSV の 11/21（暫定 183,007）を 11/22 09時台に取り直した確定値に置き換える。
照合: Shopify の店全体（store_1101_1121_raw.json）・Meta のアカウント日別（meta_acct_daily_1101_1121_raw.json）。
手数料は 実売 × 3.325%（11/2 に直近100注文で測った割合）の計算値で、実際に引かれた額そのものではない"""
import io, contextlib, json, os
D0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(D0, '..', '..', '..', '..'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1121.py').read(), g)
CUM, NC, KC, DCC, ACCT, AD = g['CUM'], g['NC'], g['KC'], g['DCC'], g['ACCT'], g['AD']
assert CUM[0] == '2026-11-01' and CUM[-1] == '2026-11-21' and len(CUM) == 21
FEE = 0.03325
def table(f):
    return [l.strip().split(',') for l in json.load(open(os.path.join(D0, f)))['data']['data'].split('\n')[1:] if l.strip()]
st = json.load(open(os.path.join(D0, 'store_1101_1121_raw.json')))['rows'][0]
gross, disc, ret, orders = int(st[0]), -int(st[1]), -int(st[2]), int(st[3])
sales = sum(NC.values()); cogs = sum(KC.values())
assert sales == gross - disc, (sales, gross - disc)            # CSV の積み上げ ＝ Shopify の店全体（11/22 09時台の直読）
assert sum(DCC.values()) == disc
fin = {r[1]: int(r[2]) for r in table('meta_camp_1121_final_raw.json')}; f21 = sum(fin.values())
p21 = ACCT(['2026-11-21']); assert abs(p21 - 183007) < 1
assert set(fin) == {c for c in AD if AD[c].get('2026-11-21', 0)}, 'キャンペーンの顔ぶれが違う'
ad = ACCT(CUM) - p21 + f21
acct = {r[0]: int(r[1]) for r in table('meta_acct_daily_1101_1121_raw.json')}; assert len(acct) == 21 and acct['2026-11-21'] == f21
profit = sales - cogs - ad; fee = sales * FEE
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
P('■ 2026年11月 1日〜21日（21日間）')
P(f'  売上（総額 {gross:,} − 値引き {disc:,}）: {sales:,}円（{sales/21:,.0f}/日・注文 {orders:,}件）')
P(f'  原価: {cogs:,.0f}円（売上の {cogs/sales:.1%}）')
P(f'  広告費: {ad:,.0f}円（売上の {ad/sales:.1%}・{ad/21:,.0f}/日）')
P(f'  利益: {profit:,.0f}円（売上の {profit/sales:.1%}・{profit/21:,.0f}/日）')
P(f'  決済手数料（売上 × {FEE:.3%}・計算値）: {fee:,.0f}円')
P(f'  手数料控除後利益: {profit-fee:,.0f}円（売上の {(profit-fee)/sales:.1%}・{(profit-fee)/21:,.0f}/日）')
P(f'  売上÷広告費 {sales/ad:.2f}・倍率（（売上−原価）÷広告費） {(sales-cogs)/ad:.2f}')
P('')
P('■ 確かめたこと')
P(f'  売上: 日別ファイルの合計 {sales:,} ＝ Shopify の店全体（11/22 09時台）{gross-disc:,}（差 0）')
P(f'  広告費: 11/21 を暫定 {p21:,.0f} → 確定 {f21:,}（{f21-p21:+,.0f}）に置き換えた。Meta のアカウント日別を今取り直した合計は {sum(acct.values()):,}（差 {sum(acct.values())-ad:+,.0f}・{(sum(acct.values())-ad)/ad:+.3%}）')
P(f'  返品（売上・利益からは引いていない）: {ret:,}円')
P(f'  11/21 の1日（確定）: 利益 {sum(g["N1"].values())-sum(g["K1"].values())-f21:,.0f}円')
open(os.path.join(D0, 'mtd_1122.txt'), 'w').write('\n'.join(L) + '\n')
