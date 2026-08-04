#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-04 「安定していた形状記憶日傘がなぜ売れないのか」
日傘2商品（K=形状記憶日傘 / Z=完全遮光・形状記憶・晴雨兼用・UV日傘）の
2026-05-04〜08-03 日次Meta実測を週次に集計し、単品と合算の両方で見る。
日傘は同一SKU相互流入があるため、SKILLの規定どおり合算も併記する。
"""
from collections import defaultdict
from datetime import date, timedelta

SRC = '/tmp/claude-0/-home-user-LOOana/42be2ed9-9967-56df-ab9c-75166f45bbc9/scratchpad/umb.txt'
rows = []
for line in open(SRC):
    line = line.strip()
    if not line:
        continue
    d, n, cost, imp, ctr, clicks, freq, purch, val = line.split(',')
    rows.append((d, n, float(cost), float(imp), float(ctr), float(clicks),
                 float(freq), float(purch), float(val)))

def wk(d):
    y, m, dd = map(int, d.split('-'))
    t = date(y, m, dd)
    return (t - timedelta(days=t.weekday())).isoformat()

PRICE = {'K': 4980, 'Z': 5980}     # 実測: gross/net_items から確認済み
COST  = {'K': 1309, 'Z': 1309}
NAME  = {'K': '形状記憶日傘', 'Z': '完全遮光UV日傘'}

agg = defaultdict(lambda: [0.0]*6)   # (week, name) -> cost, imp, clicks, purch, val, freqw
for d, n, c, i, ctr, cl, fq, p, v in rows:
    a = agg[(wk(d), n)]
    a[0] += c; a[1] += i; a[2] += cl; a[3] += p; a[4] += v; a[5] += fq * i
weeks = sorted({wk(d) for d, *_ in rows})

def table(keys, title, price, cost):
    print()
    print('=' * 104)
    print(title)
    print('=' * 104)
    gp = price - cost
    print(f"{'週':12}{'広告費':>10}{'CPM':>7}{'CTR':>7}{'クリック':>8}{'CVR':>7}{'購入':>6}"
          f"{'CPA':>7}{'頻度':>6}{'粗利-広告費':>12}")
    out = []
    for w in weeks:
        c = i = cl = p = v = fw = 0
        for k in keys:
            a = agg[(w, k)]
            c += a[0]; i += a[1]; cl += a[2]; p += a[3]; v += a[4]; fw += a[5]
        if i == 0:
            continue
        cpm = c/i*1000; ctr = cl/i; cvr = p/cl if cl else 0
        cpa = c/p if p else float('nan')
        prof = gp*p - c
        print(f'{w:12}{c:10,.0f}{cpm:7,.0f}{ctr*100:6.2f}%{cl:8,.0f}{cvr*100:6.2f}%{p:6,.0f}'
              f'{cpa:7,.0f}{fw/i:6.2f}{prof:12,.0f}')
        out.append((w, c, cpm, ctr, cvr, p, cpa, prof))
    return out

k = table(['K'], '形状記憶日傘（売価4,980 / 原価1,309 / 粗利3,671 = 分岐CPA）', 4980, 1309)
z = table(['Z'], '完全遮光UV日傘（売価5,980 / 原価1,309 / 粗利4,671 = 分岐CPA）', 5980, 1309)

# 合算（粗利は加重平均で持つ必要があるので別計算）
print()
print('=' * 104)
print('日傘2本 合算（相互流入があるためSKILL規定で必ず併記）')
print('=' * 104)
print(f"{'週':12}{'広告費':>10}{'購入':>7}{'CPA':>8}{'粗利-広告費':>13}{'K比率':>8}")
for w in weeks:
    ck, ik, clk, pk, vk, _ = agg[(w, 'K')]
    cz, iz, clz, pz, vz, _ = agg[(w, 'Z')]
    c = ck + cz; p = pk + pz
    if p == 0:
        continue
    prof = (4980-1309)*pk + (5980-1309)*pz - c
    print(f'{w:12}{c:10,.0f}{p:7,.0f}{c/p:8,.0f}{prof:13,.0f}{pk/p*100:7.1f}%')

# ---- ピーク週と直近週の比較 ----
print()
print('=' * 104)
print('形状記憶日傘: 何が壊れたのか（5/11週 ピーク → 7/27週）')
print('=' * 104)
def get(w, key):
    c, i, cl, p, v, fw = agg[(w, key)]
    return dict(cost=c, imp=i, clicks=cl, purch=p, val=v,
                cpm=c/i*1000, ctr=cl/i, cvr=p/cl, cpa=c/p, aov=v/p, freq=fw/i)
a = get('2026-05-11', 'K'); b = get('2026-07-27', 'K')
print(f'{"":16}{"5/11週":>12}{"7/27週":>12}{"変化":>11}')
for lab, kk, f in [('広告費','cost','{:,.0f}'),('インプレッション','imp','{:,.0f}'),
                   ('クリック','clicks','{:,.0f}'),('購入','purch','{:,.0f}'),
                   ('CPM','cpm','{:,.0f}'),('CTR','ctr','{:.2%}'),('CVR','cvr','{:.2%}'),
                   ('CPA','cpa','{:,.0f}'),('AOV(Meta)','aov','{:,.0f}'),('頻度','freq','{:.2f}')]:
    print(f'{lab:16}{f.format(a[kk]):>12}{f.format(b[kk]):>12}{(b[kk]/a[kk]-1)*100:+10.1f}%')

import math
r_cpa = b['cpa']/a['cpa']; lt = math.log(r_cpa)
print()
print('CPA悪化の寄与分解（CPA = CPM ÷ (CTR × CVR × 1000)）')
for lab, r, s in [('CPM', b['cpm']/a['cpm'], +1), ('CTR', b['ctr']/a['ctr'], -1), ('CVR', b['cvr']/a['cvr'], -1)]:
    print(f'  {lab:5} {(r-1)*100:+7.1f}%  → CPAへの寄与 {s*math.log(r)/lt*100:6.1f}%')
print(f'  合計 CPA {(r_cpa-1)*100:+.1f}%')

# ---- 完全遮光との対比 ----
print()
print('=' * 104)
print('決定的な対比: 同じ「日傘」なのに完全遮光は崩れていない')
print('=' * 104)
az = get('2026-05-11', 'Z'); bz = get('2026-07-27', 'Z')
print(f'{"":22}{"形状記憶(K)":>16}{"完全遮光(Z)":>16}')
for lab, kk in [('CTR 変化','ctr'),('CVR 変化','cvr'),('CPA 変化','cpa'),('広告費 変化','cost')]:
    print(f'{lab:22}{(b[kk]/a[kk]-1)*100:+15.1f}%{(bz[kk]/az[kk]-1)*100:+15.1f}%')
print(f'{"7/27週 CPA":22}{b["cpa"]:15,.0f}{bz["cpa"]:15,.0f}')
print(f'{"分岐CPA(粗利)":22}{3671:15,}{4671:15,}')
print(f'{"分岐に対する余裕":22}{3671-b["cpa"]:15,.0f}{4671-bz["cpa"]:15,.0f}')
