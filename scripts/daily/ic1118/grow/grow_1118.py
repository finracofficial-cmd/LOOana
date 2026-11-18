# -*- coding: utf-8 -*-
"""11/18 「全体的にもっと売る・儲けるには？」の土台の数字。30日（10/19〜11/17）
利益の式: 利益 ＝ 実売 − 原価 − 広告費。30日の実売・利益・広告費は o1117/an1118.txt の30日行（実測）から読む"""
import json, re, csv
J = json.load(open('raw_1118.json'))
L = open('../../o1117/an1118.txt').read()
m = re.search(r'30日: 利益 ([\d,]+)（[\d,]+/日・[\d.]+%）売上÷広告費 ([\d.]+) 倍率 ([\d.]+) 広告費/日 ([\d,]+)', L)
prof30 = int(m.group(1).replace(',', '')); mer = float(m.group(2)); bai = float(m.group(3)); ad30 = int(m.group(4).replace(',', '')) * 30
m7 = re.search(r'7日: 利益 ([\d,]+)（([\d,]+)/日・[\d.]+%）売上÷広告費 ([\d.]+) 倍率 ([\d.]+) 広告費/日 ([\d,]+)', L)
sales30 = mer * ad30; cogs30 = sales30 - ad30 - prof30; cr = cogs30 / sales30
s, ca, ch, co = map(int, J['funnel']['rows'][0])
orders = sum(int(r[1]) for r in J['new_returning']['rows'])
per_order = sales30 / orders * (1 - cr)  # 1注文あたりの粗利（広告費の前）
print(f'30日: 実売 {sales30:,.0f}・原価率 {cr:.1%}・広告費 {ad30:,.0f}・利益 {prof30:,.0f}（{prof30/30:,.0f}/日）・注文 {orders}・1注文の粗利 {per_order:,.0f}円')
print(f'7日: 利益 {m7.group(2)}/日・倍率 {m7.group(4)}・広告費/日 {m7.group(5)}')
print(f'流れ（30日）: 来訪 {s:,} → カート {ca:,}（{ca/s:.2%}）→ 決済画面 {ch:,}（カートの {ch/ca:.0%}）→ 購入 {co:,}（決済画面の {co/ch:.1%}）')
print(f'  決済画面まで来て買わなかった {ch-co:,}（30日）')
d = co / ch
for lab, extra in (('カート率 +0.5pt', co * (ca / s + 0.005) / (ca / s) - co), ('決済完了 +5pt', co * (d + 0.05) / d - co), ('決済完了 +1pt', co * (d + 0.01) / d - co)):
    print(f'  {lab}: 注文 +{extra:.0f}/30日 → 粗利 +{extra*per_order/30:,.0f}円/日（広告費はそのまま）')
nr = {r[0]: r for r in J['new_returning']['rows']}
print(f"リピート: 注文 {nr['Returning'][1]}／{orders}（{int(nr['Returning'][1])/orders:.1%}）・売上 {int(nr['Returning'][2])/(int(nr['New'][2])+int(nr['Returning'][2])):.1%}・顧客の記録 {J['customers_total']:,}")
print('入口: ' + '・'.join(f"{r[0] or '直接/不明'} {int(r[1])/orders:.1%}" for r in J['referrer']['rows']))
B = [r for r in csv.DictReader(open('../../../../data/daily/daily_order_bands.csv')) if '2026-10-19' <= r['date'] <= '2026-11-17']
o = sum(int(r['orders']) for r in B); g7 = sum(int(r['ge7000']) for r in B)
print(f'まとめ買い（7,000円以上の注文）: {g7/o:.1%}。+5pt なら 1日 {o/30*0.05:.1f} 個増 → 粗利 約 +{o/30*0.05*3980*0.9*(1-cr):,.0f}円/日（2個目3,980円の10%引きで計算）')
for b, lab in ((0.05, '+0.05'), (0.1, '+0.1')):
    print(f'倍率 {lab}: 広告費/日 {int(m7.group(5).replace(",", "")):,} で +{b*int(m7.group(5).replace(",", "")):,.0f}円/日')
print(f'量: 倍率1.5の商品に広告費 +1万円/日 → +5,000円/日（倍率が保たれた場合）')
