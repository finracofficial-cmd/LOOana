# -*- coding: utf-8 -*-
"""10/15広告費を確定値で上書き（キャンペーン合算241,645円。暫定240,777から+868円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':36236,'むくみ取りかっさ':12108,'カタログ全部（テスト）':7960,'ナノガラス脱毛パッド':74437,
'ナノバブルシャワーヘッド':6383,'ハイウエストシェイプパンツ':4923,'ポータブルヒートシーラー':12794,'伸縮ガラスクリーナー':35543,
'快適マジックインソール':27197,'高見えレザーヘッドレストフック':15000,'4-in-1マルチクリーナー':9064}
assert sum(FINAL.values())==241645, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-15' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-15')
print('updated',n,'rows / 10/15合計',tot); assert tot==241645
