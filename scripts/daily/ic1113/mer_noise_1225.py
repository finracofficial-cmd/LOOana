# -*- coding: utf-8 -*-
"""11/13(金) 12:2x 「なんで日ごとにMERの良し悪しがぶれるのか」
店全体の日次 MER（売上÷広告費）のぶれを、①注文件数の偶然（同じ売れやすさでも件数は日によってぶれる）②曜日 ③客単価 ④それ以外 に分けて大きさを測る。
対数で分ける: log MER = log(注文÷広告費) + log(客単価)。偶然のぶれの大きさは 注文件数がポアソンに従うとして 1/注文件数。入力: data/daily/*.csv（祝日は除く）"""
import csv, collections, datetime, math, statistics as st
R = '/home/user/LOOana/'
NET = collections.defaultdict(int); AD = collections.defaultdict(float); OR = {}
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv')): OR[r['date']] = int(r['orders'])
HOL = {'2026-09-21', '2026-09-22', '2026-09-23', '2026-10-12', '2026-11-03'}
for lab, a, b in (('直近30日', '2026-10-14', '2026-11-12'), ('その前の30日', '2026-09-14', '2026-10-13')):
    D = [d for d in sorted(OR) if a <= d <= b and d not in HOL]
    m = {d: NET[d] / AD[d] for d in D}; lm = [math.log(m[d]) for d in D]
    lc = [math.log(OR[d] / AD[d]) for d in D]; la = [math.log(NET[d] / OR[d]) for d in D]
    vt = st.pvariance(lm); vc = st.pvariance(lc); va = st.pvariance(la); cov = (vt - vc - va) / 2
    pois = st.mean(1 / OR[d] for d in D)
    # 曜日: 注文÷広告費の対数を曜日の平均で説明できる分
    byw = collections.defaultdict(list)
    for d, x in zip(D, lc): byw[datetime.date.fromisoformat(d).weekday()].append(x)
    mu = st.mean(lc); vdow = sum(len(v) * (st.mean(v) - mu) ** 2 for v in byw.values()) / len(lc)
    sd = lambda v: (math.exp(math.sqrt(v)) - 1) * 100
    print(f"■ {lab}（{D[0]}〜{D[-1]}・祝日除く{len(D)}日）: MER {min(m.values()):.2f}〜{max(m.values()):.2f}（中央値 {st.median(m.values()):.2f}）・注文 {min(OR[d] for d in D)}〜{max(OR[d] for d in D)}件/日（平均 {st.mean(OR[d] for d in D):.0f}）")
    print(f"  MERのぶれ（対数の分散）{vt:.4f}＝ふだん±{sd(vt):.0f}%")
    print(f"   ├ 注文÷広告費のぶれ {vc:.4f}（±{sd(vc):.0f}%）: うち 注文件数の偶然 {pois:.4f}（±{sd(pois):.0f}%・{pois/vt*100:.0f}%）・曜日 {vdow:.4f}（{vdow/vt*100:.0f}%）・それ以外 {max(vc-pois-vdow,0):.4f}（{max(vc-pois-vdow,0)/vt*100:.0f}%）")
    print(f"   ├ 客単価のぶれ {va:.4f}（±{sd(va):.0f}%・{va/vt*100:.0f}%）")
    print(f"   └ 2つの重なり {2*cov:+.4f}（{2*cov/vt*100:+.0f}%）")
# 商品1つ・1日で見たときの偶然のぶれの目安
print('\n■ 1日の件数と、偶然だけで起きるぶれの目安（±1標準偏差）: ' + '・'.join(f"{n}件/日 → ±{100/math.sqrt(n):.0f}%" for n in (5, 10, 15, 20, 70)))
