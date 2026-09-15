# -*- coding: utf-8 -*-
"""9/14広告費を確定値で上書き（アカウント合計221,456と差0円。暫定220,988から+468円）"""
import csv
FINAL={'ナノガラス脱毛パッド':70829,'伸縮ガラスクリーナー':30962,'W固定スマホ車載ホルダー':28803,
'快適マジックインソール':28117,'高見えレザーヘッドレストフック':15470,'カタログ全部（テスト）':13088,
'バランスケアスリッパ':10663,'ムダ毛シェーバー':10243,'姿勢サポートチェア':8951,
'もちふわ肉球サンダル':4314,'4-in-1マルチクリーナー':16}
assert sum(FINAL.values())==221456, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-14' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-14')
print('updated',n,'rows / 9/14合計',tot); assert tot==221456
