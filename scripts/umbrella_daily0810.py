# -*- coding: utf-8 -*-
"""日傘2種の日次＋カタログ広告費の期間別内訳＋利益率のレバー分解"""
import csv, collections, datetime, pickle
R=pickle.load(open('/tmp/rep0810.pkl','rb'))
S=collections.defaultdict(lambda: collections.defaultdict(int)); A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_sales.csv')): S[r['name']][r['date']]+=int(r['gross'])-int(r['disc'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['campaign']][r['date']]+=float(r['cost'])
G=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('data/daily/daily_sales.csv')): G[r['name']][r['date']]+=int(r['gross'])
WD=['月','火','水','木','金','土','日']
print('=== 日傘2種の日次（分岐1.37） ===')
print(f"{'日付':11}{'曜':>3}{'短:広告':>9}{'短:実売':>9}{'短MER':>7}{'  ':2}{'長:広告':>9}{'長:実売':>9}{'長MER':>7}{'長:利益':>9}")
NG={'短':('形状記憶日傘','形状記憶日傘'),'長':('完全遮光・形状記憶','完全遮光・形状記憶・晴雨兼用・UV日傘')}
run=0
for d in sorted(S['形状記憶日傘']):
    if d<'2026-08-01': continue
    o={}
    for k,(sn,an) in NG.items():
        o[k]=(A[an][d],S[sn][d],round(G[sn][d]/4980)*1309)
    lp=o['長'][1]-o['長'][2]-o['長'][0]
    m=o['長'][1]/o['長'][0] if o['長'][0] else 0
    run = run+1 if m<1.37 else 0
    flag='🚨' if run>=3 else ('⚠️' if m<1.37 else '')
    print(f"{d:11}{WD[datetime.date(*map(int,d.split('-'))).weekday()]:>3}{o['短'][0]:>9,.0f}{o['短'][1]:>9,}{o['短'][1]/o['短'][0]:>7.2f}{'  ':2}{o['長'][0]:>9,.0f}{o['長'][1]:>9,}{m:>7.2f}{lp:>9,.0f} {flag}")
print(f"\n  長の「MER<分岐が3日連続」: 現在 {run}日連続 → {'🚨 日次トリガー該当＝即−25%' if run>=3 else '未該当'}")
print()
print('=== カタログ全部（テスト）の広告費 ===')
for lbl,ds in [('前日 8/09',['2026-08-09']),('3日 8/07-09',['2026-08-0%d'%i for i in (7,8,9)]),
               ('7日 8/03-09',['2026-08-0%d'%i for i in range(3,10)])]:
    print(f"  {lbl:14} {sum(A['カタログ全部（テスト）'][d] for d in ds):>10,.0f}円")
print('  → レポートの表に載せた166,990円は【7日合計】。前日は24,064円です')
print()
print('=== 利益率のレバー分解（利益率 = 1 − 原価率 − 1/MER） ===')
for lbl,k in [('7日 8/03-09','d7'),('30日 7/11-8/09','d30')]:
    N=R['N7'] if k=='d7' else R['N30']; K=R['K7'] if k=='d7' else R['K30']
    AC=R['ACCT7'] if k=='d7' else R['ACCT30']
    s=sum(N.values()); c=sum(K.values())
    print(f"  {lbl:16} 原価率 {c/s*100:>5.2f}%  MER {s/AC:>5.2f}  広告費率 {AC/s*100:>5.2f}%  → 利益率 {(1-c/s-AC/s)*100:>5.2f}%")
s7=sum(R['N7'].values()); c7=sum(R['K7'].values()); a7=R['ACCT7']
print(f"\n  現在(7日): 原価率 {c7/s7*100:.2f}% / 広告費率 {a7/s7*100:.2f}% / 利益率 {(1-c7/s7-a7/s7)*100:.2f}%")
print('  利益率を+1pt上げるのに必要な変化:')
print(f"    ・原価率を −1.00pt（=原価 {s7*0.01:,.0f}円/週の削減）")
print(f"    ・MERを {1/(a7/s7):.3f} → {1/(a7/s7-0.01):.3f}（+{(1/(a7/s7-0.01))/(1/(a7/s7))*100-100:.1f}%）")
print(f"    ・広告費を {a7:,.0f} → {a7-s7*0.01:,.0f}円/週（−{s7*0.01/a7*100:.1f}%）※ただし売上も落ちる")
