# -*- coding: utf-8 -*-
"""2026-08-16 定例レポートの計算本体（昨日=8/15 土）。数値はすべて w0815.py の実測窓から。"""
import pickle, csv, collections, datetime, json
R = pickle.load(open('/tmp/rep0815w.pkl', 'rb')); FEE = 0.03452
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
COST, PRICE, MAP = R['COST'], R['PRICE'], R['MAP']; INV = {v: k for k, v in MAP.items()}
D5 = D7[-5:]                                   # 3窓判定用の5日窓 8/11-15

# ── Shopify実測（2026-08-16取得）: 商品別 注文数（7日 8/09-15）
ORD7 = {'ナノガラス脱毛パッド':289,'W固定スマホ車載ホルダー':146,'害虫ブロッカー':80,'接触冷感UVパーカー':75,
'形状記憶日傘':66,'偏光・調光サングラス':47,'ムダ毛シェーバー':44,'2WAYシートボックス':39,'4WAY':39,
'完全遮光・接触冷感UVハット':38,'完全遮光・形状記憶':28,'接触冷感UVアームカバー':26,'優先配送':26,
'姿勢サポートチェア':24,'5WAY腰掛けファン':23,'快適マジックインソール':22,'バランスケアスリッパ':13,
'携帯電動シェーバー':10,'卓上冷感クーラー':9,'壁掛けディスペンサー':2,'ナノバブルシャワーヘッド':2,
'3WAYサーキュレーター':2,'瞬間冷感ポンチョ':2,'健康サンダル':1,'UV歯ブラシ除菌器':1}
STORE_ORD = {'d1':142,'d3':387,'d7':1015,'cum':2555}
STORE_ITEMS7 = 1243; RETURN_CUM = 71649
assert abs(sum(ORD7.values()) - 1015 - 39) == 0, 'Σ商品注文 − 全店注文 = ミックス超過39件のはず'

# ── Meta実測（キャンペーン別）W0=8/09-15 / W1=8/02-08 : cost,imp,linkCTR,CPM,Freq,outclicks
W0 = {'ナノガラス脱毛パッド':(559493,344973,.0257,1621.8,1.163,8866),'害虫ブロッカー':(274330,128163,.0199,2140.5,1.166,2494),
'形状記憶日傘':(244671,75325,.0380,3248.2,1.092,2867),'W固定スマホ車載ホルダー':(230922,161230,.0291,1432.3,1.146,4519),
'接触冷感UVパーカー':(194169,65806,.0310,2950.6,1.178,2052),'カタログ全部（テスト）':(159832,40732,.0380,3924.0,1.806,1453),
'ムダ毛シェーバー':(139499,115459,.0125,1208.2,1.432,1398),'4WAY':(137033,32161,.0312,4260.8,1.349,1003),
'完全遮光・形状記憶':(130898,32775,.0452,3993.8,1.161,1420),'偏光・調光サングラス':(124973,55109,.0281,2267.7,1.244,1490),
'2WAYシートボックス':(100709,42614,.0286,2363.3,1.202,1190),'5WAY腰掛けファン':(88426,29748,.0398,2972.5,1.154,1158),
'完全遮光・接触冷感UVハット':(79793,20874,.0515,3822.6,1.078,1041),'姿勢サポートチェア':(69928,54991,.0187,1271.6,1.111,997),
'接触冷感UVアームカバー':(55741,13144,.0326,4240.8,1.509,416),'快適マジックインソール':(46888,21911,.0319,2139.9,1.135,697),
'バランスケアスリッパ':(34998,26492,.0160,1321.1,1.194,411),'卓上冷感クーラー':(33644,14128,.0377,2381.4,1.155,521),
'携帯電動シェーバー':(28095,10433,.0230,2692.9,1.301,225),'瞬間冷感ポンチョ':(21092,4733,.0344,4456.4,1.164,154),
'ナノバブルシャワーヘッド':(6186,1990,.0588,3108.5,1.106,109)}
W1 = {'ナノガラス脱毛パッド':(556747,313414,.0262,1776.4,1.229,8053),'4WAY':(377757,88692,.0343,4259.2,1.463,3014),
'害虫ブロッカー':(349260,159765,.0212,2186.1,1.109,3207),'形状記憶日傘':(310706,109684,.0379,2832.7,1.125,4125),
'接触冷感UVパーカー':(215073,65396,.0375,3288.8,1.182,2421),'完全遮光・形状記憶':(210495,55664,.0481,3781.5,1.217,2566),
'カタログ全部（テスト）':(175026,50297,.0395,3479.8,1.660,1891),'偏光・調光サングラス':(153955,77133,.0241,1996.0,1.183,1733),
'ムダ毛シェーバー':(135606,121550,.0137,1115.6,1.316,1583),'5WAY腰掛けファン':(122332,43738,.0454,2796.9,1.191,1901),
'卓上冷感クーラー':(118110,44441,.0448,2657.7,1.148,1901),'W固定スマホ車載ホルダー':(101531,49946,.0320,2032.8,1.145,1514),
'接触冷感UVアームカバー':(94072,26895,.0284,3497.8,1.414,730),'瞬間冷感ポンチョ':(71240,15127,.0498,4709.5,1.387,716),
'携帯電動シェーバー':(68183,35472,.0164,1922.2,1.404,564),'3WAYサーキュレーター':(67115,16574,.0392,4049.4,1.207,634),
'完全遮光・接触冷感UVハット':(55834,12589,.0483,4435.1,1.140,582),'健康サンダル':(55743,18264,.0294,3052.1,1.189,524),
'姿勢サポートチェア':(52847,28918,.0213,1827.5,1.173,589),'バランスケアスリッパ':(34956,18994,.0201,1840.4,1.204,359),
'2WAYシートボックス':(28182,10474,.0281,2690.7,1.083,286),'UV歯ブラシ除菌器':(25611,8847,.0228,2894.9,1.165,188),
'壁掛けディスペンサー':(4145,1232,.0381,3364.4,1.068,47)}
for lbl, W, days in [('W0', W0, D7), ('W1', W1, D7)]:
    pass
