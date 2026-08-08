# -*- coding: utf-8 -*-
"""害虫 秋CR(C / C-コピー)の日次推移。既存(A/B)との比較。Meta実測。"""
D=[('2026-08-06',[('A',19996,7707,187),('A - コピー',320,108,1),('B',14835,9236,155),('B - コピー',1671,765,12),('C',2131,793,11),('C - コピー',313,56,1)]),
   ('2026-08-07',[('A',12643,4487,90),('B',8051,4472,92),('C',12078,3729,66),('C - コピー',5484,1603,20)]),
   ('2026-08-08',[('A',20863,10632,154),('A - コピー',489,232,1),('B',23732,12211,207),('C',6616,1642,29),('C - コピー',2769,773,14)]),
   ('2026-08-09',[('A',4286,2071,36),('B',3521,1910,41),('C',6,2,0),('C - コピー',1,1,0)])]
print('=== 害虫 秋CR(C系) vs 既存(A/B系) の日次 ===')
print(f"{'日付':12}{'秋CR消化':>10}{'比率':>7}{'秋CTR':>8}{'既存CTR':>9}{'秋÷既存':>9}{'秋CPM':>8}{'既存CPM':>9}")
for d,ads in D:
    n=[a for a in ads if a[0].startswith('C')]; o=[a for a in ads if not a[0].startswith('C')]
    nc=sum(a[1] for a in n); ni=sum(a[2] for a in n); ncl=sum(a[3] for a in n)
    oc=sum(a[1] for a in o); oi=sum(a[2] for a in o); ocl=sum(a[3] for a in o)
    if ni<50: print(f"{d:12}{nc:>10,}{nc/(nc+oc)*100:>6.1f}%{'—':>8}{ocl/oi*100:>8.2f}%{'—':>9}{'—':>8}{oc/oi*1000:>9,.0f}  ※秋CRの配信ほぼ停止"); continue
    print(f"{d:12}{nc:>10,}{nc/(nc+oc)*100:>6.1f}%{ncl/ni*100:>7.2f}%{ocl/oi*100:>8.2f}%{(ncl/ni)/(ocl/oi)*100:>8.0f}%{nc/ni*1000:>8,.0f}{oc/oi*1000:>9,.0f}")
print()
tn=[(d,[a for a in ads if a[0].startswith('C')]) for d,ads in D]
nc=sum(a[1] for _,x in tn for a in x); ni=sum(a[2] for _,x in tn for a in x); ncl=sum(a[3] for _,x in tn for a in x)
to=[(d,[a for a in ads if not a[0].startswith('C')]) for d,ads in D]
oc=sum(a[1] for _,x in to for a in x); oi=sum(a[2] for _,x in to for a in x); ocl=sum(a[3] for _,x in to for a in x)
print(f'=== 4日累計(8/06-09 07時台) ===')
print(f"  秋CR: 消化 {nc:,}円({nc/(nc+oc)*100:.1f}%) インプ {ni:,} クリック {ncl} CTR {ncl/ni*100:.2f}% CPM {nc/ni*1000:,.0f}")
print(f"  既存: 消化 {oc:,}円({oc/(nc+oc)*100:.1f}%) インプ {oi:,} クリック {ocl} CTR {ocl/oi*100:.2f}% CPM {oc/oi*1000:,.0f}")
print(f"  → 秋CRのCTRは既存の {(ncl/ni)/(ocl/oi)*100:.0f}%、CPMは {(nc/ni)/(oc/oi)*100:.0f}%")
print(f"  → 1クリック単価: 秋CR {nc/ncl:,.0f}円 vs 既存 {oc/ocl:,.0f}円 （{(nc/ncl)/(oc/ocl)-1:+.0%}）")
