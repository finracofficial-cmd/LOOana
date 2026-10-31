# -*- coding: utf-8 -*-
"""時間別シート用データ（10/31 土 vs 前週土10/24 vs 10/25-30の6日平均）。Meta時間別 data_query・Shopify GROUP BY day,hour_of_day の結果を転記し、日次合計で検算する"""
import json, csv, collections, os
H=os.path.dirname(os.path.abspath(__file__))+'/h1031/'
M={}
for l in open(H+'meta.txt'):
    d,*hs=l.strip().split('|'); M[d]=[tuple(int(x) for x in h.split(',')) for h in hs]; assert len(M[d])==24
S={}
for l in open(H+'shop.txt'):
    d,*hs=l.strip().split('|'); S[d]={int(h.split(':')[0]):(int(h.split(':')[1]),int(h.split(':')[2])) for h in hs}
SES=[tuple(int(x) for x in h.split(',')) for h in open(H+'ses.txt').read().strip().split('|')]
B='/home/user/LOOana/data/daily/'
G=collections.defaultdict(int); A=collections.defaultdict(float)
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')): G[r['date']]+=int(r['gross'])
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')): A[r['date']]+=float(r['cost'])
D6=['2026-10-%02d'%d for d in range(25,31)]
for d in S: assert sum(v[0] for v in S[d].values())==G[d], (d, sum(v[0] for v in S[d].values()), G[d])
assert sum(v[1] for v in S['2026-10-31'].values())==70
assert sum(s for s,_ in SES)==2659 and sum(c for _,c in SES)==152
for d in M:
    s=sum(m[0] for m in M[d]); print(d,'Meta時間別合計',s,'日次CSV',round(A[d]),'差',round(s-A[d])); assert abs(s-A[d])<=max(30,A[d]*0.002)
M31,M24=M['2026-10-31'],M['2026-10-24']; M6=[tuple(sum(M[d][h][i] for d in D6) for i in range(4)) for h in range(24)]
S31,S24=S['2026-10-31'],S['2026-10-24']; S6={h:(sum(S[d].get(h,(0,0))[0] for d in D6),sum(S[d].get(h,(0,0))[1] for d in D6)) for h in range(24)}
rows=[]
for h in range(24):
    a,b,c=M31[h],M24[h],[x/6 for x in M6[h]]
    g31,o31=S31.get(h,(0,0)); g24,o24=S24.get(h,(0,0)); g6,o6=[x/6 for x in S6[h]]
    rows.append([f'{h:02d}時台',a[0],b[0],round(c[0]),a[1],b[1],round(c[1]),a[2],b[2],round(c[2],1),a[3],b[3],round(c[3],1),
                 g31,g24,round(g6),o31,o24,round(o6,1),round(g31/a[0],2) if a[0] else None,round(g24/b[0],2) if b[0] else None,round(g6/c[0],2) if c[0] else None,SES[h][0],SES[h][1]])
json.dump({'rows':rows},open(os.path.dirname(os.path.abspath(__file__))+'/hourly1031.json','w'),ensure_ascii=False)
def blk(hs):
    m=[sum(M31[h][i] for h in hs) for i in range(4)]; m6=[sum(M6[h][i] for h in hs)/6 for i in range(4)]; mb=[sum(M24[h][i] for h in hs) for i in range(4)]
    g=sum(S31.get(h,(0,0))[0] for h in hs); o=sum(S31.get(h,(0,0))[1] for h in hs); g6=sum(S6[h][0] for h in hs)/6; o6=sum(S6[h][1] for h in hs)/6; ob=sum(S24.get(h,(0,0))[1] for h in hs)
    return f"広告{m[0]:,}（6日平均比{m[0]/m6[0]-1:+.0%}・前週土{mb[0]:,}）LPV{m[2]}（{m[2]/m6[2]-1:+.0%}）注文{o}（6日平均{o6:.1f}・前週土{ob}）gross{g:,}（{g/g6-1:+.0%}）"
for lab,hs in [('0-5',range(0,6)),('6-9',range(6,10)),('10-13',range(10,14)),('14-17',range(14,18)),('18-23',range(18,24))]: print(lab, blk(hs))
