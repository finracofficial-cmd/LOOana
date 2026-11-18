# -*- coding: utf-8 -*-
"""11/18 21:5x 「今日出した商品儲かってるのか」: グローブ・シーラー v2・フック v5・マルチクリップの 今日（0〜20時台）と出してからの通算の利益
利益＝値引後売上−原価（個数×原価・個数＝gross÷売価）−広告費。今日の分は raw.txt（T・S 行）、11/16〜17 のマルチクリップと 11/17 のグローブは o1117/an1118.txt と ic1118/ad_daily_1103_1117_raw.txt"""
import re, collections
src = open('../../../product_tabs.py', encoding='utf-8').read(); ns = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], ns); COST, PRICE = ns['COST'], ns['PRICE']
T = collections.defaultdict(float); S = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
for l in open('raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == 'T': T[p[1]] += float(p[3])
    elif p[0] == 'S' and p[1] == '2026-11-18': S[p[2]][0] += float(p[3]); S[p[2]][1] += float(p[4]); S[p[2]][2] += float(p[5])
an = open('../../o1117/an1118.txt', encoding='utf-8').read()
clip = re.search(r'360°マルチクリップ車載スマホホルダー（2026-11-16〜・2日）: 通算 個数(\d+)・売上([\d,]+)・原価([\d,]+)・広告([\d,]+)', an)
glove17 = sum(float(l.split(',')[4]) for l in open('../ad_daily_1103_1117_raw.txt') if l.startswith('2026-11-17,裏起毛タッチ防寒グローブ'))
for name, camp, prev in (('裏起毛タッチ防寒グローブ', '裏起毛タッチ防寒グローブ', (0, 0, glove17)),
                         ('ポータブルヒートシーラー', 'ポータブルヒートシーラーv2', (0, 0, 0)),
                         ('高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv5', (0, 0, 0)),
                         ('360°マルチクリップ車載スマホホルダー', '360°マルチクリップ車載スマホホルダー', tuple(float(clip.group(i).replace(',', '')) for i in (2, 3, 4)))):
    g, dc, o = S[name]; units = g / PRICE[name]; net = g + dc; cg = units * COST[name]; ad = T[camp]
    prof = net - cg - ad
    cn, cc, ca = prev[0] + net, prev[1] + cg, prev[2] + ad
    print(f'{name}: 今日 注文{o:.0f}・{units:.0f}個・売上 {net:,.0f}・原価 {cg:,.0f}・広告 {ad:,.0f} → 利益 {prof:+,.0f}（倍率 {(net-cg)/ad:.2f}）｜通算 売上 {cn:,.0f}・原価 {cc:,.0f}・広告 {ca:,.0f} → 利益 {cn-cc-ca:+,.0f}（倍率 {(cn-cc)/ca:.2f}）')
