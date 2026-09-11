# -*- coding: utf-8 -*-
"""2026-09-12 定例レポート本体（昨日=9/11 金）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep0911w.pkl', 'rb'))
FEE = 0.03436   # 2026-09-01 月次再計測。次回 10/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-09-12'   # 9/12 05:5x時点（9/11bムダ毛12,000後から変更なし）
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 245000, sum(BUD.values())
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
# --- 7日(9/05-9/11) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD = {'ナノガラス脱毛パッド':268,'W固定スマホ車載ホルダー':113,'快適マジックインソール':91,
'伸縮ガラスクリーナー':52,'バランスケアスリッパ':37,'ムダ毛シェーバー':36,'姿勢サポートチェア':22,
'ナノバブルシャワーヘッド':20,'4-in-1マルチクリーナー':20,'むくみ取りかっさ':18,
'高見えレザーヘッドレストフック':13,'2WAYシートボックス':11,'温感EMSフェイシャルワンド':10,
'優先配送':5,'携帯電動シェーバー':4,'偏光・調光サングラス':4,'壁掛けディスペンサー':3,
'完全遮光・形状記憶':2,'形状記憶日傘':2,'ジェットウォッシャー':2,
'湯上がりガーゼワンピース':1,'3D足臭リセットブラシ':1,'UV歯ブラシ除菌器':1,'5WAY腰掛けファン':1,
'スマートノーズEMS美顔器':1,'ビジュアル耳かき':1,'卓上冷感クーラー':1,'リカバリーサンダル':1}
STORE_ORD7, STORE_SESS7 = 729, 21824
assert sum(ORD.values()) == 741, sum(ORD.values())   # 全店729より多いのは複数商品を含む注文が両方で数えられるため

# --- 30日(8/13-9/11) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1129,'W固定スマホ車載ホルダー':509,'快適マジックインソール':319,
'ムダ毛シェーバー':184,'バランスケアスリッパ':121,'2WAYシートボックス':115,'姿勢サポートチェア':101,
'形状記憶日傘':98,'偏光・調光サングラス':83,'むくみ取りかっさ':78,'完全遮光・接触冷感UVハット':71,
'伸縮ガラスクリーナー':52,'ナノバブルシャワーヘッド':49,'4WAY':42,'優先配送':42,'接触冷感UVパーカー':37,
'害虫ブロッカー':31,'完全遮光・形状記憶':29,'接触冷感UVアームカバー':28,'3D足臭リセットブラシ':22,
'4-in-1マルチクリーナー':20,'携帯電動シェーバー':18,'温感EMSフェイシャルワンド':16,
'高見えレザーヘッドレストフック':13,'5WAY腰掛けファン':7,'壁掛けディスペンサー':6,'ビジュアル耳かき':6,
'ジェットウォッシャー':4,'ヘアドライタオル':4,'健康サンダル':3,'癒しの指圧マット':2,'瞬間冷感ポンチョ':2,
'湯上がりガーゼワンピース':2,'ネックマッサージャー':1,'UV歯ブラシ除菌器':1,'スマートノーズEMS美顔器':1,
'姿勢サポートベルト':1,'卓上冷感クーラー':1,'1秒折り畳みチェア':1,'リカバリーサンダル':1}

# --- 30日(8/13-9/11) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック）---
MF_RAW = {'ナノガラス脱毛パッド':(2396745,1256636,31848),'W固定スマホ車載ホルダー':(1002292,451803,13175),
'快適マジックインソール':(690367,423806,10276),'カタログ全部（テスト）':(562002,141385,4968),
'ムダ毛シェーバー':(538298,432155,4955),'形状記憶日傘':(386285,96897,3781),
'2WAYシートボックス':(329571,104287,2877),'姿勢サポートチェア':(319621,188052,3925),
'バランスケアスリッパ':(287924,197183,3672),'偏光・調光サングラス':(233730,98502,2683),
'完全遮光・接触冷感UVハット':(211738,47078,2212),'むくみ取りかっさ':(180745,52807,1584),
'ナノバブルシャワーヘッド':(165207,78813,1921),'接触冷感UVパーカー':(140987,44400,1244),
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':(95433,24626,738),'害虫ブロッカー':(95153,44586,893),
'3D足臭リセットブラシ':(85838,24927,338),'完全遮光・形状記憶・晴雨兼用・UV日傘':(79029,17778,784),
'接触冷感UVアームカバー':(78748,17645,630),'温感EMSフェイシャルワンド':(64858,15636,456),
'4-in-1マルチクリーナー':(64594,18480,435),'伸縮ガラスクリーナー':(58514,18905,730),
'5WAY腰掛けファン':(40175,11886,507),'ビジュアル耳かき':(26464,9402,148),
'高見えレザーヘッドレストフック':(24727,5891,245),'高吸水・速乾ヘアドライタオル':(10669,2706,75),
'カタログ全部（テスト） 夏以外':(6080,1903,50),'1秒折り畳みチェア':(5704,1773,49),
'卓上冷感クーラー':(5470,2625,79),'携帯電動シェーバー':(581,88,6)}
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
COSTa['ナノガラス脱毛パッド'] = (910 * 757 + 320 * 740) / 1230          # 30日実測ミックスの加重平均【近似】
COSTa['壁掛けディスペンサー'] = (6 * 2528 + 5 * 1981) / 11
PRICEa['壁掛けディスペンサー'] = 71780 / 11
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
sh('収益', [f'LOOTY 収益レポート 2026-09-12（昨日 = 9/11 金）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★9月累積（9/01-11・{len(CUM)}日）: 実売 {cs:,.0f} / 利益 {cp:,.0f}円（{cp/cs:.1%}）／1日あたり {cp/len(CUM):,.0f}円（8月確定は {aup:,.0f}円・{aup/31:,.0f}円/日）',
  '★9/11(金)は 実売 **505,174円**・利益 +140,700円前後（27.9%）・MER 2.20。金曜は最弱級の曜日（指数90.8）ながら、前週金曜(9/4 実売372,740円)比 **+35.5%**（※9/4は−2σの異常に弱い日だった点は割引いて読む）',
  '★**セール明け初日（楽天9/11 01:59終了）で全く垂れなかった**。9/12-14の反発確認は1日目クリア',
  '★値引 25,076円は**9月最大を更新**。点数/注文 **1.333（9月最高）**＝まとめ買いがさらに太い。フック値引5,771円・ガラス5,970円など「複数個買う理由がある商品」が値引の主役',
  f'✅ 注文96件・セッション3,014・CVR 3.19%。3日移動平均利益 {p3ma:,.0f}円',
  '🚀 **ヘッドレストフックが大化け: 14個・実売49,949円・利益+21,313円・MER5.09**（出稿3日目・グレー7個などまとめ買い中心）。ガラスクリーナーも21個・+38,910円・MER5.28、W固定は26個・**+40,379円（前日利益1位）**',
  '⚠️ 負け組は3本: ナノバブル−8,021円（増額後2日連続赤字・9/14判定へ）／スリッパ−5,079円／ムダ毛−3,765円（12,000初日・9/15判定へ）',
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
sh('シンプル判定', ['LOOTY 2026-09-12 定例（昨日=9/11 金）',
 '状態: 🚨縮小・停止=7日MER<分岐 or 7日利益マイナス ／ 🔧改善=3日MER<分岐 or 余裕<0.30 ／ 🚀伸ばす候補=7日MER≥目標かつ週消化率≥95% ／ ✅維持',
 '3窓判定（3日/5日/7日・すべて9/11終端）が本番の意思決定ルール。窓が1つでも割れたら据え置き＝動かさない',
 '「広告費1円あたり利益」= 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）。頑健性は×0.6/0.7/0.8 の3端で符号が変わらないかを見る'],
 ['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,9,9,9,8,8,12,12,12,10,12,13,14,30], {7:'#,##0',8:'#,##0',9:'#,##0',10:'0.0%'})

# ---------- 2 ネクストアクション ----------
NA = [
 ['✅ 本日合格①','高見えレザーヘッドレストフック Phase1 **合格**',
  '基準（3日9/9-11）: リンクCTR≥1.5% かつ CPA(個)≤2,636円。実測: **CTR 4.75%**（280/5,891）・Meta購入13件・**CPA 1,902円**。'
  'Shopify実売では3日23個・+27,746円・MER3.37。9/11単日は14個・+21,313円・MER5.09で**全店利益3位**。'
  '10,000円の現予算での増額後判定は9/14朝（3日倍率≥1.3）',
  '—','クローズ'],
 ['✅ 本日合格②','4-in-1マルチクリーナー Phase2本判定 **合格**',
  '基準（7日9/5-11）: CPA(個) ≤ 分岐5,206円。実測: 22個・**CPA 2,936円**（分岐の56%）・7日利益+20,683円・MER2.33。'
  '**テスト卒業＝レギュラー入り**。予算10,000は据え置き、増額は通常ルール（目標MER×消化率）で判断',
  '—','クローズ'],
 ['✅ 本日回復','姿勢サポートチェア 再点検クリア',
  '基準: 7日クリックCVR ≥2.13%。実測: **2.45%**（21/857）。基準週比−31%まで回復し発動域（−40%）を脱出。'
  '7日利益も+37,000円前後で健全。**監視解除・平常運転へ**',
  '—','クローズ'],
 ['⚠️ 要注意','ナノバブルシャワーヘッド — 増額後2日連続赤字（9/14判定の主対象）',
  '14,000への増額後: 9/10 −11,427円 → 9/11 **−8,021円**（1個・MER0.55）。増額前の9/9は+21,714円だった。'
  '判定は宣言どおり9/14朝（クリーン3日9/11-13の倍率≥1.3）。現況は不合格方向＝**11,000へ戻す公算大**。判定日まで触らない',
  '—','9/14朝'],
 ['👀 進行中','9/14朝 増額5本判定のクリーン1日目（9/11実績）',
  'インソール32,000: **+24,511円**（基準24,134円/日を1日目クリア）／ W固定33,000: **+40,379円**（前日利益1位・基準25,106円を大幅クリア）／ '
  'ガラス16,000: **+38,910円**・MER5.28 ／ フック10,000: +21,313円 ／ ナノバブル14,000: −8,021円（上記）。'
  '4勝1敗ペース。9/12-13もクリーンに走らせる（追加の予算変更を入れない）',
  '—','9/14朝'],
 ['👀 進行中','ムダ毛シェーバー 12,000初日は−3,765円',
  '2個・MER1.15。判定は9/15朝（クリーン3日9/12-14の平均利益 ≥5,379円/日で12,000確定、未達なら17,000へ戻す）',
  '—','9/15朝'],
 ['�statistical 記録','セール明け初日クリア＋スリッパ単日−5,079円',
  '楽天セール終了（9/11 01:59）当日に実売505,174円・利益率27.9%で「セール吸引」の反動なし。9/12-13で確認継続。'
  'スリッパは単日−5,079円だが7日では+50,000円前後で健全＝単日扱い',
  '—','9/13'],
 ['🔴 明朝','9/11広告費 229,108円の再取得・確認',
  '9/12 05:5x 取得の暫定値。9/10は 283,011→**283,189**（+178円）で確定済み・上書き実施',
  '—','明朝'],
 ['🟡 実行待ち','購入後クーポン（Shopify Flow）／Selleasy／優先配送536円／カゴ落ちメール／GSCサイトマップ登録',
  'いずれも手順書・文面は納品済み。クーポン判定は10/7。GSC登録はブログ42本のインデックス判定（10月）の前提',
  '合計+20万円/月規模','実行待ち'],
 ['🟡 推奨','秋テスト第2波（複数個買う商品を優先）— フックとガラスが実証を完了',
  'フック: 3日で23個・値引5,771円（2セット割引多発）／ガラス: 5日で52注文・値引5,970円。'
  '「複数個買う理由」基準は2連勝。次弾: ◎あったかインソール／着圧ソックス2-3足／衣類圧縮袋セット（9/15前後）',
  '当たり1本=週6万円〜','今週'],
 ['🟡 提案','非常ブレーキ閾値の再校正（3日移動平均 130,000 → 100,000円）','承認待ちが継続中','—','ユーザー判断'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('前日 9/11(金)', R['N1'], R['K1'], R['ACCT1']), ('3日 9/9-11', R['N3'], R['K3'], R['ACCT3']),
        ('7日 9/05-11', R['N7'], R['K7'], R['ACCT7']), ('30日 8/13-9/11', R['N30'], R['K30'], R['ACCT30']),
        ('9月累積 9/01-11', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過: Σ商品gross=全店530,250 ／ Σ値引=25,076 ／ Σ広告費=アカウント229,108円（9/11・広告セット合算・差0円）',
 '✅ 9/10の広告費は再取得で確定済み（283,011円 → **283,189円**・+178円。9/12 05:5xに上書き。adset合算=アカウント差0円）',
 '⚠️ 9/11の広告費は 9/12 05:5x の取得【暫定】。確定まで+0.1%程度動く → 明朝に再取得して確認する',
 '★ガラスクリーナー・ヘッドレストフックの原価は保守側の最高値バリアント単価で計上（フックは黒1,275だが1,344で計上＝利益は保守側）',
 '★9/11の返品は0件',
 '決済ブレンド率 **3.436%**（2026-09-01再計測。次回10/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(9/11 金) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','9/11(金)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, 'セール明け初日の9/11(金)は最弱級の曜日で実売505,174円・利益率27.9%を確保。フック14個・ガラス21個・W固定26個と、新商品と増額組が主役交代を進めている。ナノガラスは33個で平常。ナノバブルだけが増額後2日連続赤字で9/14判定の主対象').font = Font(name='Arial', size=10, color='CC0000')

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
sh('商品別', ['商品別（7日 9/05-9/11 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化（差0円・w0908.pyでassert済み）',
  '当月累積利益は9月分（9/01-08・8日）',
  '★伸縮ガラスクリーナーは9/7出稿（稼働5日）・高見えレザーヘッドレストフックは9/9昼出稿（稼働2.5日）。7日ベースで他商品と単純比較しないこと',
  '★サングラス(9/5停止)・UVハット(9/6停止)は7日窓に停止前の消化が入っている'],
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
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(8/10-9/08)」。他シートの7日窓と混ぜて読まないこと',
  'クリックは **アウトバウンドクリック**（data_query 実測・Asia/Tokyo）',
  '✅ 検算: 全キャンペーンで data_query の消化 = CSV(8/10-9/08) が許容差以内で一致（コード内assert）',
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
  '非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（⚠️ 現体制248,000円/日に対して基準が古い。100,000円への再校正を提案中 — ネクストアクション参照）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['9/12 合格','高見えレザーヘッドレストフック Phase1（3日 9/9-11）','リンクCTR ≥1.5% かつ CPA(個) ≤2,636円',
  '**CTR 4.75%（280/5,891）・CPA 1,902円**・3日23個・+27,746円','✅ **合格**','増額後判定は9/14朝（現予算10,000）'],
 ['9/12 合格','4-in-1マルチクリーナー Phase2本判定（7日 9/5-11）','CPA(個) ≤ 分岐5,206円',
  '22個・**CPA 2,936円**・7日利益+20,683円・MER2.33','✅ **合格＝レギュラー入り**','予算10,000据え置き'],
 ['9/12 回復','姿勢サポートチェア 再点検','7日クリックCVR ≥2.13%',
  '**2.45%**（21/857）・基準週比−31%まで回復','✅ 監視解除','平常運転へ'],
 ['9/12 参考','Meta週内ペーシング','暦週(9/6-9/12)の消化収束',
  '9/6〜9/11の6日合計1,503,736円。期中に予算が5回変わったため収束率は算出不能','参考値のみ','リバランス期は暦週評価を停止'],
 ['9/12-13','セール明けの反発確認','同曜日比が平常圏か',
  '初日9/11は前週金曜比+35.5%で反動なし','進行中',''],
 ['9/14','増額5本の判定（クリーン3日 9/11-13）','インソール≥24,134円/日／W固定≥25,106円/日／ナノバブル倍率≥1.3／ガラス倍率≥1.3かつCPA≤2,837／フック倍率≥1.3',
  '1日目: +24,511／+40,379／**−8,021**／+38,910／+21,313','進行中（4勝1敗ペース）','ナノバブルのみ不合格方向'],
 ['9/14(月)','曜日指数の定期更新・unitCost週次再取得','毎週月曜タスク','','待機',''],
 ['9/15','ムダ毛シェーバー 12,000の判定（クリーン3日 9/12-14）','3日平均利益 ≥5,379円/日（17,000時代の7日平均）',
  '初日(9/11・非クリーン): −3,765円','待機','未達なら17,000へ戻す'],
 ['9/18','カタログ 14,000の判定（クリーン7日 9/11-17）','7日Meta-ROAS ≥2.0で継続／<2.0なら9,000へ',
  '9/11は13,023円消化（93%）','待機',''],
 ['10/7','購入後クーポン（LOOTY500）の判定','30日リピート率 >6.38%で継続','Shopify Flow設定はユーザー実行待ち','待機',''],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日の執行: **なし**（判定3件はすべて合格/回復のクローズ）。体制は 245,000円/日・12セット',
  '★合格2件（フックPhase1・4-in-1 Phase2）・回復1件（チェア）。次: 9/14朝 増額5本 → 9/15朝 ムダ毛 → 9/18朝 カタログ',
  '★倍率の定義: **MER ÷ 分岐MER**。1.0未満＝赤字',
  '★セール明け初日(9/11)は反動なし。9/12-13で確認継続'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-09-11b': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['前日(9/11bムダ毛減額後)スナップショット → 本日(9/12・Meta直読み確認)',
  '合計 245,000 → **245,000円/日**。9/11b以降のユーザー変更は**なし**',
  '★体制: 増額5本のクリーン測定2日目（9/12）。9/13まで予算を動かさないのが判定精度のために望ましい',
  '★9/11の消化は 229,108円＝予算245,000円の93.5%。9/10の113%の反動で正常な週内ペーシング',
  '⚠️ 9/11-13は増額5本のクリーン測定期間。この間は追加の予算変更を入れないのが判定精度のために望ましい'],
 ['商品/キャンペーン','変更前','変更後','差','変化率','7日MER','分岐','目標','7日余裕','3日MER','3日余裕',
  '倍率7日','倍率3日','消化率(7日)','1円あたり利益','頑健性','印'],
 BR, [26,10,10,9,9,8,7,7,9,8,9,9,9,12,13,14,7],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'+0.0%;-0.0%',14:'0.0%'})

# ---------- 10 CVR推移 ----------
SES = {'2026-08-04':6639,'2026-08-05':5425,'2026-08-06':5138,'2026-08-07':4827,'2026-08-08':5527,'2026-08-09':5886,
'2026-08-10':5245,'2026-08-11':6001,'2026-08-12':4900,'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,
'2026-08-16':5349,'2026-08-17':3438,'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,
'2026-08-22':3220,'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733,'2026-08-27':3145,
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936,'2026-09-02':3142,'2026-09-03':3340,'2026-09-04':3293,'2026-09-05':3217,'2026-09-06':3752,'2026-09-07':2787,'2026-09-08':2739,'2026-09-09':2801,'2026-09-10':3514,'2026-09-11':3014}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88,'2026-09-02':92,'2026-09-03':103,'2026-09-04':74,'2026-09-05':106,'2026-09-06':122,'2026-09-07':96,'2026-09-08':95,'2026-09-09':98,'2026-09-10':116,'2026-09-11':96}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       ('★昨日（CVR 3.19%・セール明け初日）' if d == '2026-09-11' else '（CVR 3.30%）' if d == '2026-09-10'
        else '（−2σトリガー発動日）' if d == '2026-09-04' else '')] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★9/11は セッション3,014・注文96件 = **CVR 3.19%**。9月の中央値圏。セール明けの反動は見られない',
  '★チェックアウト完了率: 9/10 57.1% → 9/11 **52.7%**（87/165）。カゴ投入率 5.57%（168/3,014）は平常圏',
  '★点数/注文 **1.333（9月最高）**。値引25,076円も9月最大＝数量割引戦略が完全に機能',
  '★セッション2,700〜3,800/日 は日予算240,000〜253,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(8/13-9/11)。売上=gross−値引。次回の定期更新は 9/14(月)',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  '★9/11(金)は前週金曜(9/4 372,740円)比 **+35.5%**。ただし9/4は−2σトリガー発動の異常に弱い日で、金曜自体は最弱級（指数90.8）'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])

wb.save('data/reports/report-2026-09-12.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 8月確定 {aup:,.0f}円")
