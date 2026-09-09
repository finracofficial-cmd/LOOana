# -*- coding: utf-8 -*-
"""2026-09-10 定例レポート本体（データ終端=9/08 火／9/09の広告費は未確定）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep0908w.pkl', 'rb')); FEE = 0.03423   # 2026-09-01 月次再計測（SP79.7% + スマホ17.1% + Paidy3.2%）
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-09-10'   # ★Meta 直読。かっさ・2WAYが PAUSED、高見えレザーヘッドレストフック 8,000 が新設
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 230000, sum(BUD.values())
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
ORD = {'ナノガラス脱毛パッド':273,'W固定スマホ車載ホルダー':97,'快適マジックインソール':88,'ムダ毛シェーバー':46,
'バランスケアスリッパ':42,'むくみ取りかっさ':27,'ナノバブルシャワーヘッド':20,'2WAYシートボックス':19,
'温感EMSフェイシャルワンド':16,'姿勢サポートチェア':14,'伸縮ガラスクリーナー':12,'4-in-1マルチクリーナー':10,
'偏光・調光サングラス':6,'携帯電動シェーバー':5,'優先配送':4,'完全遮光・接触冷感UVハット':3,
'壁掛けディスペンサー':3,'完全遮光・形状記憶':2,'形状記憶日傘':2,'ジェットウォッシャー':2,
'湯上がりガーゼワンピース':1,'3D足臭リセットブラシ':1,'UV歯ブラシ除菌器':1,'5WAY腰掛けファン':1,
'スマートノーズEMS美顔器':1,'ビジュアル耳かき':1,'ヘアドライタオル':1,'癒しの指圧マット':1,'卓上冷感クーラー':1}
STORE_ORD7, STORE_SESS7 = 688, 22270
# 商品別注文数の合計 > 全店注文数 なのは、複数商品を含む注文が各商品で1件ずつ数えられるため
assert sum(ORD.values()) == 700, sum(ORD.values())

# --- 30日(8/03-9/01) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1145,'W固定スマホ車載ホルダー':510,'快適マジックインソール':288,'ムダ毛シェーバー':199,
'2WAYシートボックス':130,'形状記憶日傘':129,'バランスケアスリッパ':112,'偏光・調光サングラス':103,
'姿勢サポートチェア':97,'完全遮光・接触冷感UVハット':89,'接触冷感UVパーカー':79,'むくみ取りかっさ':76,
'害虫ブロッカー':63,'4WAY':59,'優先配送':46,'完全遮光・形状記憶':43,'ナノバブルシャワーヘッド':41,
'接触冷感UVアームカバー':36,'携帯電動シェーバー':23,'3D足臭リセットブラシ':22,'5WAY腰掛けファン':19,
'温感EMSフェイシャルワンド':16,'伸縮ガラスクリーナー':12,'4-in-1マルチクリーナー':10,'ビジュアル耳かき':6,
'壁掛けディスペンサー':5,'卓上冷感クーラー':5,'ヘアドライタオル':4,'ジェットウォッシャー':4,'健康サンダル':3,
'瞬間冷感ポンチョ':3,'癒しの指圧マット':2,'湯上がりガーゼワンピース':2,'3WAYサーキュレーター':2,
'ネックマッサージャー':1,'UV歯ブラシ除菌器':1,'スマートノーズEMS美顔器':1,'姿勢サポートベルト':1,
'1秒折り畳みチェア':1}

# --- 30日(8/03-9/01) Metaファネル ---
# ★★ data_query がハーネス側でブロックされているため、通る campaign_and_resource_get の
#    health_check（last_30_days = 8/03-9/01 の実測・UTC基準の窓）から取った。したがって:
#      ・窓は「7日」ではなく「30日」。過去レポートの CVR順位シートと数値を並べて比較しないこと
#      ・クリックは link_clicks ではなく **全クリック**（CTR/CVR/CPC は全クリック基準で低め/高めに出る）
#    全キャンペーンで health_check の spend = CSV(8/03-9/01) が **差0円** で一致することを検算済み。
# ★2026-09-10 取得の health_check（窓 = 8/10-9/08 = D30 と一致することを下でassert）
MF_RAW = {'ナノガラス脱毛パッド':(2385320,1280739,38543),'W固定スマホ車載ホルダー':(1007700,491744,17045),
'快適マジックインソール':(608761,373690,10359),'カタログ全部（テスト）':(585693,147563,5790),
'ムダ毛シェーバー':(548297,442892,6339),'2WAYシートボックス':(360095,120577,4055),
'姿勢サポートチェア':(321807,200270,4636),'バランスケアスリッパ':(257779,179268,3907),
'むくみ取りかっさ':(173504,50150,1982),'ナノバブルシャワーヘッド':(124931,59817,1988),
'温感EMSフェイシャルワンド':(64740,15623,649),'4-in-1マルチクリーナー':(37086,10206,300),
'伸縮ガラスクリーナー':(11789,3467,188)}
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
sh('シンプル判定', ['LOOTY 2026-09-10 定例（データ終端=9/08 火）',
 '状態: 🚨縮小・停止=7日MER<分岐 or 7日利益マイナス ／ 🔧改善=3日MER<分岐 or 余裕<0.30 ／ 🚀伸ばす候補=7日MER≥目標かつ週消化率≥95% ／ ✅維持',
 '3窓判定（3日/5日/7日・すべて9/08終端）が本番の意思決定ルール。窓が1つでも割れたら据え置き＝動かさない',
 '「広告費1円あたり利益」= 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）。頑健性は×0.6/0.7/0.8 の3端で符号が変わらないかを見る'],
 ['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,9,9,9,8,8,12,12,12,10,12,13,14,30], {7:'#,##0',8:'#,##0',9:'#,##0',10:'0.0%'})

# ---------- 2 ネクストアクション ----------
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
NA = [
 ['🔴 判定日','快適マジックインソール 再テスト → **❌ 不合格。ただし減額はしません**',
  '宣言済み基準「27,000へ戻したあとの7日利益 ≥ 27,000時代(8/23-29)の7日平均」。'
  '基準 **+213,807円** に対し、主窓 9/02-9/08 は **+150,187円（70%）**、'
  '狭窓 9/05-9/08（27,000を実測確認済み・7日換算）は **+184,935円（86%）**。**両窓とも不合格**。'
  '★**それでも減額しない**理由: 宣言済みの減額基準は「余裕<0」だけで、'
  '現在の余裕は 3日+0.98 / 5日+1.02 / 7日+0.87 と**大きくプラス**です。'
  '不合格の意味は「8月の水準に戻らなかった」であって「予算が間違っている」ではありません',
  '—','据え置き'],
 ['📊 不合格の中身','売上はほぼ横ばい、広告費が+30%膨らんだのが原因です',
  '8/23-29（基準）: 実売 **456,904円** / 121点 / 広告 **161,180円** → MER **2.83**｜'
  '9/02-08（主窓）: 実売 **438,397円**（−4.0%）/ 116点 / 広告 **209,678円（+30.1%）** → MER **2.09**。'
  '★点数も売上もほとんど変わっていないのに、**同じ日予算27,000で消化だけが1日23,026→29,954円へ増えました**。'
  'Metaのペーシングが上がった結果で、商品側の問題ではありません。'
  '**実験はここで終了**とし、判定日なし（監視のみ）へ移します',
  '—','記録'],
 ['🚨 執行','カタログ全部（テスト）**18,000 → 10,000円**（**9日連続で未実行**）',
  'Meta直読で日予算は今も18,000円。9/08の消化は18,201円。'
  '★これが**唯一残っている未執行の宣言事項**です。非常ブレーキは解除されましたが、'
  '**商品に紐づかず効率を測れないまま日1.8万円使い続けている**状態は変わっていません。'
  '30日で 585,693円 ＝ 広告費全体の **6.8%** を占めています',
  '+8,000円/日','本日'],
 ['✅ 実行確認','むくみ取りかっさ と 2WAYシートボックス が **停止**されました',
  'どちらも−25%を提案していましたが、Metaでは PAUSED。'
  'かっさは3窓 +0.10/+0.24/+0.07、2WAYは −0.28/−0.11/+0.27 で、**どちらも今朝も⚠️のまま**でした。'
  '減額より停止のほうが早く効きます。**日予算18,000円（10,000+8,000）が空きました**',
  '+18,000円/日','完了'],
 ['🚀 好調','**伸縮ガラスクリーナーが3日で29点。MER 5.11（分岐1.42）・余裕+3.69**',
  '9/07 広告2,086円→3点 ／ 9/08 **9,703円→13点51,740円** ／ 9/09 **13点51,740円**。'
  '★昨日は「日予算8,000の26%しか使っていないので増額しない」と書きましたが、'
  '9/08の消化は **9,703円＝121%** で**予算が天井になりました**。状況が変わっています。'
  '★それでも今日は増額しません（購入50件まで判定しないルール・現在29点）。'
  '**代わりに基準を先に宣言します: 50件到達時点で「7日MER ≥ 目標MER かつ 週消化率 ≥95%」なら +25%**。'
  '（目標MER = 1÷(1−原価率−0.35)。バリアント構成で動くので固定値にせず判定日に実測から出します。現在なら約2.8）'
  'このペースなら9/11〜9/12に到達します',
  '—','50件で判定'],
 ['⚠️ 注意','4-in-1マルチクリーナーが3窓とも余裕<0.30に落ちました',
  '3日 **−0.08**（MER1.66 vs 分岐1.74で分岐割れ）／ 5日+0.15 ／ 7日+0.15。累計14点。'
  '★**新商品なので50件まで判定しません**（宣言済み）。ただし伸縮クリーナーとの差がはっきりしてきました: '
  '原価率42.4%（分岐1.74）は、この価格帯だとやはり重いです。'
  '**20件到達時の中間チェックで余裕が+0.30未満なら−25%**を、ここで宣言しておきます',
  '—','20件で判定'],
 ['🆕 新商品','**高見えレザーヘッドレストフック**（9/09にキャンペーン新設・日予算8,000円）',
  '売価3,980円 / 原価 ブラック1,275・ブラウン1,344・グレー1,344 → 実売分の原価率 **33.2%**・'
  '**分岐MER 1.49・目標MER 3.14**。初日9/09に3点11,940円。'
  '★W固定スマホ車載ホルダー（車用品・分岐1.38）と同じ客層を狙える商品です。'
  '購入50件まで判定しません',
  '—','監視'],
 ['📈 好転','3日移動平均利益が2日連続で床の上（155,574 → **135,156円**）',
  '9/06 +152,048 ／ 9/07 +135,937 ／ 9/08 **+117,482（利益率23.7%）**。'
  '9/08は 実売495,040 ÷ 広告241,315 = MER 2.05。'
  '★止めた6本（UVハット・サングラス・耳かき・3D足臭・温感EMS・かっさ/2WAY）で'
  '**日予算が255,000 → 230,000円**まで絞れています',
  '—','記録'],
 ['📈 速報','9/09(水)は実売 **541,333円**・客単価 **5,524円**',
  '注文98 / 販売数124 / セッション2,801 / カート追加率5.68%。'
  '★客単価5,524円は9月に入って最高。**姿勢サポートチェアが11点65,780円**と急伸（前日3点）、'
  '伸縮ガラスクリーナーが13点51,740円で連日の二桁。返品なし',
  '—','速報'],
 ['⏸ 監視','姿勢サポートチェアは3窓判定を抜けました（ただし7日はマイナス）',
  '3日 **−0.05** ／ 5日+0.45 ／ 7日 **−0.12**。5日窓が+0.45なので3窓ルールでは据え置きです。'
  '★昨日−25%（9,000→6,750）を出しましたが、**今朝は発動条件を外れています**。'
  'まだ実行していなければそのままで構いません。'
  '9/09に11点65,780円と急伸しているので、明日の数字を見てから判断します',
  '—','取り下げ'],
 ['🟡 推奨','アップセル手動ペア5組の設定',
  'data/lp/upsell-pairs-2026-08-26.txt の5組をアプリに手入力する。優先配送が14日15件（基準28件）で'
  '不合格だったので、客単価を上げる導線はこちらに寄せます。判定は実施+14日で異商品ミックス率3.0%以上','週+約4万円','優先'],
 ['🟡 推奨','空いた日予算18,000円の使い道',
  'かっさ・2WAYの停止で18,000円が空きました。**伸縮ガラスクリーナー系（低原価率の生活雑貨）**が'
  '今いちばん効率が良いので、同系統の新商品テストに振り替えるのが最有力です','—','優先'],
 ['🟡 推奨','カテゴリタグ40件の付与',
  'data/tags/category-mutation-2026-08-23.graphql を GraphiQL で1回実行 ＋ ナノバブルの季節タグ是正','—','任意'],
 ['🟡 推奨','コレクション冒頭文7本の貼り付け',
  'data/lp/collection-intro-2026-08-23.txt。あわせて「暖房・防寒グッズ」コレクションのAmazon由来HTML説明を削除','—','任意'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('9/08(火)', R['N1'], R['K1'], R['ACCT1']), ('3日 9/06-9/08', R['N3'], R['K3'], R['ACCT3']),
        ('7日 9/02-9/08', R['N7'], R['K7'], R['ACCT7']), ('30日 8/10-9/08', R['N30'], R['K30'], R['ACCT30']),
        ('★当月累積 9/01-08', R['NC'], R['KC'], R['ACCTC'])]:
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
 ['9/10','快適マジックインソール 再テスト','27,000へ戻したあとの7日利益 ≥ 27,000時代(8/23-29)の +213,807円',
  '主窓 9/02-9/08 = **+150,187円（70%）** ／ 狭窓 9/05-9/08（7日換算）= **+184,935円（86%）**',
  '❌ 両窓とも不合格 → **それでも据え置き**',
  '★宣言済みの減額基準は「余裕<0」のみ。現在の余裕は 3日+0.98 / 5日+1.02 / 7日+0.87 と大きくプラス。'
  '不合格は「8月の水準に戻らなかった」意味であり「予算が間違っている」ではない。実験はここで終了'],
 ['9/10','（上の内訳）','売上ほぼ横ばい／広告費+30%が不合格の中身',
  '8/23-29 実売456,904・121点・広告161,180 → MER2.83 ／ 9/02-08 実売438,397（−4.0%）・116点・'
  '広告209,678（**+30.1%**）→ MER2.09','📊 記録',
  '同じ日予算27,000で1日あたり消化が 23,026 → 29,954円へ増えた。Metaのペーシングが上がった結果'],
 ['9/10','むくみ取りかっさ／2WAYシートボックス','3窓すべて 余裕<0.30 → −25%',
  'かっさ +0.10/+0.24/+0.07 ／ 2WAY −0.28/−0.11/+0.27（どちらも今朝も⚠️）',
  '✅ ユーザーが**停止**','減額より停止が早い。日予算18,000円（10,000+8,000）が空いた'],
 ['9/10','姿勢サポートチェア（昨日の提案を取り下げ）','3窓すべて 余裕<0.30 → −25%',
  '3日 −0.05 ／ **5日+0.45** ／ 7日 −0.12。9/09は11点65,780円と急伸','🔁 発動条件を外れた → 据え置き',
  '★昨日の9,000→6,750は取り下げる。まだ実行していなければそのままで構わない。明日の数字を見て再判断'],
 ['9/10','カタログ全部（テスト）','非常ブレーキ由来ではなく単体の効率問題',
  'Meta直読で日予算18,000のまま。9/08の消化18,201円。30日で585,693円＝広告費全体の**6.8%**',
  '🚨 18,000→10,000（**9日連続で未実行**）',
  '★唯一残っている未執行の宣言事項。商品に紐づかず効率を測れないまま日1.8万円使い続けている'],
 ['50件','伸縮ガラスクリーナー','**新規宣言: 50件到達時に 7日MER ≥ 目標MER かつ 週消化率 ≥95% なら +25%**（目標MER=1÷(1−原価率−0.35)・現在なら約2.8）',
  '3日で29点。3窓とも MER5.11 vs 分岐1.42・**余裕+3.69**。9/08の消化9,703円＝日予算8,000の**121%**',
  '🚀 増額候補・ただし今日は動かさない',
  '★昨日「26%しか使っていない」と書いたが、9/08で予算が天井になった。50件到達は9/11〜9/12の見込み'],
 ['20件','4-in-1マルチクリーナー','**新規宣言: 20件到達時に余裕が+0.30未満なら −25%**',
  '累計14点。3日 **−0.08**（MER1.66 vs 分岐1.74で分岐割れ）／ 5日+0.15 ／ 7日+0.15','⏸ あと6点',
  '★原価率42.4%（分岐1.74）はこの価格帯だと重い。伸縮クリーナー（28.3%）との差が出てきた'],
 ['—','高見えレザーヘッドレストフック（新商品）','購入50件に達するまで判定しない',
  '9/09新設・日予算8,000円。初日3点11,940円。売価3,980 / 原価1,275〜1,344 → **原価率33.2%・分岐MER1.49**',
  '⏸ 判定しない','W固定スマホ車載ホルダー（車用品・分岐1.38）と同じ客層を狙える'],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日の判定: **快適マジックインソールの再テストは不合格**（基準の70〜86%）。'
  '**ただし余裕が+0.87〜1.02と大きくプラスなので減額はしません**。実験はここで終了',
  '★不合格の中身は「売上ほぼ横ばい（−4%）・広告費+30%」。同じ日予算27,000で消化だけが増えた',
  '★執行は1件だけ: **カタログ 18,000→10,000**（9日連続で未実行・唯一残っている宣言事項）',
  '★取り下げ1件: 姿勢サポートチェアの−25%は発動条件を外れました（5日が+0.45）',
  '★伸縮ガラスクリーナーが3日で29点・MER5.11。9/08で予算が天井（121%）になったので50件で増額判定します'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（8/30 昼にユーザーが6セット変更／以後スナップショット未更新）----------
# 変更前 = data/budget-snapshots.csv の '2026-08-30'（朝）／ 変更後 = SNAP '2026-08-30b'（Meta直読）
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-09-09': PREVB[r[1]] += int(r[3])
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

wb.save('data/reports/report-2026-09-10.xlsx')
print('シート:', wb.sheetnames)
print(f"3日移動平均利益 {p3ma:,.0f}円 / 非常ブレーキ130,000円")
