import collections,os
D=os.path.dirname(os.path.abspath(__file__))+'/'
T=collections.OrderedDict()
for line in open(D+'adset_week.txt'):
    p=line.strip().split(',')
    if len(p)<9: continue
    w=p[0].split('|')[1]; v=[0 if x=='null' else int(x) for x in p[3:]]
    T.setdefault(p[1],collections.OrderedDict()).setdefault(p[2],{})[w]=v
WK={'40':'9/28','41':'10/05','42':'10/12','43':'10/19','44':'10/26','45':'11/2'}
for camp,sets in T.items():
    print('\n'+camp+'  （週: 広告費 / CPM / CTR / LPV→Meta購入）')
    for s,wk in sets.items():
        out=[]
        for w in ['40','41','42','43','44','45']:
            v=wk.get(w)
            if not v or v[1]==0: out.append(f"{WK[w]}: —"); continue
            out.append(f"{WK[w]}: {v[0]/1000:,.0f}k/{v[0]/v[1]*1000:,.0f}/{v[3]/v[1]:.2%}/{(v[5]/v[4] if v[4] else 0):.1%}")
        print('  '+s.replace(camp,'').strip() .replace('（BC検証用）','') or '  主力', ' | '.join(out))
