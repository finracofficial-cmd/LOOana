# -*- coding: utf-8 -*-
"""8,000円以上の注文（VIP特典の対象）の日別推移シートをレポートに追加する。
データ: data/daily/daily_order_bands.csv（Shopify ordersCount の EXACT 実測。current_total_price:>=7000 / >=8000 / >=10000 で日別に数える）
2026-10-09 16:30 にVIP条件を 8,000円 → 7,000円（＝2個以上）へ変更。ge7000 は 9/04 まで遡って取得済み
使い方: python3 scripts/vip_trend.py <report.xlsx>
毎日の定例で前日分を1行追記してから実行する。VIP特典は 2026-10-03 開始（Monster Cart の無料ギフトで優先配送0円）"""
import csv, sys, datetime
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
VIP_START = '2026-10-03'
VIP7_START = '2026-10-10'   # 7,000円条件の最初の丸1日（10/9は16:30変更の途中日）
HOL = {'2026-09-21', '2026-09-22', '2026-09-23'}
WD = ['月', '火', '水', '木', '金', '土', '日']
rows = list(csv.DictReader(open('data/daily/daily_order_bands.csv')))
for r in rows:
    for k in ('orders', 'ge7000', 'ge8000', 'ge10000'): r[k] = int(r[k])
    assert r['ge10000'] <= r['ge8000'] <= r['ge7000'] <= r['orders'], r
dates = [r['date'] for r in rows]
assert dates == sorted(set(dates)), '日付の重複・順序'
pre = [r for r in rows if r['date'] < VIP_START]
post = [r for r in rows if VIP_START <= r['date'] < VIP7_START]
post7 = [r for r in rows if r['date'] >= VIP7_START]
pre7 = [r for r in rows if '2026-09-25' <= r['date'] <= '2026-10-08']
def share(rs, k='ge8000'):
    o = sum(r['orders'] for r in rs); return (sum(r[k] for r in rs) / o) if o else None
wb = load_workbook(sys.argv[1])
if 'VIP推移' in wb.sheetnames: del wb['VIP推移']
ws = wb.create_sheet('VIP推移', 1)
TH = Font(name='Arial', bold=True, color='FFFFFF', size=10); TD = Font(name='Arial', size=10)
HEAD = PatternFill('solid', fgColor='305496'); VIPF = PatternFill('solid', fgColor='FFF2CC')
thin = Border(*[Side(style='thin', color='CCCCCC')] * 4)
notes = ['VIP特典（8,000円以上：優先発送無料＋次回1,000円OFF）の対象注文の推移',
         '件数はShopifyの実測（ordersCount・EXACT）。金額は注文の合計（割引後・返金後の現在値）',
         f'開始前 {pre[0]["date"]}〜{pre[-1]["date"]}（{len(pre)}日）: 8,000円以上 {sum(r["ge8000"] for r in pre)}件／{sum(r["orders"] for r in pre)}件 = {share(pre):.1%}'
         f'（1万円以上 {share(pre,"ge10000"):.1%}）',
         (f'開始後 {post[0]["date"]}〜{post[-1]["date"]}（{len(post)}日）: 8,000円以上 {sum(r["ge8000"] for r in post)}件／{sum(r["orders"] for r in post)}件 = {share(post):.1%}'
          f'（1万円以上 {share(post,"ge10000"):.1%}）') if post else '開始後のデータなし',
         f'7,000円以上（＝2個以上）: 変更前14日 9/25〜10/08 {sum(r["ge7000"] for r in pre7)}件／{sum(r["orders"] for r in pre7)}件 = {share(pre7,"ge7000"):.1%}'
         + (f' ／ 変更後 {post7[0]["date"]}〜{post7[-1]["date"]}（{len(post7)}日） {share(post7,"ge7000"):.1%}' if post7 else ' ／ 変更後（10/10〜）のデータなし')
         + '　※判定10/23（変更後14日）',
         '★日ごとのブレが大きい（開始前でも1〜12%）。判定は開始後14日の合計で、開始前14日と比べる。黄色＝VIP特典の開始後',
         '★7日移動の割合＝その日までの7日間の「8,000円以上の件数÷全注文」',
         '⚠️ 8,000円以上には「8,980円の商品を1個だけ」の注文も入る（UV歯ブラシ除菌器・10/4〜はネックマッサージャー）。まとめ買いが増えたかは「1万円以上の割合」で見るのが確実（1万円以上は2点以上でないと届かない）']
for i, t in enumerate(notes, 1): ws.cell(i, 1, t).font = Font(name='Arial', size=10, bold=(i == 1))
hr = len(notes) + 2
cols = ['日付', '曜', '全注文', '8,000円以上', '割合', '7日移動の割合', '1万円以上', '割合(1万)', '備考', '7,000円以上', '割合(7千)']
for c, v in enumerate(cols, 1):
    x = ws.cell(hr, c, v); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
for j, r in enumerate(rows):
    d = r['date']; w7 = rows[max(0, j-6):j+1]
    ma = share(w7) if len(w7) == 7 else None
    note = ('VIP特典 開始' if d == VIP_START else '') + ('7,000円へ変更(16:30)' if d == '2026-10-09' else '') + ('祝日' if d in HOL else '')
    vals = [d, WD[datetime.date.fromisoformat(d).weekday()], r['orders'], r['ge8000'], r['ge8000']/r['orders'],
            ma, r['ge10000'], r['ge10000']/r['orders'], note, r['ge7000'], r['ge7000']/r['orders']]
    for c, v in enumerate(vals, 1):
        x = ws.cell(hr+1+j, c, v); x.font = TD; x.border = thin
        if c in (5, 6, 8, 11) and v is not None: x.number_format = '0.0%'
        if d >= VIP_START: x.fill = VIPF
last = hr + len(rows)
for i, w in enumerate([12, 5, 9, 12, 9, 14, 10, 10, 18, 11, 10], 1): ws.column_dimensions[chr(64+i)].width = w
ch = LineChart(); ch.title = '8,000円以上の注文の割合'; ch.y_axis.number_format = '0%'; ch.height = 8; ch.width = 22
ch.add_data(Reference(ws, min_col=5, min_row=hr, max_row=last), titles_from_data=True)
ch.add_data(Reference(ws, min_col=6, min_row=hr, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=hr+1, max_row=last))
ws.add_chart(ch, f'M{hr}')
wb.save(sys.argv[1])
print('VIP推移 sheet added:', len(rows), 'days /', f'pre {share(pre):.1%}', f'post {share(post):.1%}' if post else '')