_w0 = sum(v[0] for v in W0.values())
# 許容は SKILL 既定の ±0.1%（Metaは確定まで数値がわずかに動く）。損益はCSV側の値を正とする。
assert abs(_w0 / R['ACCT7'] - 1) < 0.001, ('W0合計とCSV7日広告費が0.1%超のズレ', _w0, R['ACCT7'])
print(f"[照合] 7日広告費 ファネルクエリ {_w0:,} vs CSV {R['ACCT7']:,.0f} = {(_w0/R['ACCT7']-1)*100:+.3f}%（許容±0.1%）")

# ── 現日予算（2026-08-16スナップショット。害虫は停止＝0）
BUD = collections.defaultdict(int); BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.reader(open('data/budget-snapshots.csv')):
    if not r or not r[0][0].isdigit(): continue
    k = INV.get(r[1], r[1])
    BSNAP[k][r[0]] += int(r[3])
    if r[0] == '2026-08-16': BUD[k] += int(r[3])
BUDTOT = sum(BUD.values())
def budsum(n, days):   # 窓内の「その日に設定されていた予算」の合計。当日変更の歪みを避ける
    return sum(BSNAP[n].get(d, 0) for d in days)

def win(days, key):
    N, K, A = R['N' + key], R['K' + key], R['A' + key]
    return N, K, A
SETS = {'d1': (R['N1'], R['K1'], R['A1'], R['CAT1'], R['ACCT1'], D1),
        'd3': (R['N3'], R['K3'], R['A3'], R['CAT3'], R['ACCT3'], D3),
        'd7': (R['N7'], R['K7'], R['A7'], R['CAT7'], R['ACCT7'], D7),
        'd30': (R['N30'], R['K30'], R['A30'], R['CAT30'], R['ACCT30'], D30)}

# ── 5日窓（3窓判定用）は日次から積み直す
S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv', encoding='utf-8')):
    S[r['name']][r['date']][0] += int(r['gross']); S[r['name']][r['date']][1] += int(r['disc'])
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv', encoding='utf-8')):
    AD[r['campaign']][r['date']] += float(r['cost'])
def sal(n, days): return sum(S[n][d][0] - S[n][d][1] for d in days if d in S[n])
def adv(n, days): return sum(AD[MAP.get(n, n)].get(d, 0) for d in days)

