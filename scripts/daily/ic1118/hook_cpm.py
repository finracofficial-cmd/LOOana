# -*- coding: utf-8 -*-
"""11/18 「フックは CPM 高いのか。やっぱ無理かな？」: フック（9/9〜）の週ごとの CPM と 表示1,000回あたりの購入（Meta）。赤字にならない線＝CPM ÷ 1注文の粗利（1個・値引なし）"""
src = open('../../product_tabs.py', encoding='utf-8').read(); ns = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], ns); C, P = ns['COST']['高見えレザーヘッドレストフック'], ns['PRICE']['高見えレザーヘッドレストフック']
num = lambda x: 0 if x == 'null' else float(x)
gp = P - C
print(f'1個の粗利 {gp:,.0f}円（売価 {P}・原価 {C}）')
for l in open('life/meta_weekly_raw.txt'):
    if l[0] == '#' or 'ヘッドレストフック' not in l: continue
    w, c, cost, imp, reach, fq, clk, lpv, atc, pur = l.strip().split(',')
    cost, imp, pur = num(cost), num(imp), num(pur)
    if cost < 10000: continue
    cpm = cost / imp * 1000
    print(f'  週{w.split("|")[1]} {c[-3:]}: 広告費 {cost:,.0f}・CPM {cpm:,.0f}・購入 {pur:.0f}（表示1,000回あたり {pur/imp*1000:.2f}）・赤字にならない線 {cpm/gp:.2f}・倍率1.86の線 {cpm/gp*1.86:.2f}')
cpm = 4271 / 839 * 1000
print(f'v5 11/18（22:13 時点・Meta）: CPM {cpm:,.0f}・購入2／表示839（{2/839*1000:.2f}）・赤字にならない線 {cpm/gp:.2f}・倍率1.86の線 {cpm/gp*1.86:.2f}')
