#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-05 「単日でここまで崩れるのは問題では」の深掘り
害虫ブロッカーの38日実測（6/29-8/5）で、単日崩れの正体を分解する。
売上・注文 = Shopify実測（data/analysis/gaichu_shopify_orders_0629_0805.csv 当日クエリ保存分）
配信指標   = Meta実測（data/analysis/gaichu_meta_daily_0629_0805.csv 当日クエリ保存分）
CVR = Shopify注文 ÷ Metaアウトバウンドクリック（datarulesの分担）
"""
import csv, math
from datetime import date, timedelta

M = {r['date']: r for r in csv.DictReader(open('data/analysis/gaichu_meta_daily_0629_0805.csv'))}
S = {r['date']: r for r in csv.DictReader(open('data/analysis/gaichu_shopify_orders_0629_0805.csv'))}
PRICE, UCOST = 3980, 867
GP_ORDER = 5342          # 分岐CPA(注文) = 粗利/個3,113 × 1.716個/注文（7/27週実測）

def wk(days):
    c = sum(float(M[d]['cost']) for d in days)
    i = sum(float(M[d]['impressions']) for d in days)
    cl = sum(float(M[d]['clicks']) for d in days)
    o = sum(int(S[d]['orders']) for d in days)
    g = sum(int(S[d]['gross']) for d in days)
    return c, i, cl, o, g

print('=== 週次の悪化チェーン（CPA = CPC ÷ CVR）===')
print(f"{'週':14}{'CPM':>7}{'CTR':>7}{'CPC':>6}{'CVR':>7}{'CPA注文':>8}{'注文/日':>8}{'分岐との余裕':>12}")
rows = []
for wstart in ['2026-06-29','2026-07-06','2026-07-13','2026-07-20','2026-07-27']:
    d0 = date.fromisoformat(wstart)
    days = [(d0+timedelta(i)).isoformat() for i in range(7)]
    c,i,cl,o,g = wk(days)
    rows.append((wstart, c/i*1000, cl/i, c/cl, o/cl, c/o, o/7))
    print(f'{wstart}週 {c/i*1000:7,.0f}{cl/i*100:6.2f}%{c/cl:6,.0f}{o/cl*100:6.2f}%{c/o:8,.0f}{o/7:8.1f}{GP_ORDER-c/o:12,.0f}')

a, b = rows[0], rows[-1]
print()
print('6/29週 → 7/27週:')
print(f'  CPM  {a[1]:,.0f} → {b[1]:,.0f}  ({(b[1]/a[1]-1)*100:+.0f}%)  … オークションはほぼ横ばい')
print(f'  CTR  {a[2]*100:.2f}% → {b[2]*100:.2f}%  ({(b[2]/a[2]-1)*100:+.0f}%)  … クリックする人が枯れた（主犯①）')
print(f'  CPC  {a[3]:,.0f} → {b[3]:,.0f}  ({(b[3]/a[3]-1)*100:+.0f}%)')
print(f'  CVR  {a[4]*100:.2f}% → {b[4]*100:.2f}%  ({(b[4]/a[4]-1)*100:+.0f}%)  … 買う人も薄くなった（主犯②）')
print(f'  CPA  {a[5]:,.0f} → {b[5]:,.0f}  (×{b[5]/a[5]:.1f})  分岐{GP_ORDER:,}への余裕 {GP_ORDER-a[5]:,.0f} → {GP_ORDER-b[5]:,.0f}')
print(f'  CPA悪化ペース ≈ {(b[5]-a[5])/4:,.0f}円/週 → このペースだと分岐到達まで {(GP_ORDER-b[5])/((b[5]-a[5])/4):.1f}週')

print()
print('=== 単日ノイズの構造（なぜ「1日の崩れ」が目立つようになったか）===')
def stats(days):
    o = [int(S[d]['orders']) for d in days]
    m = sum(o)/len(o)
    sd = math.sqrt(sum((x-m)**2 for x in o)/(len(o)-1))
    return m, sd
d0 = date.fromisoformat('2026-06-29')
early = [(d0+timedelta(i)).isoformat() for i in range(14)]
d1 = date.fromisoformat('2026-07-22')
late  = [(d1+timedelta(i)).isoformat() for i in range(14)]
me, se = stats(early); ml, sl = stats(late)
print(f'6/29-7/12: 注文 {me:.1f}±{se:.1f}/日 (変動係数 {se/me*100:.0f}%)  1.5σ下振れ日でも {me-1.5*se:.0f}注文 → 利益は黒字圏')
print(f'7/22-8/04: 注文 {ml:.1f}±{sl:.1f}/日 (変動係数 {sl/ml*100:.0f}%)  1.5σ下振れ日は {ml-1.5*sl:.0f}注文 → CPA {58520/ (ml-1.5*sl):,.0f}円 ≈ 分岐スレスレ')
print('→ 母数半減でノイズの相対振幅が拡大し、かつ余裕が半減したので、同じ下振れが「赤字の日」として顕在化する')

lam = 12  # 同時刻比較の期待値（8/2-8/4の15時までの実測 12-15注文の下端）
p = sum(math.exp(-lam)*lam**k/math.factorial(k) for k in range(4))
print(f'今日(15:23時点3注文): 同時刻期待値{lam}に対しP(X≤3)={p*100:.2f}% ≈ {1/p:,.0f}日に1回の下振れ + 全店も同時刻比-26%の弱い日')