print('=' * 100)
print(f"【全体】 昨日 {D1[0]} (土)   曜日指数 {R['IDX']['土']:.1f}")
GT = {}
for k, (N, K, A, cat, acct, days) in SETS.items():
    s = sum(N.values()); c = sum(K.values()); a = acct; p = s - c - a
    GT[k] = dict(s=s, c=c, a=a, p=p, r=p / s, fee=p - s * FEE, days=len(days))
    print(f"  {k:4} {len(days):2}日 売上{s:>11,} 原価{c:>10,} 広告{a:>11,.0f} 総合原価{c+a:>11,.0f}({(c+a)/s*100:4.1f}%) "
          f"利益{p:>10,.0f}({p/s*100:4.1f}%) 手数料後{p-s*FEE:>10,.0f}({(p-s*FEE)/s*100:4.1f}%) 日平均利益{p/len(days):>9,.0f}")
NC, KC = sum(R['NC'].values()), sum(R['KC'].values()); AC_ = R['ACCTC']
pc = NC - KC - AC_
print(f"  当月 {len(CUM)}日 売上{NC:>11,} 原価{KC:>10,} 広告{AC_:>11,.0f} 利益{pc:>10,.0f}({pc/NC*100:4.1f}%) 手数料後{pc-NC*FEE:>10,.0f}")
print(f"  当月返品 {RETURN_CUM:,}円（返品率 {RETURN_CUM/NC*100:.2f}%）")
print(f"  現日予算合計 {BUDTOT:,}円/日（害虫ブロッカー停止で −37,000）")

# ── 日次利益（床10万円との距離）
DP = {}
for d in D7:
    s = sum(S[n][d][0] - S[n][d][1] for n in S if d in S[n])
    a = sum(AD[c].get(d, 0) for c in AD)
    DP[d] = (s, a)
print('\n【日次利益】原価は日次の実測（qty()と同じ計算）。近似なし。')
WD = ['月','火','水','木','金','土','日']; KDAY = R['KDAY']; mv = []
for d in R['D30'][-14:]:
    s, a = (sum(S[n][d][0]-S[n][d][1] for n in S if d in S[n]), sum(AD[c].get(d,0) for c in AD))
    pr = s - KDAY[d] - a; mv.append(pr)
    mark = '  ← 床10万円割れ' if pr < 100000 else ''
    print(f"  {d}({WD[datetime.date(*map(int,d.split('-'))).weekday()]}) 売上{s:>9,} 原価{KDAY[d]:>8,} 広告{a:>9,.0f} 利益{pr:>9,.0f} ({pr/s*100:4.1f}%){mark}")
m3 = sum(mv[-3:]) / 3
print(f"  3日移動平均 {m3:>10,.0f}円 … 非常ブレーキ閾値130,000円 → {'🚨発動' if m3<130000 else '未発動'}")
gai7 = 82890
print(f"  ※ 害虫ブロッカーは8/15に広告停止（PSE対応）。7日利益+{gai7:,}円=日{gai7/7:,.0f}円がこの先は乗らない")
print(f"     → 害虫ぬきの7日日平均利益 = {(GT['d7']['p']-gai7)/7:,.0f}円/日")

