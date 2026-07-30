# -*- coding: utf-8 -*-
"""変化型3日シグナルの日次計算（SKILL 7d-0）
使い方: python3 signal3.py <daily_sales.csv> <daily_ad.csv> [基準日=最終日]
  シグナル = 直近3日の曜日補正MER ÷ 直前7日(祝日除く)の曜日補正MER
    <=0.75 → 減額 / >=1.25 → 増額 / その間 → 触らない
  ガード: 予算変更から7日ロック・同時増額は最大2商品
検証(6/29-7/29): 悪化シグナル72%的中・改善シグナル68%的中（水準型の分岐割れは24%）"""
import csv, sys, collections, datetime
SALES, AD = sys.argv[1], sys.argv[2]
SNAP = '/home/user/LOOana/data/budget-snapshots.csv'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'UV歯ブラシ除菌器':3240,'ナノガラス脱毛パッド':751,'壁掛けディスペンサー':2318}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
BREAKEVEN={'4WAY':1.57,'害虫ブロッカー':1.31,'形状記憶日傘':1.37,'完全遮光・形状記憶':1.37,'卓上冷感クーラー':1.53,
'接触冷感UVパーカー':1.58,'5WAY腰掛けファン':1.66,'偏光・調光サングラス':1.30,'3WAYサーキュレーター':1.76,
'接触冷感UVアームカバー':1.25,'健康サンダル':1.32,'瞬間冷感ポンチョ':1.36,'ムダ毛シェーバー':1.77,
'携帯電動シェーバー':1.54,'バランスケアスリッパ':1.37,'UV歯ブラシ除菌器':1.58,'ナノガラス脱毛パッド':1.24,'壁掛けディスペンサー':1.56}
SEASON_END = {'4WAY','形状記憶日傘','完全遮光・形状記憶','卓上冷感クーラー','5WAY腰掛けファン','害虫ブロッカー',
              '接触冷感UVパーカー','接触冷感UVアームカバー','瞬間冷感ポンチョ','偏光・調光サングラス','3WAYサーキュレーター'}
HOLIDAYS={'2026-07-20'}
IDX={'日':120.9,'水':103.4,'土':102.9,'金':99.9,'木':94.3,'火':89.8,'月':87.2}
WD=['月','火','水','木','金','土','日']; wd=lambda x: WD[datetime.date(*map(int,x.split('-'))).weekday()]

S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0])); A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(SALES,encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
for r in csv.DictReader(open(AD,encoding='utf-8')):
    A[r['campaign']][r['date']]+=float(r['cost'])
B=collections.defaultdict(dict)
for r in csv.DictReader(open(SNAP,encoding='utf-8')):
    B[r['campaign']][r['snapshot_date']]=B[r['campaign']].get(r['snapshot_date'],0)+int(r['daily_budget'])

ALL=[d for d in sorted({d for v in S.values() for d in v}) if d not in HOLIDAYS]
END = sys.argv[3] if len(sys.argv)>3 else ALL[-1]
i = ALL.index(END)+1
CUR3, BASE = ALL[i-3:i], ALL[i-10:i-3]

def mer(n, ds):
    s=sum((S[n][d][0]-S[n][d][1])/(IDX[wd(d)]/100) for d in ds if d in S[n])
    a=sum(A[MAP.get(n,n)].get(d,0) for d in ds)
    return s/a if a>2000 else None
def last_change(n):
    c=MAP.get(n,n); ks=sorted(B[c]); prev=None; last=None
    for d in ks:
        if prev is not None and B[c][d]!=prev: last=d
        prev=B[c][d]
    return last

out=[]
for n in BREAKEVEN:
    b, c = mer(n, BASE), mer(n, CUR3)
    if not b or not c: continue
    ratio=c/b
    sig = '減額' if ratio<=0.75 else ('増額' if ratio>=1.25 else '—')
    reason=''
    lc=last_change(n)
    if sig!='—' and lc and lc > ALL[i-8]:
        sig, reason = 'ロック', f'{lc[5:]}に予算変更→7日ロック'
    if sig=='増額' and n in SEASON_END: reason='※季節終盤: 増額可否は残シーズン週数を確認'
    cur=B[MAP.get(n,n)].get(ALL[-1])
    out.append((ratio, n, b, c, BREAKEVEN[n], sig, cur, reason))
out.sort()
print(f'変化型3日シグナル（直近3日 {CUR3[0][5:]}-{CUR3[-1][5:]} vs ベースライン {BASE[0][5:]}-{BASE[-1][5:]}・曜日補正済み）')
print(f"{'商品':<20}{'基準MER':>8}{'直近3日':>8}{'比':>7}{'分岐':>6}{'判定':>8}{'現予算':>9}  理由")
for ratio,n,b,c,br,sig,cur,reason in out:
    mark={'減額':'🔻','増額':'🔺','ロック':'⏸','—':'  '}[sig]
    print(f'{n:<20}{b:>8.2f}{c:>8.2f}{ratio:>7.2f}{br:>6.2f}{mark+sig:>8}{(cur or 0):>9,}  {reason}')
ups=[x for x in out if x[5]=='増額']
if len(ups)>2:
    print(f'\n⚠️ 増額シグナルが{len(ups)}件。同時増額は最大2商品なので、比が大きい順に上位2件のみ実行:')
    for x in sorted(ups, key=lambda z:-z[0])[:2]: print(f'   → {x[1]}（比 {x[0]:.2f}）')
