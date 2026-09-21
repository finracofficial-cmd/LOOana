# -*- coding: utf-8 -*-
"""2026-09-22 定例レポート本体（昨日=9/21 月・敬老の日）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep0921w.pkl', 'rb'))
FEE = 0.03436   # 2026-09-01 月次再計測。次回 10/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-09-22'   # 9/22 08時時点（9/21cリバランス後から変更検出なし）
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 256000, sum(BUD.values())
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
# --- 7日(9/15-9/21) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD = {'ナノガラス脱毛パッド':265,'伸縮ガラスクリーナー':141,'W固定スマホ車載ホルダー':119,
'快適マジックインソール':100,'高見えレザーヘッドレストフック':69,'もちふわ肉球サンダル':32,'バランスケアスリッパ':23,
'姿勢サポートチェア':19,'優先配送':18,'携帯電動シェーバー':13,'UV歯ブラシ除菌器':10,'ムダ毛シェーバー':7,
'電動温熱カッサ':3,'リカバリーサンダル':2,'接触冷感UVアームカバー':2,'完全遮光・接触冷感UVハット':2,
'ビジュアル耳かき':1,'3D足臭リセットブラシ':1,'ナノバブルシャワーヘッド':1,'完全遮光・形状記憶':1,'スタイルアップインナー':1}
STORE_ORD7, STORE_SESS7 = 805, 26676
assert sum(ORD.values()) == 830, sum(ORD.values())   # 全店805より多いのは複数商品を含む注文が両方で数えられるため

# --- 30日(8/23-9/21) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1136,'W固定スマホ車載ホルダー':501,'快適マジックインソール':396,
'伸縮ガラスクリーナー':263,'ムダ毛シェーバー':136,'バランスケアスリッパ':136,'姿勢サポートチェア':99,
'高見えレザーヘッドレストフック':97,'むくみ取りかっさ':78,'2WAYシートボックス':67,'ナノバブルシャワーヘッド':51,
'優先配送':36,'もちふわ肉球サンダル':34,'完全遮光・接触冷感UVハット':31,'偏光・調光サングラス':30,
'携帯電動シェーバー':27,'4-in-1マルチクリーナー':21,'3D足臭リセットブラシ':17,'温感EMSフェイシャルワンド':16,
'形状記憶日傘':15,'UV歯ブラシ除菌器':11,'4WAY':8,'ビジュアル耳かき':7,'完全遮光・形状記憶':6,
'壁掛けディスペンサー':6,'リカバリーサンダル':3,'ジェットウォッシャー':3,'接触冷感UVアームカバー':3,
'電動温熱カッサ':3,'高吸水・速乾ヘアドライタオル':2,'癒しの指圧マット':2,'スマートノーズEMS美顔器':2,
'接触冷感UVパーカー':2,'湯上がりガーゼワンピース':2,'ネックマッサージャー':1}

# --- 30日(8/23-9/21) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック）---
MF_RAW = {'ナノガラス脱毛パッド':(2417408,1238946,32588),'W固定スマホ車載ホルダー':(983918,377513,12517),
'快適マジックインソール':(875225,553008,13446),'カタログ全部（テスト）':(460842,115912,4154),
'ムダ毛シェーバー':(409436,341400,3840),'バランスケアスリッパ':(339685,223461,4306),
'伸縮ガラスクリーナー':(330318,134429,5733),'姿勢サポートチェア':(307341,163867,4089),
'2WAYシートボックス':(185040,58235,1453),'むくみ取りかっさ':(180745,52807,1584),
'高見えレザーヘッドレストフック':(176298,40555,1691),'ナノバブルシャワーヘッド':(163744,79679,1848),
'完全遮光・接触冷感UVハット':(98691,21493,916),'もちふわ肉球サンダル':(89892,27338,1228),
'4-in-1マルチクリーナー':(80605,23105,551),'偏光・調光サングラス':(76470,31507,853),
'温感EMSフェイシャルワンド':(64858,15636,456),'3D足臭リセットブラシ':(63234,19780,242),
'形状記憶日傘':(56710,14859,579),'UV歯ブラシ除菌器':(51512,18909,297),
'携帯電動シェーバー':(28104,12586,279),'ビジュアル耳かき':(26464,9402,148),
'電動温熱カッサ':(20149,5282,159),'カタログ全部（テスト） 夏以外':(6080,1903,50),
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':(4086,1056,20),'接触冷感UVアームカバー':(2709,455,20)}
MF = {INV.get(k, k): v for k, v in MF_RAW.items()}

SEA = {'4WAY','3WAYサーキュレーター','卓上冷感クーラー','5WAY腰掛けファン','瞬間冷却ハンディファン','接触冷感UVパーカー',
'接触冷感UVアームカバー','瞬間冷感ポンチョ','完全遮光・接触冷感UVハット','形状記憶日傘','完全遮光・形状記憶',
'偏光・調光サングラス','害虫ブロッカー','湯上がりガーゼワンピース'}

wb = Workbook(); wb.remove(wb.active)
TH = Font(name='Arial', bold=True, color='FFFFFF', size=10); TD = Font(name='Arial', size=10)
NEG = Font(name='Arial', size=10, color='CC0000'); HEAD = PatternFill('solid', fgColor='305496')
thin = Border(*[Side(style='thin', color='CCCCCC')] * 4)

def sh(title, note, cols, data, widths, fmt=None):
    ws = wb.create_sheet(title); r = 1
    if note:
        for ln in note: ws.cell(r, 1, ln).font = Font(name='Arial', size=10, bold=(r == 1)); r += 1
        r += 1
    for c, v in enumerate(cols, 1): ws.cell(r, c, v)
    for c in range(1, len(cols) + 1):
        x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin
        x.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[r].height = 30; hr = r; r += 1
    for row in data:
        for c, v in enumerate(row, 1):
            x = ws.cell(r, c, v); x.border = thin; x.font = TD
            if isinstance(v, (int, float)) and v < 0: x.font = NEG
            if fmt and c in fmt: x.number_format = fmt[c]
        r += 1
    for i, w_ in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i) if i < 27 else 'A' + chr(38 + i)].width = w_
    ws.freeze_panes = ws.cell(hr + 1, 1).coordinate
    return ws

# ===== 日次CSVを読む =====
Sd = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r_ in csv.DictReader(open('data/daily/daily_sales.csv')):
    Sd[r_['name']][r_['date']][0] += int(r_['gross']); Sd[r_['name']][r_['date']][1] += int(r_['disc'])
ADd = collections.defaultdict(lambda: collections.defaultdict(float))
for r_ in csv.DictReader(open('data/daily/daily_ad.csv')): ADd[r_['campaign']][r_['date']] += float(r_['cost'])
COSTa = dict(R['COST']); PRICEa = dict(R['PRICE'])
COSTa['ナノガラス脱毛パッド'] = (927 * 757 + 326 * 740) / 1253          # 30日実測ミックスの加重平均【近似】
COSTa['壁掛けディスペンサー'] = (7 * 2528 + 3 * 1981) / 10
PRICEa['壁掛けディスペンサー'] = 66800 / 10
ALLD = sorted({d for v in Sd.values() for d in v if d <= D1[0]})
D5 = ALLD[-5:]
def win(n, days):
    g = sum(Sd[n][d][0] for d in days if d in Sd[n]); dc = sum(Sd[n][d][1] for d in days if d in Sd[n])
    c = g / PRICEa[n] * COSTa[n] if g and n in PRICEa and n in COSTa else 0
    a = sum(ADd[MAP.get(n, n)].get(d, 0) for d in days)
    return g - dc, c, a

# ---------- 0 収益 ----------
WDJ0 = ['月', '火', '水', '木', '金', '土', '日']
def dayblk(d):
    s = c = 0
    for n, v in Sd.items():
        if n == '' or d not in v: continue
        g, dc = v[d]
        if not g: continue
        s += g - dc
        if n in PRICEa and n in COSTa: c += g / PRICEa[n] * COSTa[n]
    a = sum(ADd[cp].get(d, 0) for cp in ADd)
    return s, c, a, s - c - a

PROF = []
_pl = [dayblk(d) for d in ALLD]
for i, d in enumerate(ALLD):
    if d < ALLD[-21]: continue
    s, c, a, p = _pl[i]
    ma = sum(_pl[j][3] for j in range(i-2, i+1)) / 3 if i >= 2 else None
    PROF.append([d, WDJ0[datetime.date.fromisoformat(d).weekday()], round(s), round(c), round(a),
                 round(p), round(p/s, 4), round(p - s*FEE), round(s/a, 2) if a else '',
                 round(ma) if ma else '', ('🚨' if ma and ma < 130000 else ('✅' if ma else '')),
                 '★昨日' if d == D1[0] else ''])
# 8月確定（広告費の上書き後の最終値）と9月の滑り出し
AUG = [d for d in ALLD if '2026-08-01' <= d <= '2026-08-31']
_au = [dayblk(d) for d in AUG]
aus = sum(x[0] for x in _au); auc = sum(x[1] for x in _au); aua = sum(x[2] for x in _au); aup = aus-auc-aua
_cum = [dayblk(d) for d in CUM]
cs = sum(x[0] for x in _cum); cc = sum(x[1] for x in _cum); ca = sum(x[2] for x in _cum); cp = cs-cc-ca
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
sh('収益', [f'LOOTY 収益レポート 2026-09-22（昨日 = 9/21 月・敬老の日）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★9月累積（9/01-21・{len(CUM)}日）: 実売 {cs:,.0f} / 利益 {cp:,.0f}円（{cp/cs:.1%}）／1日あたり {cp/len(CUM):,.0f}円（8月確定は {aup:,.0f}円・{aup/31:,.0f}円/日）',
  '★9/21(月・敬老の日)は 実売 **751,971円**・利益 **+275,077円（36.6%）**・MER 2.69＝**売上・利益とも9月最高日**。利益率は北極星35%を初超え。前週月曜(平日)比+54.3%は祝日ルールで読む',
  '★注文150件・セッション4,571・CVR **3.28%**（3日連続で切り上がり）。フック34個（値引14,129円=ペア買い多発）・ナノ52個・ガラス35個と主力が全開。返品2点（インソール・優先配送）',
  '✅ ブレーキ余裕: 3日移動平均 **234,067円/日**（9/19-21）＝9月最高水準。祝日3連発 +702,202円',
  '🚀 増額組の初日: フック+51,722円・**MER5.10**（20,000でも効率維持）／ガラス+66,199円・MER3.93／インソール+24,244円・MER2.03（3本中最薄・判定9/25）。ナノはMER2.35へ復調・チェアも4個で復調（9/20の売上0円は単日ノイズと確定・監視解除）',
  '⚖️ **本日の判定2本=復活2本のPhase1・両方合格**: シェーバー CPA(個)2,138円/CTR2.25%✅（8,000継続確定）／歯ブラシ CPA(個)4,874円/CTR1.52%✅（9/21の4個が逆転打・次関門9/26の7日判定CPA≤4,000円）',
  '✅ 9/20広告費を確定上書き: 273,661→**274,436円**（+775円）。9/21分279,264円（予算比109%＝祝日上振れ）は暫定・明朝確定 ／ 📅 明日9/24から平日: **9/24-25の平日CVR3%台で外部要因説の確定クローズ**',
  '原価は日次のバリアント構成が取れないナノガラス/壁掛けディスペンサーのみ30日実測ミックスの加重平均単価【近似】。'
  '期間別サマリー（次シート）はバリアント別実数量の正確値'],
 ['日付','曜','実売','原価','広告費','利益','利益率','手数料後利益','MER','3日移動平均利益','ブレーキ','備考'],
 PROF, [12,5,13,12,12,13,9,14,8,16,9,10],
 {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'#,##0',9:'0.00',10:'#,##0'})

# ---------- 1 シンプル判定 ----------
def blk(n, N, K, A_):
    s = N.get(n, 0); k = K.get(n, 0); a = A_.get(n, 0); return s, k, a, s - k - a
SIMPLE = []
for n in sorted(R['N7'], key=lambda x: -R['N7'][x]):
    a7 = R['A7'].get(n, 0)
    if not a7: continue
    s7, k7, _, p7 = blk(n, R['N7'], R['K7'], R['A7'])
    s3, k3, a3, p3 = blk(n, R['N3'], R['K3'], R['A3']); s1, k1, a1, p1 = blk(n, R['N1'], R['K1'], R['A1'])
    gm = 1 - k7 / s7; be = 1 / gm; tg = 1 / (gm - 0.35) if gm - 0.35 > 0 else None; mer = s7 / a7
    cp = MAP.get(n, n); days = [d for d in D7 if d in BSNAP[cp]]
    wu = (a7 / sum(BSNAP[cp][d] for d in days)) if len(days) == 7 and sum(BSNAP[cp][d] for d in days) else None
    w3 = []
    for dd in (D3, D5, D7):
        sx, cx, ax = win(n, dd)
        w3.append((sx / ax if ax else None, 1 / (1 - cx / sx) if sx and sx > cx else None))
    below = all(m is not None and b is not None and m < b for m, b in w3)
    tight = all(m is not None and b is not None and m - b < 0.30 for m, b in w3)
    rich = all(m is not None and tg and m >= tg for m, _ in w3) and wu is not None and wu >= 0.95
    tri = '🚨3窓すべて分岐割れ→停止/−50%' if below else ('⚠️3窓すべて余裕<0.30→−25%' if tight else
          ('🚀3窓すべて目標超＋消化95%→+25%' if rich else '⏸窓が割れた→据え置き'))
    if p7 < 0 or mer < be: st = '🚨縮小・停止'
    elif (a3 and s3 / a3 < be) or mer < be + 0.30: st = '🔧改善'
    elif tg and mer >= tg and wu and wu >= 0.95: st = '🚀伸ばす候補'
    else: st = '✅維持'
    mm = mer * 0.7; per = mm * gm - 1
    ends = [mer * x * gm - 1 for x in (0.6, 0.7, 0.8)]
    rob = '一致' if (all(e > 0 for e in ends) or all(e < 0 for e in ends)) else '⚠️符号が割れる'
    SIMPLE.append([n, round(mer, 2), round(s3 / a3, 2) if a3 else '', round(s1 / a1, 2) if a1 else '',
        round(be, 2), round(tg, 2) if tg else '', round(p7), round(p3), round(p1),
        round(wu, 3) if wu else '', round(per, 3), rob, st, tri])
sh('シンプル判定', ['LOOTY 2026-09-22 定例（昨日=9/21 月・敬老の日）',
 '状態: 🚨縮小・停止=7日MER<分岐 or 7日利益マイナス ／ 🔧改善=3日MER<分岐 or 余裕<0.30 ／ 🚀伸ばす候補=7日MER≥目標かつ週消化率≥95% ／ ✅維持',
 '3窓判定（3日/5日/7日・すべて9/21終端）が本番の意思決定ルール。窓が1つでも割れたら据え置き＝動かさない',
 '「広告費1円あたり利益」= 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）。頑健性は×0.6/0.7/0.8 の3端で符号が変わらないかを見る'],
 ['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,9,9,9,8,8,12,12,12,10,12,13,14,30], {7:'#,##0',8:'#,##0',9:'#,##0',10:'0.0%'})

# ---------- 2 ネクストアクション ----------
NA = [
 ['✅ 本日判定①','携帯電動シェーバー Phase1 **合格**（8,000で継続確定・購入50件まで触らない）',
  '基準: クリーン3日(9/19-21) CTR≥1.5% かつ CPA(個)≤3,237円。実測: 11個・CPA(個)**2,138円**・CTR**2.25%**・3日利益+11,856円。'
  '「Bを外してA単独で再開」の読みどおり。復活成功の1本目',
  '—','クローズ'],
 ['✅ 本日判定②','UV歯ブラシ除菌器 Phase1 **合格**（9/21の4個が逆転打）',
  '基準: 同 CPA(個)≤5,740円。実測: 8個・CPA(個)**4,874円**・CTR1.52%（ギリギリ）・3日利益+6,932円。'
  '日次CPAは8,437→4,952→**3,053円**と3日連続改善。ただし**次関門=9/26の7日判定（CPA≤4,000円）**は現状未達圏＝秋衛生CRの準備は継続推奨',
  '—','クローズ'],
 ['🚀 祝日3連発','9/19〜21の3日利益 **+702,202円**（平均234,067円/日）・9/21は利益率36.6%で**北極星35%を初超え**',
  '増額組の初日: フック+51,722円・MER5.10（20,000でも効率維持）／ガラス+66,199円・MER3.93／インソール+24,244円・MER2.03（3本中で最も薄い・判定9/25）。'
  'CVRは2.98→3.13→**3.28%**と3日連続で切り上がり',
  '—','—'],
 ['👀 9/25判定 5本','増額3本＋サンダル10,000＋カタログ9,000（クリーン3日/7日・宣言済み基準）',
  'インソール36,000: ≥25,721円/日（初日24,244円=僅かに未達ペース）／ガラス32,000: ≥35,596円/日（初日66,199円=余裕）／'
  'フック20,000: ≥14,987円/日（初日51,722円=余裕）／サンダル10,000: ≥5,715円/日（初日1,334円=**未達圏**・未達なら8,000へ）／'
  'カタログ: 7日ROAS≥2.0（9/18-21消化37,701円）',
  '—','9/25朝'],
 ['📅 答え合わせ','明日9/24(木)から平日。**9/24-25の平日CVRが3.0%台なら外部要因で確定クローズ**',
  '連休中の実測: 2.98→3.13→3.28%と回復済み。本日9/23(水・秋分)まで週末扱い。楽天マラソンは9/24 01:59終了',
  '—','9/24-25'],
 ['🔴 明朝','9/21広告費 279,264円の確定再取得',
  '9/20は 273,661→**274,436円**（+775円）で確定・上書き済み',
  '—','明朝'],
 ['🟡 実行待ち','**カゴ落ちメール（最優先）**／Selleasy／購入後クーポン（Shopify Flow）／優先配送536円／GSCサイトマップ登録',
  'CJ確認待ち: フック・4-in-1の最新原価／インソール$0.82が全サイズ共通か。'
  '次の新弾候補: 癒しの指圧マット（Phase1基準 CTR≥1.5%かつCPA≤4,332円・出稿はユーザー判断）',
  '合計+20万円/月規模','実行待ち'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('前日 9/21(月祝)', R['N1'], R['K1'], R['ACCT1']), ('3日 9/19-21', R['N3'], R['K3'], R['ACCT3']),
        ('7日 9/15-21', R['N7'], R['K7'], R['ACCT7']), ('30日 8/23-9/21', R['N30'], R['K30'], R['ACCT30']),
        ('9月累積 9/01-21', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過: Σ商品gross=全店782,020 ／ Σ値引=30,049 ／ Σ広告費=アカウント279,264円（9/21・キャンペーン合算・差0円）',
 '✅ 9/20の広告費は再取得で確定済み（273,661円 → **274,436円**・+775円。9/22朝に上書き）',
 '⚠️ 9/21の広告費は 9/22 08時 の取得【暫定】。確定まで+0.1%程度動く → 明朝に再取得して確認する',
 '★ガラスクリーナー・ヘッドレストフックの原価は保守側の最高値バリアント単価で計上（フックは黒1,275だが1,344で計上＝利益は保守側）',
 '★9/21の返品はインソール1点（−3,980円）・優先配送1点（−790円）。★5e-2突合: 「広告費あり売上ゼロ」商品なし＝チェアは4個で復調・監視解除',
 '決済ブレンド率 **3.436%**（2026-09-01再計測。次回10/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(9/21 月祝) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','9/21(月祝)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '9/21(月・敬老の日)は実売751,971円・利益+275,077円（36.6%）で売上・利益とも9月最高日、利益率は北極星35%を初超え。本日の判定=復活2本のPhase1は両方合格（シェーバーCPA2,138円・歯ブラシ4,874円で9/21の4個が逆転打）。増額組の初日はフックMER5.10・ガラス3.93と快走、インソール2.03とサンダル1.64が薄め。CVRは連休3日で2.98→3.13→3.28%と切り上がり。次は9/24-25の平日CVR答え合わせと9/25の判定5本（増額3本+サンダル+カタログ）').font = Font(name='Arial', size=10, color='CC0000')

# ---------- 4 商品別 ----------
P = []
for n in sorted(R['N7'], key=lambda x: -R['N7'][x]):
    s7,k7,a7,p7 = blk(n,R['N7'],R['K7'],R['A7']); s1,k1,a1,p1 = blk(n,R['N1'],R['K1'],R['A1'])
    s3,k3,a3,p3 = blk(n,R['N3'],R['K3'],R['A3']); s30,k30,a30,p30 = blk(n,R['N30'],R['K30'],R['A30'])
    sc,kc,ac,pc = blk(n,R['NC'],R['KC'],R['AC'])
    gm = 1-k7/s7 if s7 else 0; mer = s7/a7 if a7 else None; be = 1/gm if gm else None
    tg = 1/(gm-0.35) if gm-0.35 > 0 else None; yo = (mer-be) if mer and be else None
    q7 = R['Q7'].get(n, 0); o = ORD.get(n); ipo = q7/o if o else None
    bcpa = (s7-k7)/q7*ipo if q7 and ipo else None; cpa = a7/o if o and a7 else None
    jud = ('📦広告なし' if not a7 else ('🚨赤字' if p7 < 0 else ('🔧テコ入れ' if yo is not None and yo < 0.30 else
           ('🚀増額候補' if tg and mer >= tg else '✅維持'))))
    P.append([n, '季節' if n in SEA else '通年', s7, k7, round(a7), round(p7), round(p7/s7,4) if s7 else '',
        round(mer,2) if mer else '—', round(be,2) if be else '—', round(tg,2) if tg else '—',
        round(yo,2) if yo is not None else '—', s1, round(p1), round(p1/s1,4) if s1 else '',
        round(p3), round(p30), round(pc), q7, o or '', round(ipo,2) if ipo else '',
        round(cpa) if cpa else '', round(bcpa) if bcpa else '', BUD.get(MAP.get(n,n), '—'), jud])
P.append(['カタログ全部（テスト）※全商品横断','—','—','—',round(R['CAT7'])]+['—']*18+[BUD.get('カタログ全部（テスト）','—'),'—'])
sh('商品別', ['商品別（7日 9/15-9/21 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化（差0円・w0921.pyでassert済み）',
  '当月累積利益は9月分（9/01-21・21日）',
  '★携帯電動シェーバー・UV歯ブラシ除菌器は9/18 12時に再開（稼働4日・**Phase1両方合格**）＝7日窓に休止期間を含む点は変わらず注意',
  '★ムダ毛・電動かっさ(9/18停止)の停止前消化が7日窓に残る（残り3日で抜ける）'],
 ['商品','区分','7日売上','7日原価','7日広告','7日利益','7日利益率','MER','分岐','目標','余裕','前日売上','前日利益','前日利益率',
  '3日利益','30日利益','当月累積利益','7日販売数','7日注文数','点数/注文','CPA(注文)','分岐CPA(注文)','現日予算','判定'],
 P, [26,6]+[12]*22, {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',12:'#,##0',13:'#,##0',14:'0.0%',
                     15:'#,##0',16:'#,##0',17:'#,##0',21:'#,##0',22:'#,##0',23:'#,##0'})

# ---------- 5 レバー一覧 ----------
LV = []
for n in sorted(R['N7'], key=lambda x: -R['N7'][x]):
    cp = MAP.get(n, n); b = BUD.get(cp)
    if not b: continue
    s7, k7, a7, p7 = blk(n, R['N7'], R['K7'], R['A7'])
    if not a7: continue
    gm = 1-k7/s7; mer = s7/a7; mm = mer*0.7
    days = [d for d in D7 if d in BSNAP[cp]]
    wu = (a7/sum(BSNAP[cp][d] for d in days)) if len(days) == 7 and sum(BSNAP[cp][d] for d in days) else None
    ends = [mer*x*gm-1 for x in (0.6, 0.7, 0.8)]
    LV.append([n, '季節' if n in SEA else '通年', b, round(wu,3) if wu else '', round(mer,2), round(1/gm,2),
        round(mer-1/gm,2), round(mm*gm-1,3), round(ends[0],3), round(ends[2],3),
        '一致' if (all(e>0 for e in ends) or all(e<0 for e in ends)) else '⚠️符号が割れる',
        round((1-mm*gm)*b*0.25*7), round((mm*gm-1)*b*0.25*7), round(p7)])
LV.sort(key=lambda x: -max(x[11], x[12]))
sh('レバー一覧', ['「どれを動かすと一番効くか」は7日平均の利益額ではなく、動かしたときの変化量で並べる',
  '削減1円あたりの利益変化 = 1 − 限界MER×粗利率 ／ 増額1円あたり = 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）',
  '★頑健性: ×0.6 と ×0.8 の両端で符号が変わらないものだけ動かしてよい。割れたら据え置き',
  '増額は週消化率95%以上のものだけが対象（それ未満は増やしても使われない）'],
 ['商品','区分','日予算','週消化率','MER','分岐','余裕','1円あたり利益(×0.7)','×0.6端','×0.8端','頑健性','−25%で週','+25%で週','7日利益'],
 LV, [26,6,11,10,8,8,8,15,10,10,13,12,12,12], {3:'#,##0',4:'0.0%',12:'#,##0',13:'#,##0',14:'#,##0'})

# ---------- 6 週次診断 ----------
def wblk(days, names=None):
    s = c = 0
    for n, v in Sd.items():
        if names is not None and n not in names: continue
        g = sum(v[d][0] for d in days if d in v); dc = sum(v[d][1] for d in days if d in v)
        if not g: continue
        s += g-dc
        if n in PRICEa and n in COSTa: c += g/PRICEa[n]*COSTa[n]
    a = sum(ADd[MAP.get(n, n)].get(d, 0) for n in (names if names is not None else Sd) for d in days) if names is not None \
        else sum(ADd[cp].get(d, 0) for cp in ADd for d in days)
    return s, c, a, s-c-a
YR = {n for n in Sd if n and n not in SEA}
end = datetime.date(2026, 9, 6); WK = []
for i in range(6):
    a = end - datetime.timedelta(days=7*i+6)
    WK.append((f"{a.strftime('%m/%d')}-{(a+datetime.timedelta(days=6)).strftime('%m/%d')}",
               [(a+datetime.timedelta(days=j)).isoformat() for j in range(7)]))
WK.reverse()
WD_ = []
for lbl, days in WK:
    if days[0] < '2026-06-29': continue
    s, c, a, p = wblk(days); ss, _, sa, sp = wblk(days, SEA); ys, _, ya, yp = wblk(days, YR)
    WD_.append([lbl, round(s), round(c), round(a), round(p), round(p/s,4), round(s/a,2), round(c/s,4), round(a/s,4),
                round(sp), round(ss/sa,2) if sa else '', round(yp), round(ys/ya,2) if ya else ''])
sh('週次診断', ['全店の週次分解（完全週のみ・最新は8/31-9/6週）。9/7-8は進行中週のため未集計。原価はナノガラス/ディスペンサーのみ加重平均単価【近似】',
  '★夏物の崩壊が8月前半の正体。壊れたのは季節物だけで、通年物へ入れ替えて回復した',
  '★9月は日予算240,000〜253,000で運転。9/9リバランスで253,000へ。日予算590,000だった7月とは水準が違うので利益額の絶対比較はしない',
  '★8/31-9/6週は楽天スーパーセール(9/4夜〜)と重なる。翌週(9/7-13)との比較でセール影響を切り分ける'],
 ['週','実売','原価','広告費','利益','利益率','MER','原価率','広告費率','季節物 利益','季節物MER','通年物 利益','通年物MER'],
 WD_, [14,13,12,12,12,9,8,9,10,15,11,15,11],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'0.00',8:'0.0%',9:'0.0%',10:'#,##0',11:'0.00',12:'#,##0',13:'0.00'})

# ---------- 7 ファネル（30日・RPM/CPM つき）----------
for _k, _v in MF_RAW.items():
    _c = sum(ADd[_k].get(d, 0) for d in D30)
    assert abs(_c - _v[0]) <= max(50, _v[0] * 0.0005), (_k, _c, _v[0])
FN = []
for n, (c, imp, clk) in MF.items():
    s = R['N30'].get(n, 0); k = R['K30'].get(n, 0); q = R['Q30'].get(n, 0); o = ORD30.get(n, 0)
    if not s or not o or not clk: continue
    ipo = q/o; bcpa = (s-k)/q*ipo; cpm = c/imp*1000
    ctr = clk/imp; cvr = o/clk; gpo = (s-k)/o
    need = cpm/(gpo*1000)
    FN.append([n, '季節' if n in SEA else '通年', imp, round(ctr,4), clk, round(cvr,4), round(s/clk),
               round(c/clk), round(c/o), round(bcpa), round(bcpa-c/o), round(cpm), round(gpo),
               round(ctr*cvr*10000, 2), round(need*10000, 2), round((ctr*cvr)/need, 2)])
mc = statistics.median([x[5] for x in FN]) if FN else 0; mr = statistics.median([x[6] for x in FN]) if FN else 0
FN.sort(key=lambda x: -x[15])
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(8/23-9/21)」。他シートの7日窓と混ぜて読まないこと',
  'クリックは **アウトバウンドクリック**（data_query 実測・Asia/Tokyo）',
  '✅ 検算: 全キャンペーンで data_query の消化 = CSV(8/23-9/21) が許容差以内で一致（コード内assert）',
  'CVR = Shopify注文 ÷ Meta全クリック（Metaの購入数は損益に使わない）',
  f'中央値 CVR {mc*100:.2f}% ／ 売上perクリック {mr:.0f}円',
  '★RPM/CPM = CTR×CVR×粗利/注文 ÷ CPM。1.0未満が赤字圏。★CTR単独では成否を判別できない（実測で反証済み）',
  '★必要CTR×CVR(‱) = CPM ÷ (粗利/注文 × 1000)。この列を下回っている商品が赤字'],
 ['商品','区分','インプ','CTR','クリック','CVR','売上/クリック','CPC','CPA(注文)','分岐CPA(注文)','余裕','CPM','粗利/注文',
  '実測CTR×CVR(‱)','必要CTR×CVR(‱)','RPM/CPM'],
 FN, [26,6,12,9,11,9,13,9,12,15,11,10,11,15,15,10],
 {3:'#,##0',4:'0.00%',5:'#,##0',6:'0.00%',7:'#,##0',8:'#,##0',9:'#,##0',10:'#,##0',11:'#,##0',12:'#,##0',13:'#,##0'})

# ---------- 8 日次推移 ----------
WDJ = ['月','火','水','木','金','土','日']
pr = {}
for d in ALLD:
    s = c = 0
    for n, v in Sd.items():
        if n == '' or d not in v: continue
        g, dc = v[d]; s += g-dc
        if g and n in PRICEa and n in COSTa: c += g/PRICEa[n]*COSTa[n]
    a = sum(ADd[cp].get(d, 0) for cp in ADd); pr[d] = (s, c, a, s-c-a)
DD = []
for j, d in enumerate(ALLD):
    if d < '2026-07-13': continue
    s, c, a, p = pr[d]; ma = sum(pr[x][3] for x in ALLD[j-2:j+1])/3
    DD.append([d, WDJ[datetime.date.fromisoformat(d).weekday()], round(s), round(c), round(a), round(p),
               round(p/s,4), round(s/a,2), round(ma), '⚠️非常ブレーキ' if ma < 130000 else ''])
sh('日次推移', ['日次の利益は上記【近似】原価ベース。4期間サマリーはバリアント別実数量の正確値',
  '非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（現況234,067円=大幅余裕。100,000円への再校正提案は残置）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['9/22 判定','携帯電動シェーバー Phase1（クリーン3日 9/19-21）','CTR≥1.5% かつ CPA(個)≤3,237円',
  '11個・CPA(個)**2,138円**・CTR**2.25%**・3日利益+11,856円','✅ **合格 → 8,000で継続確定**','購入50件まで予算・CRを触らない'],
 ['9/22 判定','UV歯ブラシ除菌器 Phase1（クリーン3日 9/19-21）','CTR≥1.5% かつ CPA(個)≤5,740円',
  '8個・CPA(個)**4,874円**・CTR1.52%・日次CPAは3日連続改善','✅ **合格**','次関門: 9/26の7日判定 CPA≤4,000円（現状未達圏）'],
 ['9/25','快適マジックインソール 36,000（クリーン3日 9/22-24）','3日平均利益 ≥25,721円/日（変更前7日実測）',
  '初日9/21: +24,244円・MER2.03','待機（僅かに未達ペース）','未達なら32,000へ'],
 ['9/25','伸縮ガラスクリーナー 32,000（クリーン3日 9/22-24）','3日平均利益 ≥35,596円/日',
  '初日9/21: +66,199円・MER3.93','待機（余裕）','未達なら27,000へ。新原価988円ベース'],
 ['9/25','高見えレザーヘッドレストフック 20,000（クリーン3日 9/22-24）','3日平均利益 ≥14,987円/日',
  '初日9/21: +51,722円・MER5.10','待機（余裕）','未達なら15,000へ'],
 ['9/25','もちふわ肉球サンダル 10,000（クリーン3日 9/22-24）','3日平均利益 ≥5,715円/日',
  '初日9/21: +1,334円・MER1.64','待機（**未達圏**）','未達なら8,000へ'],
 ['9/25','カタログ 9,000（クリーン7日 9/18-24）','Meta-ROAS ≥2.0で継続／未達なら停止',
  '9/18-21消化 37,701円','待機',''],
 ['9/24-25','連休・セール要因の答え合わせ','平日の全店CVRが3.0%台へ回復すれば外部要因で確定・クローズ',
  '連休中 2.98→3.13→**3.28%**と回復済み','待機（好サイン）','回復しなければLP側テコ入れ検討'],
 ['10/1','決済手数料の月次再計測','直近100注文のpaymentGatewayNames×金額で実効ブレンド率を更新','前回9/1: 3.436%','待機',''],
 ['10/7','購入後クーポン（LOOTY500）の判定','30日リピート率 >6.38%で継続','Shopify Flow設定はユーザー実行待ち','待機',''],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日の判定2本: **復活2本のPhase1・両方✅合格**（シェーバー8,000継続確定／歯ブラシは9/26の7日判定CPA≤4,000円が次関門）',
  '★次: 9/24-25 平日CVR答え合わせ → **9/25朝 判定5本**（増額3本+サンダル+カタログ） → 9/26朝 歯ブラシ7日判定 → 10/1 手数料再計測',
  '★倍率の定義: **MER ÷ 分岐MER**。1.0未満＝赤字',
  '★9/19-21の3日利益 +702,202円（平均234,067円/日）＝9月最高水準。祝日3連発をフルに獲った'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-09-21c': PREVB[r[1]] += int(r[3])
BR, inc, dec = [], 0, 0
for cp in sorted(BUD, key=lambda c: -BUD[c]):
    p, nn = PREVB.get(cp, 0), BUD[cp]
    n = INV.get(cp, cp)
    s7 = R['N7'].get(n, 0); k7 = R['K7'].get(n, 0); a7 = R['A7'].get(n, 0)
    s3 = R['N3'].get(n, 0); k3 = R['K3'].get(n, 0); a3 = R['A3'].get(n, 0)
    q7 = R['Q7'].get(n, 0); q3 = R['Q3'].get(n, 0)
    gm = 1 - k7/s7 if s7 else None
    mer = s7/a7 if s7 and a7 else None; be = 1/gm if gm else None
    tg = 1/(gm-0.35) if gm and gm-0.35 > 0 else None
    m3 = s3/a3 if s3 and a3 else None; b3_ = 1/(1-k3/s3) if s3 else None
    r7 = ((s7-k7)/q7)/(a7/q7) if q7 and a7 else None
    r3 = ((s3-k3)/q3)/(a3/q3) if q3 and a3 else None
    dd = [d for d in D7 if BSNAP[cp].get(d)]
    w = (sum(ADd[cp].get(d, 0) for d in dd) / sum(BSNAP[cp][d] for d in dd)) if dd else None
    per = (mer*0.7*gm - 1) if mer and gm else None
    e6 = (mer*0.6*gm - 1) if mer and gm else None
    e8 = (mer*0.8*gm - 1) if mer and gm else None
    if nn > p: inc += nn - p
    elif nn < p: dec += p - nn
    BR.append([n if n != cp else cp, p, nn, nn-p, (nn/p-1) if p else '',
        round(mer, 2) if mer else '—', round(be, 2) if be else '—', round(tg, 2) if tg else '—',
        round(mer-be, 2) if mer and be else '—', round(m3, 2) if m3 else '—',
        round(m3-b3_, 2) if m3 and b3_ else '—', round(r7, 2) if r7 else '—', round(r3, 2) if r3 else '—',
        round(w, 3) if w else '—', round(per, 3) if per is not None else '—',
        ('一致' if (e6 and e8 and ((e6 > 0 and e8 > 0) or (e6 < 0 and e8 < 0))) else '⚠️符号が割れる') if per is not None else '—',
        '★変更' if p != nn else ''])
BR.sort(key=lambda x: (x[16] == '', -abs(x[3]), -x[2]))
sh('予算見直しチェック', ['前日(9/21c=リバランス後)スナップショット → 本日(9/22)',
  '合計 256,000 → **256,000円/日**。9/21c（増額3本+サンダル10,000）から変更なし',
  '★体制: 12セット・256,000円/日。9/22-24は増額3本+サンダル10,000のクリーン測定期間（判定9/25朝）',
  '★9/21の消化は 279,264円＝予算256,000円の**109%**（祝日上振れ・Meta仕様）。ガラスは107%・フックは119%消化＝増額が即満額で回った',
  '⚠️ 9/25朝の判定5本まで追加の予算変更を入れない（判定窓は連休明けの平日を含む＝需要の切り替わりに注意して執行）'],
 ['商品/キャンペーン','変更前','変更後','差','変化率','7日MER','分岐','目標','7日余裕','3日MER','3日余裕',
  '倍率7日','倍率3日','消化率(7日)','1円あたり利益','頑健性','印'],
 BR, [26,10,10,9,9,8,7,7,9,8,9,9,9,12,13,14,7],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'+0.0%;-0.0%',14:'0.0%'})

# ---------- 10 CVR推移 ----------
SES = {'2026-08-04':6639,'2026-08-05':5425,'2026-08-06':5138,'2026-08-07':4827,'2026-08-08':5527,'2026-08-09':5886,
'2026-08-10':5245,'2026-08-11':6001,'2026-08-12':4900,'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,
'2026-08-16':5349,'2026-08-17':3438,'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,
'2026-08-22':3220,'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733,'2026-08-27':3145,
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936,'2026-09-02':3142,'2026-09-03':3340,'2026-09-04':3293,'2026-09-05':3217,'2026-09-06':3752,'2026-09-07':2787,'2026-09-08':2739,'2026-09-09':2801,'2026-09-10':3514,'2026-09-11':3014,'2026-09-12':3132,'2026-09-13':4246,'2026-09-14':3592,'2026-09-15':3358,'2026-09-16':3348,'2026-09-17':3418,'2026-09-18':3583,'2026-09-19':4088,'2026-09-20':4310,'2026-09-21':4571}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88,'2026-09-02':92,'2026-09-03':103,'2026-09-04':74,'2026-09-05':106,'2026-09-06':122,'2026-09-07':96,'2026-09-08':95,'2026-09-09':98,'2026-09-10':116,'2026-09-11':96,'2026-09-12':117,'2026-09-13':140,'2026-09-14':102,'2026-09-15':103,'2026-09-16':99,'2026-09-17':100,'2026-09-18':96,'2026-09-19':122,'2026-09-20':135,'2026-09-21':150}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       ('★昨日（敬老の日・CVR 3.28%・9月最高利益日）' if d == '2026-09-21' else '（日曜・CVR 3.13%）' if d == '2026-09-20' else '（マラソン初日・CVR 2.98%）' if d == '2026-09-19' else '' if d in ('2026-09-14','2026-09-15','2026-09-16','2026-09-17','2026-09-18') else '（セッション4,246・注文140＝9月最多）' if d == '2026-09-13' else '（CVR 3.74%・9月最高）' if d == '2026-09-12'
        else '（−2σトリガー発動日）' if d == '2026-09-04' else '')] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★9/21は セッション4,571・注文150件 = **CVR 3.28%**＝3日連続の切り上がり（2.98→3.13→3.28）。9月のCVR上位日',
  '★チェックアウト完了率: 9/20 52.0% → 9/21 **56.4%**（141/250）＝9月上位。カゴ投入率 5.84%（267/4,571）も上振れ',
  '★点数/注文 1.267（190点/150注文）。値引30,049円＝フックのペア買い多発（値引14,129円）。セット購入が戻っている',
  '★セッション2,700〜3,800/日 は日予算240,000〜253,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(8/23-9/21)。売上=gross−値引。祝日除外に9/21-23を追加済み・次回定期更新9/28(月)',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  '★9/21(月祝)は実売751,971円で9月最高。祝日のため月曜平均には算入しない（HOLに9/21-23を追加）。本日9/23(水・秋分)まで週末扱い'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])

wb.save('data/reports/report-2026-09-22.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 8月確定 {aup:,.0f}円")