# ── 商品別
print('\n' + '=' * 100)
print(f"{'商品':26}{'7日売上':>10}{'原価':>9}{'広告':>9}{'利益':>9}{'率':>6}{'MER':>6}{'分岐':>6}{'余裕':>7}{'目標':>6}{'注文':>5}{'点/注':>6}{'CPA注':>7}{'分岐CPA':>8}{'消化率':>7}{'日予算':>8}")
rowsout = []
for n in sorted(set(R['N7']) | set(BUD), key=lambda x: -R['N7'].get(x, 0)):
    if n == '': continue
    s7 = R['N7'].get(n, 0); k7 = R['K7'].get(n, 0); a7 = R['A7'].get(n, 0)
    if s7 == 0 and a7 == 0: continue
    p7 = s7 - k7 - a7; q7 = R['Q7'].get(n, 0); o7 = ORD7.get(n, 0)
    gr = 1 - k7 / s7 if s7 else 0
    be = 1 / gr if gr > 0 else 0
    tgt = 1 / (gr - .35) if gr > .35 else 0
    mer = s7 / a7 if a7 else 0
    ipo = q7 / o7 if o7 else 0
    gpu = (s7 - k7) / q7 if q7 else 0
    gpo = (s7 - k7) / o7 if o7 else 0
    cpao = a7 / o7 if o7 else 0
    bud = BUD.get(n, 0)
    b7 = budsum(n, D7); cons = a7 / b7 if b7 else 0
    rowsout.append(dict(n=n, s7=s7, k7=k7, a7=a7, p7=p7, q7=q7, o7=o7, gr=gr, be=be, tgt=tgt, mer=mer,
                        ipo=ipo, gpu=gpu, gpo=gpo, cpao=cpao, bud=bud, cons=cons))
    if a7 == 0:
        print(f"{n[:25]:26}{s7:>10,}{k7:>9,}{'—':>9}{p7:>9,.0f}{p7/s7*100:>5.0f}%{'—':>6}{'—':>6}{'—':>7}{'—':>6}{o7:>5}{ipo:>6.2f}{'—':>7}{'—':>8}{'—':>7}{'—':>8}")
    else:
        print(f"{n[:25]:26}{s7:>10,}{k7:>9,}{a7:>9,.0f}{p7:>9,.0f}{p7/s7*100:>5.0f}%{mer:>6.2f}{be:>6.2f}{mer-be:>+7.2f}"
              f"{(tgt if tgt else 0):>6.2f}{o7:>5}{ipo:>6.2f}{cpao:>7,.0f}{gpo:>8,.0f}{cons*100:>6.0f}%{bud:>8,}")
print(f"{'カタログ全部（テスト）※横断':26}{'—':>10}{'—':>9}{R['CAT7']:>9,.0f}{'—':>9}{'—':>6}{'—':>6}{'—':>6}{'—':>7}{'—':>6}{'—':>5}{'—':>6}{'—':>7}{'—':>8}{R['CAT7']/budsum('カタログ全部（テスト）',D7)*100:>6.0f}%{23000:>8,}")
assert abs(sum(r['a7'] for r in rowsout) + R['CAT7'] - R['ACCT7']) < 2, '商品広告費+カタログ = アカウント消化 が不一致'
print(f"  ✅ 商品別広告費 {sum(r['a7'] for r in rowsout):,.0f} + カタログ {R['CAT7']:,.0f} = Meta実消化 {R['ACCT7']:,.0f}")
print(f"  ✅ 全店1注文あたり粗利（＝カタログの分岐CPA）= {(GT['d7']['s']-GT['d7']['c'])/STORE_ORD['d7']:,.0f}円 "
      f"／ カタログCPA(注文) は Meta計上でしか出せない")

# ── 3窓判定（3日/5日/7日）と頑健性（限界MER=平均×0.6/0.7/0.8）
print('\n' + '=' * 100)
print('【3窓判定】3日(8/13-15) / 5日(8/11-15) / 7日(8/09-15)  ※3窓一致のときだけ動かす')
print(f"{'商品':24}{'MER3':>7}{'MER5':>7}{'MER7':>7}{'分岐':>7}{'目標':>7}{'判定':>16}  頑健性(×.6/.7/.8 vs 分岐)")
JUD = {}
for r in sorted(rowsout, key=lambda x: -x['a7']):
    n = r['n']
    if r['a7'] == 0 or r['bud'] == 0: continue
    ms = []
    for dd in (D3, D5, D7):
        a = adv(n, dd); ms.append(sal(n, dd) / a if a else 0)
    be, tgt = r['be'], r['tgt']
    if all(m < be for m in ms): j = '🚨 停止/−50%'
    elif all(m - be < .30 for m in ms): j = '🔻 −25%'
    elif all(m >= tgt for m in ms) and tgt and r['cons'] >= .95: j = '🚀 +25%'
    else: j = '⏸ 据え置き'
    rb = ['+' if r['mer'] * f > be else '-' for f in (.6, .7, .8)]
    JUD[n] = (ms, j, ''.join(rb))
    print(f"{n[:23]:24}{ms[0]:>7.2f}{ms[1]:>7.2f}{ms[2]:>7.2f}{be:>7.2f}{(tgt or 0):>7.2f}{j:>16}  {''.join(rb)}"
          f"{'  ⚠️端で逆転' if len(set(rb))>1 else ''}")

