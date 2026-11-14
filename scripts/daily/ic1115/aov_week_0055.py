# -*- coding: utf-8 -*-
"""客単価（実売÷注文）が前週より 7.1% 下がった中身（2026-11-15 00:5x）
①7,000円以上の注文の割合（daily_order_bands・週別）と偶然のぶれ ②商品の顔ぶれ（構成）と商品の中の変化に分ける
②は Shopify の商品別 注文数・売上（値引前）を使う。1注文に2商品あれば両方に数えるので、店の注文数とは合わない（目安）"""
import csv, math, datetime, collections
R = __file__.rsplit('/scripts/', 1)[0] + '/'
H = R + 'scripts/daily/ic1115/'
OB = {r['date']: r for r in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv'))}
END = datetime.date(2026, 11, 14)
W = lambda w: [(END - datetime.timedelta(7 * w + k)).isoformat() for k in range(6, -1, -1)]
print('週（7日）       注文  7,000円以上  割合')
SH = {}
for w in range(5, -1, -1):
    ds = W(w); o = sum(int(OB[d]['orders']) for d in ds); h = sum(int(OB[d]['ge7000']) for d in ds); SH[w] = (o, h)
    print(f'{ds[0][5:]}〜{ds[-1][5:]}   {o:4d}   {h:4d}      {h/o*100:4.1f}%')
(o1, h1), (o2, h2) = SH[1], SH[0]
p = (h1 + h2) / (o1 + o2); se = math.sqrt(p * (1 - p) * (1 / o1 + 1 / o2)); z = (h2 / o2 - h1 / o1) / se
print(f'  前週→今週 {h1/o1*100:.1f}% → {h2/o2*100:.1f}%（差 {(h2/o2-h1/o1)*100:+.1f}pt・偶然のぶれ ±{se*100:.1f}pt・z {z:+.2f}）')
o4 = sum(SH[w][0] for w in (2, 3, 4, 5)); h4 = sum(SH[w][1] for w in (2, 3, 4, 5))
p = (h4 + h2) / (o4 + o2); se = math.sqrt(p * (1 - p) * (1 / o4 + 1 / o2)); z = (h2 / o2 - h4 / o4) / se
print(f'  その前の4週（10/11〜11/7 のうち前週を除く 10/11〜10/31＋10/4〜10/10）→今週 {h4/o4*100:.1f}% → {h2/o2*100:.1f}%（差 {(h2/o2-h4/o4)*100:+.1f}pt・偶然のぶれ ±{se*100:.1f}pt・z {z:+.2f}）')
PO = collections.defaultdict(dict)
for l in open(H + 'prod_orders_wk.txt'):
    if l[0] != '#': w, n, o, g = l.strip().split(','); PO[w][n] = (int(o), int(g))
A, B = PO['A'], PO['B']
oa = sum(v[0] for v in A.values()); ga = sum(v[1] for v in A.values()); ob = sum(v[0] for v in B.values()); gb = sum(v[1] for v in B.values())
mix = sum(B[n][0] * (A[n][1] / A[n][0] if n in A and A[n][0] else B[n][1] / B[n][0]) for n in B) / ob
print(f'\n商品ごとの注文1件あたり売上（値引前）: 前週 {ga/oa:,.0f} → 今週 {gb/ob:,.0f}（{(gb/ob)/(ga/oa)*100-100:+.1f}%）')
print(f'  顔ぶれだけ今週にした場合（商品ごとの1件あたりは前週のまま）: {mix:,.0f}（{mix/(ga/oa)*100-100:+.1f}%）→ 顔ぶれで {math.log(mix/(ga/oa))/math.log((gb/ob)/(ga/oa))*100:.0f}%・商品の中で {math.log((gb/ob)/mix)/math.log((gb/ob)/(ga/oa))*100:.0f}%')
print('  商品の中（前週→今週の1件あたり・注文）:')
for n in sorted(B, key=lambda n: -B[n][0]):
    if n in A and A[n][0] >= 5 and B[n][0] >= 5:
        print(f'    {n}: {A[n][1]/A[n][0]:,.0f} → {B[n][1]/B[n][0]:,.0f}（{(B[n][1]/B[n][0])/(A[n][1]/A[n][0])*100-100:+.1f}%・注文 {A[n][0]}→{B[n][0]}）')
