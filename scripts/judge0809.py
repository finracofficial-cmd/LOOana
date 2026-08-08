# -*- coding: utf-8 -*-
"""8/09 判定の執行。増分MERは曜日補正と全店コントロール補正の両方を出し、悪い方で機械判定する。"""
import csv, collections, pickle, datetime
R=pickle.load(open('/tmp/rep0809.pkl','rb')); IDX=R['IDX']
S=collections.defaultdict(lambda: collections.defaultdict(int)); A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_sales.csv')): S[r['name']][r['date']]+=int(r['gross'])-int(r['disc'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['campaign']][r['date']]+=float(r['cost'])
ALL=collections.defaultdict(int)
for n,v in S.items():
    for d,x in v.items(): ALL[d]+=x
WD=['月','火','水','木','金','土','日']
def inc(name,camp,P1,P2,label):
    s1=sum(S[name][d] for d in P1)/len(P1); s2=sum(S[name][d] for d in P2)/len(P2)
    a1=sum(A[camp][d] for d in P1)/len(P1); a2=sum(A[camp][d] for d in P2)/len(P2)
    i1=sum(IDX[WD[datetime.date(*map(int,d.split('-'))).weekday()]] for d in P1)/len(P1)
    i2=sum(IDX[WD[datetime.date(*map(int,d.split('-'))).weekday()]] for d in P2)/len(P2)
    s2w=s2*(i1/i2)                                        # ①曜日指数補正
    c1=sum(ALL[d]-S[name][d] for d in P1)/len(P1); c2=sum(ALL[d]-S[name][d] for d in P2)/len(P2)
    s2c=s2*(c1/c2)                                        # ②全店コントロール補正
    da=a2-a1
    print(f"\n=== {label} ===")
    print(f"  P1 {P1[0]}〜{P1[-1]} ({len(P1)}日): 売上/日 {s1:>9,.0f}  広告/日 {a1:>9,.0f}  曜日指数 {i1:.1f}")
    print(f"  P2 {P2[0]}〜{P2[-1]} ({len(P2)}日): 売上/日 {s2:>9,.0f}  広告/日 {a2:>9,.0f}  曜日指数 {i2:.1f}")
    print(f"  Δ広告費/日 {da:+,.0f}  （|Δ|<3,000なら算出しない → {'OK' if abs(da)>=3000 else '算出不可'}）")
    if abs(da)<3000: return None
    for lbl,sx in [('①曜日指数補正',s2w),('②全店コントロール補正',s2c)]:
        print(f"  {lbl}: 補正後売上/日 {sx:>9,.0f}  Δ売上 {sx-s1:+9,.0f}  増分MER {(sx-s1)/da:>7.2f}")
    return min((s2w-s1)/da,(s2c-s1)/da), max((s2w-s1)/da,(s2c-s1)/da)
P1=['2026-08-03','2026-08-04','2026-08-05']; P2=['2026-08-07','2026-08-08']
r=inc('害虫ブロッカー','害虫ブロッカー',P1,P2,'① 害虫ブロッカー 8/6減額(40,000→30,000)の増分MER')
if r:
    lo,hi=r
    print(f"\n  → 下限 {lo:.2f} / 上限 {hi:.2f}  （分岐1.31・目標2.42）")
    z=lambda x: '分岐割れ' if x<1.31 else ('分岐〜目標' if x<2.42 else '目標超え')
    print(f"  ゾーン: 下限={z(lo)} / 上限={z(hi)} → {'✅ 同ゾーン＝採用' if z(lo)==z(hi) else '⚠️ 別ゾーン＝判定保留（SKILL既定）'}")
print('\n=== ② 2WAYシートボックス 中間判定（8/09） ===')
n='2WAYシートボックス'; s=R['N7'][n]; c=R['K7'][n]; a=R['A7'][n]; q=R['Q7'][n]
o=24  # 【転記】Shopify 8/02-08 orders（同クエリの合計で検算済）
cl=None
print(f"  7日: 実売 {s:,} / 広告 {a:,.0f} / 販売数 {q} / 注文 {o}")
print(f"  MER {s/a:.2f}（分岐 {1/(1-c/s):.2f}・目標 {1/(1-c/s-0.35):.2f}）  余裕 {s/a-1/(1-c/s):+.2f}  7日利益 {s-c-a:+,.0f}円")
print(f"  CPA(注文) {a/o:,.0f}円 vs 分岐CPA {(s-c)/o:,.0f}円 → {'✅ 合格' if a/o<(s-c)/o else '❌ 不合格'}")
print(f"  宣言済み基準: CPA(注文) < 3,037円 → 実測 {a/o:,.0f}円 → {'✅ 合格' if a/o<3037 else '❌ 不合格'}")