# ── 予算1円あたりの利益（削減側/増額側）※限界MER=平均×0.7
print('\n' + '=' * 100)
print('【動かしたときの変化量】限界MER=平均×0.7（実測がある商品は本文で上書き）')
print(f"{'商品':24}{'限界MER':>8}{'追加1円':>9}{'削減1円':>9}{'−25%で+利益/週':>15}{'+25%で+利益/週':>15}")
for r in sorted(rowsout, key=lambda x: -x['a7']):
    if r['a7'] == 0 or r['bud'] == 0: continue
    lm = r['mer'] * .7; gr = r['gr']
    add = lm * gr - 1; cut = 1 - lm * gr
    print(f"{r['n'][:23]:24}{lm:>8.2f}{add:>+9.3f}{cut:>+9.3f}{cut*r['a7']*.25:>15,.0f}{add*r['a7']*.25:>15,.0f}")

# ── Meta週次ファネル（W1 8/02-08 → W0 8/09-15）
print('\n' + '=' * 100)
print('【週次ファネル】CTR=Meta / CVR=Shopify注文÷Metaクリック / 売上per click=Shopify実売÷クリック')
print(f"{'商品':24}{'CTR前':>7}{'CTR今':>7}{'Δ':>7}{'CVR今':>7}{'CPM前':>7}{'CPM今':>7}{'Δ':>7}{'頻度':>6}{'売上/CL':>8}")
SPC = {}
for r in sorted(rowsout, key=lambda x: -x['a7']):
    n = r['n']
    if n not in W0: continue
    c0, i0, t0, m0, f0, k0 = W0[n]
    cvr = r['o7'] / k0 if k0 else 0; spc = r['s7'] / k0 if k0 else 0; SPC[n] = spc
    if n in W1:
        _, _, t1, m1, _, _ = W1[n]
        print(f"{n[:23]:24}{t1*100:>6.2f}%{t0*100:>6.2f}%{(t0/t1-1)*100:>+6.0f}%{cvr*100:>6.2f}%{m1:>7,.0f}{m0:>7,.0f}{(m0/m1-1)*100:>+6.0f}%{f0:>6.2f}{spc:>8,.0f}")
    else:
        print(f"{n[:23]:24}{'—':>7}{t0*100:>6.2f}%{'—':>7}{cvr*100:>6.2f}%{'—':>7}{m0:>7,.0f}{'—':>7}{f0:>6.2f}{spc:>8,.0f}")
vals = sorted(SPC.values()); md = vals[len(vals)//2]
print(f"  売上/クリック 中央値 {md:,.0f}円 ／ 下位25% {vals[len(vals)//4]:,.0f}円 … LP改修の対象はここより下だけ")

# ── 全店週次MER（P-1ガード：直近3日 vs その前3日）
print('\n' + '=' * 100)
ALLD = sorted({d for v in S.values() for d in v}); ALLD = [d for d in ALLD if d <= '2026-08-15']
def storemer(days):
    s = sum(S[n][d][0] - S[n][d][1] for n in S for d in days if d in S[n])
    a = sum(AD[c].get(d, 0) for c in AD for d in days)
    return s, a, (s / a if a else 0)
print('【全店 週次MER】')
prev = None
for i in range(5, 0, -1):
    w = ALLD[-7*i:len(ALLD)-7*(i-1)] if i > 1 else ALLD[-7:]
    s, a, m = storemer(w)
    d = f'{(m/prev-1)*100:+.1f}%' if prev else '—'
    print(f"  {w[0]}〜{w[-1]} 売上{s:>10,} 広告{a:>10,.0f} MER {m:.3f}  {d}")
    prev = m
a3 = storemer(D3); b3 = storemer(ALLD[-6:-3])
print(f"  P-1（直近3日 vs その前3日）: {b3[2]:.3f} → {a3[2]:.3f} = {(a3[2]/b3[2]-1)*100:+.1f}% → "
      f"{'🚨発動（未測定の増額は禁止）' if a3[2]/b3[2]-1 <= -0.08 else '未発動'}")
json.dump({'rows': rowsout, 'GT': GT, 'BUD': dict(BUD), 'JUD': {k: (v[0], v[1], v[2]) for k, v in JUD.items()}},
          open('/tmp/a0816.json', 'w'), ensure_ascii=False, default=float)
