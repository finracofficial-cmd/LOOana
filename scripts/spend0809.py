# -*- coding: utf-8 -*-
"""なぜ8/08の広告費が跳ねたか。暦週(日〜土)ペーシングで検証。"""
import csv, collections, datetime
A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['date']][r['campaign']]+=float(r['cost'])
B=collections.defaultdict(int)
for r in csv.DictReader(open('data/budget-snapshots.csv')): B[r['snapshot_date']]+=int(r['daily_budget'])
WD=['月','火','水','木','金','土','日']
print('=== 日次: 日予算 vs 実消化 ===')
print(f"{'日付':12}{'曜':>3}{'日予算':>10}{'実消化':>10}{'消化率':>8}")
days=sorted(d for d in A if d>='2026-07-26')
for d in days:
    c=sum(A[d].values()); b=B.get(d,0)
    print(f"{d:12}{WD[datetime.date(*map(int,d.split('-'))).weekday()]:>3}{(f'{b:,}' if b else '—'):>10}{c:>10,.0f}{(f'{c/b*100:.0f}%' if b else '—'):>8}")
print()
print('=== 暦週(日〜土)の累計消化 vs 日予算×7 ===')
for st in ['2026-07-26','2026-08-02']:
    s=datetime.date(*map(int,st.split('-')))
    wk=[(s+datetime.timedelta(i)).isoformat() for i in range(7)]
    wk=[d for d in wk if d in A]
    tot=sum(sum(A[d].values()) for d in wk)
    bud=sum(B.get(d,0) for d in wk)
    print(f"  {wk[0]}〜{wk[-1]} ({len(wk)}日): 実消化 {tot:>10,.0f}  日予算合計 {bud:>10,.0f}  消化率 {tot/bud*100:.1f}%")
print()
print('=== 8/07 → 8/08 のキャンペーン別 増減 ===')
d1,d2='2026-08-07','2026-08-08'
rows=sorted(set(A[d1])|set(A[d2]), key=lambda c: -(A[d2].get(c,0)-A[d1].get(c,0)))
print(f"{'キャンペーン':30}{'8/07':>9}{'8/08':>9}{'差':>9}{'変化率':>8}")
t1=t2=0
for c in rows:
    a=A[d1].get(c,0); b=A[d2].get(c,0); t1+=a; t2+=b
    if abs(b-a)<1500: continue
    print(f"{c[:30]:30}{a:>9,.0f}{b:>9,.0f}{b-a:>+9,.0f}{(b/a-1)*100 if a else 0:>+7.0f}%")
print(f"{'合計':30}{t1:>9,.0f}{t2:>9,.0f}{t2-t1:>+9,.0f}{(t2/t1-1)*100:>+7.1f}%")
print(f"\n  日予算の変更分は 2WAY +2,500 と W固定 +3,000 の計 +5,500円だけ")
print(f"  実際の増加 {t2-t1:+,.0f}円 のうち、予算変更で説明できるのは +5,500円（{5500/(t2-t1)*100:.0f}%）")
