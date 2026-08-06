# 2026-08-07 朝の確定再取得（SKILL 5e: 前日分は翌朝に必ず再取得する）
import csv
D='2026-08-06'
AD=[('ナノガラス脱毛パッド',79643),('4WAY 取り付けOK 小型瞬間冷却ハンディファン',46236),('害虫ブロッカー',39261),
('形状記憶日傘',36387),('完全遮光・形状記憶・晴雨兼用・UV日傘',29978),('接触冷感UVパーカー',29805),
('偏光・調光サングラス',24216),('カタログ全部（テスト）',21186),('ムダ毛シェーバー',18689),
('W固定スマホ車載ホルダー',17380),('5WAY腰掛けファン',15324),('接触冷感UVアームカバー',13933),
('卓上冷感クーラー',12422),('携帯電動シェーバー',10242),('姿勢サポートチェア',9029),('瞬間冷感ポンチョ',8559),
('完全遮光・接触冷感UVハット',6726),('2WAYシートボックス',6413),('バランスケアスリッパ',5752),
('3WAYサーキュレーター扇風機',5602),('健康サンダル',4818)]
old={}
rows=[r for r in csv.reader(open('data/daily/daily_ad.csv'))]
hdr=rows[0]
for r in rows[1:]:
    if r and r[0]==D: old[r[1]]=float(r[2])
body=[r for r in rows[1:] if r and r[0]!=D]
for c,v in AD: body.append([D,c,v])
with open('data/daily/daily_ad.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(body)
o=sum(old.values()); n=sum(v for _,v in AD)
print(f'8/06 広告費 速報 {o:,.0f} → 確定 {n:,.0f}  ドリフト {n-o:+,.0f}円 ({(n/o-1)*100:+.3f}%)')
for c,v in AD:
    d=v-old.get(c,0)
    if abs(d)>=10: print(f'  {c[:26]:28}{old.get(c,0):>9,.0f} → {v:>9,.0f}  {d:+,.0f}')
