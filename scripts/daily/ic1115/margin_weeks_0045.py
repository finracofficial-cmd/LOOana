# -*- coding: utf-8 -*-
"""利益率は下がっているか・なぜか（2026-11-15 00:4x ユーザー「利益率は低下してるよね。効率が悪くなってる証拠？なんで悪いの」）
data/daily の実測だけで、11/14 終端の7日ブロックを12週並べる。
利益率（利益÷実売）= 1 − 原価率 − 広告費率（1/売上÷広告費）に分け、どちらで動いたかを見る。"""
import csv, sys, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
NET = collections.defaultdict(int); AD = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
CO = collections.defaultdict(float)
for n in g['S']:
    for r in g['series'](n): CO[r['date']] += r['cost'] or 0
END = datetime.date(2026, 11, 14)
print('週（7日）           実売/日   広告費/日   利益/日  利益率  原価率 広告費率 売上÷広告費 倍率')
rows = []
for w in range(11, -1, -1):
    ds = [(END - datetime.timedelta(7 * w + k)).isoformat() for k in range(7)]
    assert all(d in AD and d in NET for d in ds), ds
    n = sum(NET[d] for d in ds); c = sum(CO[d] for d in ds); a = sum(AD[d] for d in ds); p = n - c - a
    assert abs(p / n - (1 - c / n - a / n)) < 1e-12
    rows.append((min(ds), max(ds), n, c, a, p))
    print(f'{min(ds)[5:]}〜{max(ds)[5:]}  {n/7:9,.0f} {a/7:10,.0f} {p/7:+9,.0f}  {p/n*100:5.1f}%  {c/n*100:5.1f}%  {a/n*100:5.1f}%     {n/a:5.2f}   {(n-c)/a:4.2f}')
print('\n利益率の変化の分け方（直近週 − 比べる週）: 利益率の差 = −(原価率の差) − (広告費率の差)')
L = rows[-1]
for k, lab in ((-2, '前週'), (-5, '4週前'), (0, '12週前')):
    B = rows[k]
    dm = L[5] / L[2] - B[5] / B[2]; dc = L[3] / L[2] - B[3] / B[2]; da = L[4] / L[2] - B[4] / B[2]
    print(f'  {lab}（{B[0][5:]}〜{B[1][5:]}）比: 利益率 {dm*100:+.1f}pt ＝ 原価率で {-dc*100:+.1f}pt ＋ 広告費率で {-da*100:+.1f}pt')
