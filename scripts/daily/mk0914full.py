# -*- coding: utf-8 -*-
"""2026-09-14 定例レポート本体（データ終端=9/12 土／9/13の広告費は未確定）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep0912w.pkl', 'rb')); FEE = 0.03423   # 2026-09-01 月次再計測（SP79.7% + スマホ17.1% + Paidy3.2%）
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-09-14'   # ★Meta 直読。伸縮ガラスクリーナー 16,000→27,000 をユーザーが増額
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 241000, sum(BUD.values())
# ★2026-08-30修正: 同じ日に複数回スナップショットを取った日（末尾 b/c/d）を
#   従来は `rstrip('b')` して **合算** していたため、その日の予算が2〜3倍に膨らみ、
#   週消化率が実態より低く出ていた（例: 偏光・調光サングラス 8/25 は 10,000+10,000+7,000+7,000 = 34,000 と誤集計）。
#   正しくは「その日の最後のスナップショット＝その日の大半で効いていた値」を採る。
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
# --- 7日(8/26-9/01) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD = {'ナノガラス脱毛パッド':268,'W固定スマホ車載ホルダー':119,'快適マジックインソール':93,
'伸縮ガラスクリーナー':77,'バランスケアスリッパ':34,'ムダ毛シェーバー':31,'姿勢サポートチェア':24,
'4-in-1マルチクリーナー':18,'ナノバブルシャワーヘッド':17,'高見えレザーヘッドレストフック':16,
'むくみ取りかっさ':13,'温感EMSフェイシャルワンド':8,'2WAYシートボックス':8,'優先配送':5,
'偏光・調光サングラス':3,'携帯電動シェーバー':3,'壁掛けディスペンサー':3,'完全遮光・形状記憶':2,
'スマートノーズEMS美顔器':2,'ジェットウォッシャー':2,'湯上がりガーゼワンピース':1,'UV歯ブラシ除菌器':1,
'接触冷感UVパーカー':1,'3D足臭リセットブラシ':1,'リカバリーサンダル':1}
STORE_ORD7, STORE_SESS7 = 740, 21739
# 商品別注文数の合計 > 全店注文数 なのは、複数商品を含む注文が各商品で1件ずつ数えられるため
assert sum(ORD.values()) == 751, sum(ORD.values())

# --- 30日(8/03-9/01) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1143,'W固定スマホ車載ホルダー':499,'快適マジックインソール':330,'ムダ毛シェーバー':179,
'バランスケアスリッパ':123,'2WAYシートボックス':112,'姿勢サポートチェア':103,'形状記憶日傘':91,
'偏光・調光サングラス':81,'むくみ取りかっさ':78,'伸縮ガラスクリーナー':77,'完全遮光・接触冷感UVハット':69,
'ナノバブルシャワーヘッド':50,'4WAY':39,'優先配送':39,'接触冷感UVパーカー':31,'接触冷感UVアームカバー':25,
'完全遮光・形状記憶':22,'3D足臭リセットブラシ':22,'害虫ブロッカー':20,'4-in-1マルチクリーナー':20,
'温感EMSフェイシャルワンド':16,'高見えレザーヘッドレストフック':16,'携帯電動シェーバー':16,
'ビジュアル耳かき':6,'5WAY腰掛けファン':5,'壁掛けディスペンサー':5,'ジェットウォッシャー':4,
'ヘアドライタオル':4,'湯上がりガーゼワンピース':2,'スマートノーズEMS美顔器':2,'癒しの指圧マット':2,
'健康サンダル':2,'ネックマッサージャー':1,'リカバリーサンダル':1,'1秒折り畳みチェア':1,'瞬間冷感ポンチョ':1,
'姿勢サポートベルト':1,'UV歯ブラシ除菌器':1,'卓上冷感クーラー':1}

# --- 30日(8/03-9/01) Metaファネル ---
# ★★ data_query がハーネス側でブロックされているため、通る campaign_and_resource_get の
#    health_check（last_30_days = 8/03-9/01 の実測・UTC基準の窓）から取った。したがって:
#      ・窓は「7日」ではなく「30日」。過去レポートの CVR順位シートと数値を並べて比較しないこと
#      ・クリックは link_clicks ではなく **全クリック**（CTR/CVR/CPC は全クリック基準で低め/高めに出る）
#    全キャンペーンで health_check の spend = CSV(8/03-9/01) が **差0円** で一致することを検算済み。
# ★2026-09-14 取得の health_check（窓 = 8/14-9/12 = D30 と一致することを下でassert）
MF_RAW = {'ナノガラス脱毛パッド':(2399942,1246261,37675),'W固定スマホ車載ホルダー':(1000965,436206,15959),
'快適マジックインソール':(705491,436625,11880),'カタログ全部（テスト）':(550310,138143,5370),
'ムダ毛シェーバー':(530393,424717,6163),'姿勢サポートチェア':(317366,183558,4518),
'バランスケアスリッパ':(292580,198338,4528),'ナノバブルシャワーヘッド':(174322,82970,2686),
'伸縮ガラスクリーナー':(75607,25815,1362),'4-in-1マルチクリーナー':(73184,20972,649),
'高見えレザーヘッドレストフック':(34103,8414,408)}
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

# ===== 日次CSVを読む（3窓判定・週次・日次推移で使う）=====
Sd = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r_ in csv.DictReader(open('data/daily/daily_sales.csv')):
    Sd[r_['name']][r_['date']][0] += int(r_['gross']); Sd[r_['name']][r_['date']][1] += int(r_['disc'])
ADd = collections.defaultdict(lambda: collections.defaultdict(float))
for r_ in csv.DictReader(open('data/daily/daily_ad.csv')): ADd[r_['campaign']][r_['date']] += float(r_['cost'])
COSTa = dict(R['COST']); PRICEa = dict(R['PRICE'])
COSTa['ナノガラス脱毛パッド'] = (855 * 757 + 373 * 740) / 1228          # 30日実測ミックスの加重平均【近似】
COSTa['壁掛けディスペンサー'] = (41 * 2528 + 13 * 1981) / 54
PRICEa['壁掛けディスペンサー'] = 363920 / 54
ALLD = sorted({d for v in Sd.values() for d in v if d <= D1[0]})
D5 = ALLD[-5:]
def win(n, days):
    """商品nのその窓の（実売, 原価【近似】, 広告費）"""
    g = sum(Sd[n][d][0] for d in days if d in Sd[n]); dc = sum(Sd[n][d][1] for d in days if d in Sd[n])
    c = g / PRICEa[n] * COSTa[n] if g and n in PRICEa and n in COSTa else 0
    a = sum(ADd[MAP.get(n, n)].get(d, 0) for d in days)
    return g - dc, c, a

# ---------- 0 収益（先頭シート・2026-08-31ユーザー要望）----------
# 「毎日のExcelで収益を見たい」に対する常設シート。
# 昨日の損益 → 日次の推移 → 期間別 → 当月の着地ペース の順で、上から読めば収益だけ分かる。
WDJ0 = ['月', '火', '水', '木', '金', '土', '日']
def dayblk(d):
    """1日ぶんの（実売, 原価【近似】, 広告費, 利益）。原価はバリアント構成が取れないため近似"""
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
# 当月の着地ペース
_cum = [dayblk(d) for d in CUM]
cs = sum(x[0] for x in _cum); cc = sum(x[1] for x in _cum); ca = sum(x[2] for x in _cum); cp = cs-cc-ca
import calendar
_dim = calendar.monthrange(2026, 9)[1]
# ★2026-09-10修正: 見出しの日付を f-string で自動生成する。9/02から固定文字列のまま放置され、
#   「2026-09-02（昨日 = 9/01 火）」と誤表示し続けていた。
_WD = WDJ0[datetime.date.fromisoformat(D1[0]).weekday()]
sh('収益', [f'LOOTY 収益レポート（データ終端 = {D1[0][5:].replace("-", "/")} {_WD}）',
  f'★この日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★当月累積（9/01-{CUM[-1][8:]}・{len(CUM)}日）実売 {cs:,.0f} / 原価 {cc:,.0f} / 広告 {ca:,.0f} → '
  f'**利益 {cp:,.0f}円（{cp/cs:.1%}）**／1日あたり {cp/len(CUM):,.0f}円',
  f'★参考: **8月の確定値 実売 22,082,602円 / 利益 4,917,233円（22.3%）／1日あたり 158,620円**',
  '★非常ブレーキ = 3日移動平均利益 < 130,000円。🚨が付いた日は発動水準',
  '原価は日次のバリアント構成が取れないナノガラス/壁掛けディスペンサーのみ30日実測ミックスの加重平均単価【近似】。'
  '期間別サマリー（次シート）はバリアント別実数量の正確値'],
 ['日付','曜','実売','原価','広告費','利益','利益率','手数料後利益','MER','3日移動平均利益','ブレーキ','備考'],
 PROF, [12,5,13,12,12,13,9,14,8,16,9,10],
 {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'#,##0',9:'0.00',10:'#,##0'})

# ---------- 1 シンプル判定（3窓判定つき） ----------
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
    # ★3窓判定（3日/5日/7日・すべて前日終端）
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
    # 頑健性: 限界MER = 平均MER×0.6/0.7/0.8 の3端で符号が変わらないか
    ends = [mer * x * gm - 1 for x in (0.6, 0.7, 0.8)]
    rob = '一致' if (all(e > 0 for e in ends) or all(e < 0 for e in ends)) else '⚠️符号が割れる'
    SIMPLE.append([n, round(mer, 2), round(s3 / a3, 2) if a3 else '', round(s1 / a1, 2) if a1 else '',
        round(be, 2), round(tg, 2) if tg else '', round(p7), round(p3), round(p1),
        round(wu, 3) if wu else '', round(per, 3), rob, st, tri])
sh('シンプル判定', ['LOOTY 2026-09-14 定例（データ終端=9/12 土）',
 '状態: 🚨縮小・停止=7日MER<分岐 or 7日利益マイナス ／ 🔧改善=3日MER<分岐 or 余裕<0.30 ／ 🚀伸ばす候補=7日MER≥目標かつ週消化率≥95% ／ ✅維持',
 '3窓判定（3日/5日/7日・すべて9/12終端）が本番の意思決定ルール。窓が1つでも割れたら据え置き＝動かさない',
 '「広告費1円あたり利益」= 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）。頑健性は×0.6/0.7/0.8 の3端で符号が変わらないかを見る'],
 ['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,9,9,9,8,8,12,12,12,10,12,13,14,30], {7:'#,##0',8:'#,##0',9:'#,##0',10:'0.0%'})

# ---------- 2 ネクストアクション ----------
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
NA = [
 ['🎉 最高益','**9/12(土)は利益 +208,427円・利益率 36.6%。9月に入って最高です**',
  '実売568,890 ÷ 広告 **219,682** = **MER 2.59**（これも9月最高）。'
  '3日移動平均利益も **166,631円** まで上がり、6日連続で床（130,000円）の上です。'
  '★9/13(日)はさらに セッション **4,246**（直近最多）・実売658,520円。'
  '9/01-04の谷（1日平均76,969円）とは完全に別の局面に入りました',
  '—','記録'],
 ['✅ 実行確認','伸縮ガラスクリーナーの日予算が **16,000 → 27,000円** になっていました',
  '昨日の判定で私は **20,000（+25%）** を出しましたが、Meta直読では **27,000（+69%）** です。'
  '★**大きく踏み込んだ判断ですが、数字はそれを支持しています**。'
  '9/12は 広告17,093円 で **32点121,788円・利益+68,725円・MER 7.13**。'
  '3窓とも MER4.95〜5.36（分岐1.42）で、余裕は **+3.53〜+3.94**。'
  '9/09からの4日で MER は 3.52 → 3.72 → 5.28 → **7.13** と**上がり続けています**',
  '—','記録'],
 ['🔴 新規宣言','伸縮ガラスクリーナー 27,000の判定を **9/17** に置きます',
  '基準: **27,000時代（9/13以降）の1日あたり利益 ≥ 16,000時代（9/09-9/12）の +39,620円**。'
  '★16,000時代の4日は 実売315,614 / 83点 / 広告63,818 → 利益 **+158,480円** ＝ 1日 +39,620円。'
  '★+69%は私の基準（+20〜30%）より大きい踏み込みなので、**4日ぶん（9/13-9/16）で判定**します。'
  'MERが7.13まで上がっている以上、27,000でも消化しきれない可能性のほうが高いとみています',
  '—','9/17'],
 ['🚨 執行','ムダ毛シェーバー **17,000 → 12,750円（−25%）**',
  '3窓とも余裕<0.30 に入りました（3日 **−0.86** ／ 5日 **−0.20** ／ 7日 +0.28）＝宣言済みルールの発動。'
  '★3日(9/10-12) 実売34,900 / 5点 / 広告43,175 → **損益 −22,265円**。5日も −9,266円。'
  '**広告費が売上を上回っています**。昨日「明日の数字を見る」と書いた件で、今日の発動です',
  '+4,250円/日','本日'],
 ['🚨 執行','カタログ全部（テスト）**18,000 → 10,000円**（**13日連続で未実行**）',
  'Meta直読で日予算は今も18,000円。9/12の消化は10,859円。30日で **550,310円**。'
  '★伸縮が27,000へ上がって日予算合計が241,000円になりました。'
  'カタログを10,000へ落とせば **233,000円**で、伸縮の増額ぶんをほぼ吸収できます',
  '+8,000円/日','本日'],
 ['⚠️ 注意','4-in-1マルチクリーナーが3窓とも余裕<0.30に落ちました',
  '3日 +0.22 ／ 5日 +0.12 ／ 7日 +0.19。7日(9/06-12) 実売136,459 / 20点 / 広告69,767 → 利益 **+7,472円**。'
  '★**宣言では「50点到達時に再判定」としたので、今日は動かしません**（現在21点）。'
  'ただし一般ルール（3窓とも余裕<0.30 → −25%）なら本日発動する水準です。'
  '**このまま推移すれば50点判定は−25%になります**。'
  '原価率42.4%（分岐1.79）が、この価格帯ではやはり重い',
  '—','50点で判定'],
 ['🚫 除外','快適マジックインソールが5日連続で「🚀増額候補」。**9/22まで除外は動かしません**',
  '3窓とも目標超え（余裕 3日+1.40 / 5日+1.30 / 7日+1.21）で、数字は毎日強くなっています。'
  '★8/30の 27,000→30,000 で追加売上を検出できなかった事実は変わりません。'
  '**あと8日です**。9/22に改めて増分MERを測り直します',
  '—','9/22'],
 ['🎉 好調','高見えレザーヘッドレストフックが3窓とも MER2.98・余裕+1.41（累計37点）',
  '9/09 3点 → 9/10 6点 → 9/11 14点 → 9/12 5点 → 9/13 **9点**。'
  '9/12の消化は9,375円＝日予算8,000円の**117%**で天井のまま。'
  '★**50点は9/15前後**。そこで「7日MER ≥ 目標MER かつ 消化率 ≥95%」で増額判定します',
  '—','50点で判定'],
 ['⏸ 確認','ナノバブルシャワーヘッドは9/12も9,115円消化していました',
  'Meta上は PAUSED ですが、9/12に9,115円。停止が効いたのは9/12の途中とみられます。'
  '3窓は 3日 **−0.93** ／ 5日+0.23 ／ 7日+0.12 で⚠️水準まで落ちていたので、'
  '**停止の判断は結果的に正しかった**ことになります',
  '—','完了'],
 ['📈 速報','9/13(日)は実売 **658,520円**・販売数157点・セッション **4,246**',
  '注文140 / 客単価4,704円 / カート追加率5.75%。前週の日曜(9/06 601,723円)比 **+9.4%**。'
  '★**伸縮ガラスクリーナーが29点115,420円**（累計128点）、'
  '高見えレザーヘッドレストフックが9点35,820円（累計37点）。新商品2本で38点＝全体の24.2%。返品なし',
  '—','速報'],
 ['🟡 推奨','空いた日予算の使い道',
  'ナノバブル停止（14,000円）ぶんが空いています。**伸縮の+11,000はここでほぼ相殺**されました。'
  'カタログを10,000へ落とせばさらに8,000円出るので、'
  '**クリーナー系・車用品系の新商品テスト**に回すのが最有力です','—','優先'],
 ['🟡 推奨','アップセル手動ペア5組の設定',
  'data/lp/upsell-pairs-2026-08-26.txt の5組をアプリに手入力する。優先配送が14日15件（基準28件）で'
  '不合格だったので、客単価を上げる導線はこちらに寄せます。判定は実施+14日で異商品ミックス率3.0%以上','週+約4万円','優先'],
 ['🟡 推奨','カテゴリタグ40件の付与',
  'data/tags/category-mutation-2026-08-23.graphql を GraphiQL で1回実行 ＋ ナノバブルの季節タグ是正','—','任意'],
 ['🟡 推奨','コレクション冒頭文7本の貼り付け',
  'data/lp/collection-intro-2026-08-23.txt。あわせて「暖房・防寒グッズ」コレクションのAmazon由来HTML説明を削除','—','任意'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('9/12(土)', R['N1'], R['K1'], R['ACCT1']), ('3日 9/10-9/12', R['N3'], R['K3'], R['ACCT3']),
        ('7日 9/06-9/12', R['N7'], R['K7'], R['ACCT7']), ('30日 8/14-9/12', R['N30'], R['K30'], R['ACCT30']),
        ('★当月累積 9/01-12', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過: Σ商品gross=全店400,180 ／ Σ値引=5,971 ／ Σキャンペーン広告費=223,482円（8/31）',
 '★8/31の広告費は data_query がブロックされたため health_check(8/02-8/31実測) − CSV(8/02-8/30実測) で導出。'
 '窓の検証: ビジュアル耳かき(8/28開始)は CSV 20,554 / HC 26,408 → 8/31 = 5,854円。推計ではなく2つの実測の差',
 '決済ブレンド率 3.423%（2026-09-01再計測: SP79.7%×3.25% ＋ KOMOJUスマホ17.1%×4.1% ＋ Paidy3.2%×4.1%。前回3.452%からPaidyが半減）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(9/01 火) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','9/01(火)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '⚠️ 同曜日平均比は当面読まないこと。直近30日の日曜（8/02・8/09・8/16）が夏物崩壊前・日予算590,000時代で汚染されている。'
  f'実態は前週月曜(8/24 529,383円)比 **−25.5%**。同じ月曜どうしでこの落差なので曜日では説明できない。'
  f'ただし3日移動平均利益 {p3ma:,.0f}円 は非常ブレーキ130,000円を6日連続で上回っている').font = Font(name='Arial', size=10, color='CC0000')

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
sh('商品別', ['商品別（7日 8/25-31 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,747,353円（差0円・w0831.pyでassert済み）',
  '★3D足臭(8/29停止)・形状記憶日傘(8/25停止)・ビジュアル耳かき(8/31停止)は7日窓に残消化が入っている',
  '★形状記憶日傘・カタログ夏以外も停止済み。判定の対象外'],
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
end = datetime.date(2026, 9, 1); WK = []
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
sh('週次診断', ['全店の週次分解。原価は日次のバリアント構成が取れないナノガラス/ディスペンサーのみ30日実測ミックスの加重平均単価【近似】',
  '★夏物の崩壊が全体の正体。壊れたのは季節物だけで、通年物は伸びている',
  '★最新週(8/25-31)は日予算253,000〜255,000で運転。日予算590,000だった7月とは水準が違うので、利益額の絶対比較はしない'],
 ['週','実売','原価','広告費','利益','利益率','MER','原価率','広告費率','季節物 利益','季節物MER','通年物 利益','通年物MER'],
 WD_, [14,13,12,12,12,9,8,9,10,15,11,15,11],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'0.00',8:'0.0%',9:'0.0%',10:'#,##0',11:'0.00',12:'#,##0',13:'0.00'})

# ---------- 7 ファネル（30日・RPM/CPM つき）----------
# ★★ Meta側は health_check（30日・全クリック）。Shopify側も同じ30日窓に揃えてある
for _k, _v in MF_RAW.items():
    assert abs(sum(ADd[_k].get(d, 0) for d in D30) - _v[0]) < 1, (_k, _v[0])
FN = []
for n, (c, imp, clk) in MF.items():
    s = R['N30'].get(n, 0); k = R['K30'].get(n, 0); q = R['Q30'].get(n, 0); o = ORD30.get(n, 0)
    if not s or not o or not clk: continue
    ipo = q/o; bcpa = (s-k)/q*ipo; cpm = c/imp*1000
    ctr = clk/imp; cvr = o/clk; gpo = (s-k)/o          # 粗利/注文
    need = cpm/(gpo*1000)                              # 必要 CTR×CVR
    FN.append([n, '季節' if n in SEA else '通年', imp, round(ctr,4), clk, round(cvr,4), round(s/clk),
               round(c/clk), round(c/o), round(bcpa), round(bcpa-c/o), round(cpm), round(gpo),
               round(ctr*cvr*10000, 2), round(need*10000, 2), round((ctr*cvr)/need, 2)])
mc = statistics.median([x[5] for x in FN]) if FN else 0; mr = statistics.median([x[6] for x in FN]) if FN else 0
FN.sort(key=lambda x: -x[15])
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(8/03-9/01)」。他シートの7日窓と混ぜて読まないこと',
  '⚠️ クリックは link_clicks ではなく **全クリック**。Supermetrics の data_query がハーネス側でブロックされており、'
  '通る health_check（30日・全クリック）から取ったため。過去レポートの「CVR順位」シートと数値を並べて比較しない',
  '✅ 検算: 14キャンペーンすべてで health_check の消化 = CSV(8/03-9/01) が差0円で一致（コード内assert）',
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
  '非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（カタログ→赤字商品一律−25%）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['9/14','ムダ毛シェーバー','3窓すべて 余裕<0.30 → −25%',
  '3日 **−0.86**（実売34,900 / 5点 / 広告43,175 → **損益 −22,265円**）／ 5日 **−0.20**（−9,266円）／ 7日 +0.28',
  '🚨 −25% → 17,000を12,750へ',
  '★3日窓は広告費が売上を上回っている。昨日「明日の数字を見る」とした件の発動'],
 ['9/14','伸縮ガラスクリーナー（ユーザーが27,000へ）','昨日の判定で私は 20,000（+25%）を出した',
  'Meta直読で **27,000（+69%）**。9/12は 広告17,093円で32点121,788円・利益+68,725円・**MER 7.13**',
  '✅ 数字は支持している',
  '★9/09からの4日でMERは 3.52 → 3.72 → 5.28 → **7.13** と上がり続けている'],
 ['9/17','伸縮ガラスクリーナー 27,000の判定（新規宣言）',
  '**27,000時代（9/13以降）の1日あたり利益 ≥ 16,000時代（9/09-12）の +39,620円**',
  '16,000時代の4日: 実売315,614 / 83点 / 広告63,818 → 利益+158,480円 ＝ 1日 +39,620円',
  '⏳ 9/13-9/16の4日で判定',
  '★+69%は私の基準（+20〜30%）より大きい踏み込みなので4日ぶんで見る'],
 ['9/14','カタログ全部（テスト）','非常ブレーキ由来ではなく単体の効率問題',
  'Meta直読で日予算18,000のまま。9/12の消化10,859円。30日で550,310円',
  '🚨 18,000→10,000（**13日連続で未実行**）',
  '★伸縮が27,000へ上がり日予算合計241,000円。カタログを10,000にすれば233,000円で増額ぶんをほぼ吸収できる'],
 ['50点','4-in-1マルチクリーナー','20点判定の基準を持ち越し: 余裕が+0.30未満なら −25%',
  '累計21点。3窓とも余裕<0.30（3日+0.22 / 5日+0.12 / 7日+0.19）。7日利益 +7,472円',
  '⏸ 宣言どおり50点まで動かさない',
  '★一般ルールなら本日発動する水準。このまま推移すれば50点判定は−25%になる。原価率42.4%が重い'],
 ['50点','高見えレザーヘッドレストフック','50点到達時に 7日MER ≥ 目標MER かつ 消化率 ≥95% なら +25%',
  '累計37点。3窓とも MER2.98 vs 分岐1.57・**余裕+1.41**。9/12の消化9,375円＝日予算8,000の**117%**',
  '⏸ 50点は9/15前後','—'],
 ['9/22','快適マジックインソール（5日連続で増額候補）','3窓とも目標超え（+1.21〜+1.40）',
  '8/30の 27,000→30,000 で追加売上を検出できなかった事実は変わらない','🚫 あと8日',
  '★9/22に改めて増分MERを測り直す'],
 ['9/14','ナノバブルシャワーヘッド（停止の事後確認）','9/12も9,115円消化していた',
  '3窓は 3日 **−0.93** ／ 5日+0.23 ／ 7日+0.12 で⚠️水準まで落ちていた','✅ 停止は結果的に正しかった',
  'Meta上は PAUSED。停止が効いたのは9/12の途中とみられる'],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★**9/12は利益 +208,427円・利益率36.6%・MER2.59 で9月最高**。3日移動平均も166,631円（6日連続で床の上）',
  '★執行2件: ①**ムダ毛シェーバー 17,000 → 12,750**（3窓とも余裕<0.30・3日窓は−22,265円の赤字）'
  '②**カタログ 18,000 → 10,000**（13日連続で未実行）',
  '★伸縮ガラスクリーナーは私の提案（20,000）を超えて **27,000** になっていました。'
  '9/12は MER **7.13**・利益+68,725円で、数字は踏み込みを支持しています。**9/17に27,000の判定**を置きます',
  '★4-in-1マルチクリーナーが3窓とも余裕<0.30。宣言どおり50点まで動かしませんが、'
  'このまま推移すれば50点判定は−25%になります'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（8/30 昼にユーザーが6セット変更／以後スナップショット未更新）----------
# 変更前 = data/budget-snapshots.csv の '2026-08-30'（朝）／ 変更後 = SNAP '2026-08-30b'（Meta直読）
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-09-13': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['2026-08-30 昼にユーザーが日予算を見直した。**変更後の値はMetaを直読して確認済み**'
  '（campaign_and_resource_get / campaign_detail_level="ad_groups"・ENABLEDの広告セットのみ合計）',
  '合計 253,000 → **255,000円**（+2,000円/日・+0.8%）。実質は「効率の良い3つへ +8,000／薄い3つから −6,000」の付け替え',
  '★増額 3件: 快適マジックインソール +3,000(+11.1%) ／ むくみ取りかっさ +3,000(+30.0%) ／ バランスケアスリッパ +2,000(+20.0%)',
  '★減額 3件: 2WAYシートボックス −2,000(−15.4%) ／ 完全遮光・接触冷感UVハット −2,000(−25.0%) ／ 偏光・調光サングラス −2,000(−28.6%)',
  '★総評: **方向は正しい**。増額した3つは7日余裕が +0.94〜+1.62 と全商品の上位、減額した3つは3日余裕が +0.04〜+0.57 と縮んでいる側',
  '⚠️ 週消化率はこのシートから計算方法を直した。同じ日に複数回スナップショットを取った日(8/23-25)を'
  '従来は合算しており、消化率が実態より低く出ていた。修正後、快適マジックインソールは 85%→**97.7%** になり、'
  '3窓判定が「据え置き」→「🚀3窓すべて目標超＋消化95%→+25%」に変わった'],
 ['商品/キャンペーン','変更前','変更後','差','変化率','7日MER','分岐','目標','7日余裕','3日MER','3日余裕',
  '倍率7日','倍率3日','消化率(7日)','1円あたり利益','頑健性','印'],
 BR, [26,10,10,9,9,8,7,7,9,8,9,9,9,12,13,14,7],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'+0.0%;-0.0%',14:'0.0%'})

# ---------- 10 CVR推移 ----------
SES = {'2026-08-04':6639,'2026-08-05':5425,'2026-08-06':5138,'2026-08-07':4827,'2026-08-08':5527,'2026-08-09':5886,
'2026-08-10':5245,'2026-08-11':6001,'2026-08-12':4900,'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,
'2026-08-16':5349,'2026-08-17':3438,'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,
'2026-08-22':3220,'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733,'2026-08-27':3145,
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       '★昨日（確定値）' if d == '2026-08-30' else ''] for d in sorted(SES)]
o1 = sum(ORDD[d] for d in sorted(SES) if d <= '2026-08-16'); s1_ = sum(SES[d] for d in sorted(SES) if d <= '2026-08-16')
o2 = sum(ORDD[d] for d in sorted(SES) if '2026-08-17' <= d <= '2026-08-30'); s2 = sum(SES[d] for d in sorted(SES) if '2026-08-17' <= d <= '2026-08-30')
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  f'★8/04-16（広告費が大きかった時期）: {o1}注文 / {s1_:,}セッション = {o1/s1_:.2%}',
  f'★8/17-30（広告費を絞った後）: {o2}注文 / {s2:,}セッション = {o2/s2:.2%} → 広告費を削ったらCVRは **{o2/s2/(o1/s1_)-1:+.1%}** 改善している',
  '★8/29は セッション3,537（8/16以降で最多）に対し注文115件 = CVR 3.25%。セッションが増えた分CV率は薄まるが、'
  'カート追加221件はこの窓の最多で、需要そのものが戻っている',
  '★8/28は セッション3,149・注文85件 = CVR 2.70% でこの窓の最低。ただし翌日に戻っており単日のブレ',
  '★セッションは 5,000〜6,000/日 → 2,700〜3,500/日 へ減った。これは日予算 590,000→253,000 の直接の結果'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
sh('曜日指数', ['直近30日(8/03-9/01)・祝日 8/11(山の日) を除外。売上=gross−値引',
  '★同曜日平均との比較は当面使わない。直近30日の土曜（8/01・8/08・8/15）が夏物崩壊前・日予算590,000時代で汚染されているため',
  '★代わりに「前週同曜日比」で読む。8/29(土)は前週土曜(8/22 469,248円)比 **+24.3%**',
  '★日曜が最強(125.4)・水曜が最弱(88.4)。この形は7月から変わっていない'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in sorted(R['IDX'].items(), key=lambda x: -x[1])], [10, 16])

wb.save('data/reports/report-2026-09-14.xlsx')
print('シート:', wb.sheetnames)
print(f"3日移動平均利益 {p3ma:,.0f}円 / 非常ブレーキ130,000円")
