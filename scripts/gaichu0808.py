# -*- coding: utf-8 -*-
"""害虫 8/08 08:15時点。前日同時刻と比較。配信=Meta / 売上=Shopify"""
# 【転記】Meta 8/08 広告別（trace 3c6db83e...）
T=[('本体','A',4984,2094,38),('0719','B',3689,1760,32),('本体','C(秋)',1588,457,11),('0719','C-コピー(秋)',152,35,2)]
tc=sum(x[2] for x in T); ti=sum(x[3] for x in T); tcl=sum(x[4] for x in T)
S=23880-1791; O=4; Q=round(23880/3980)
print('=== 8/08 08:15時点 害虫（Meta配信） ===')
print(f"{'セット':6}{'広告':16}{'消化':>8}{'インプ':>7}{'CL':>4}{'外部CTR':>8}")
for s,n,c,i,cl in T: print(f"{s:6}{n:16}{c:>8,}{i:>7,}{cl:>4}{cl/i*100:>7.2f}%")
print(f"{'合計':22}{tc:>8,}{ti:>7,}{tcl:>4}{tcl/ti*100:>7.2f}%")
new=sum(x[2] for x in T if '秋' in x[1]); ncl=sum(x[4] for x in T if '秋' in x[1]); ni=sum(x[3] for x in T if '秋' in x[1])
old=tc-new; ocl=tcl-ncl; oi=ti-ni
print(f"\n  秋CR2本: 消化 {new:,}円({new/tc*100:.1f}%) CTR {ncl/ni*100:.2f}%")
print(f"  既存2本: 消化 {old:,}円({old/tc*100:.1f}%) CTR {ocl/oi*100:.2f}%")
print(f"  → 秋CRは既存の {(ncl/ni)/(ocl/oi)*100:.0f}%（8/07朝 63% → 8/07夜 90% → 今 {(ncl/ni)/(ocl/oi)*100:.0f}%）")
print()
print('=== 損益（08:15時点） ===')
print(f"  実売 {S:,}円 / {O}注文 / {Q}個 / 広告 {tc:,}円")
print(f"  MER {S/tc:.2f}（分岐1.31）  利益 {S-Q*867-tc:+,.0f}円")
print(f"  CPA(注文) {tc/O:,.0f}円 vs 分岐CPA {(3980-867)*Q/O:,.0f}円  点数/注文 {Q/O:.2f}")
print()
print('=== 前日(8/07)の同時刻帯との比較 ===')
print('  ※8/07は11:40が最初の観測なので厳密な同時刻比較は不可。以下は「1日通算」との対比')
for lbl,c,s,o,q in [('8/06 全日',39264,62685,7,17),('8/07 全日',38245,34228,7,9)]:
    print(f"  {lbl}: 広告 {c:,} 実売 {s:,} MER {s/c:.2f} CPA {c/o:,.0f}円 点数/注文 {q/o:.2f}")
print(f"  8/08 08:15: 広告 {tc:,} 実売 {S:,} MER {S/tc:.2f} CPA {tc/O:,.0f}円 点数/注文 {Q/O:.2f}")
