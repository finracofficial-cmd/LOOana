# -*- coding: utf-8 -*-
"""2026-09-02 定例レポート本体（昨日=9/1 火）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep0901w.pkl', 'rb'))
FEE = 0.03436   # 2026-09-01 月次再計測。次回 10/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-09-02'   # 9/2朝 data_query（9/1時点）で13セット確認。9/1b と同一・変更なし
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 244000, sum(BUD.values())
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
# --- 7日(8/26-9/1) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD = {'ナノガラス脱毛パッド':259,'W固定スマホ車載ホルダー':125,'快適マジックインソール':86,'ムダ毛シェーバー':56,
'むくみ取りかっさ':37,'バランスケアスリッパ':36,'2WAYシートボックス':29,'姿勢サポートチェア':29,
'ナノバブルシャワーヘッド':19,'完全遮光・接触冷感UVハット':14,'偏光・調光サングラス':10,'優先配送':6,
'3D足臭リセットブラシ':6,'ビジュアル耳かき':5,'携帯電動シェーバー':4,'4WAY':4,'形状記憶日傘':2,
'ネックマッサージャー':1,'瞬間冷感ポンチョ':1,'接触冷感UVパーカー':1,'ジェットウォッシャー':1,
'壁掛けディスペンサー':1,'ヘアドライタオル':1,'1秒折り畳みチェア':1,'完全遮光・形状記憶':1}
STORE_ORD7, STORE_SESS7 = 721, 21571
assert sum(ORD.values()) == 735, sum(ORD.values())   # 全店721より多いのは複数商品を含む注文が両方で数えられるため

# --- 30日(8/03-9/01) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1194,'W固定スマホ車載ホルダー':524,'形状記憶日傘':226,'快適マジックインソール':200,
'ムダ毛シェーバー':200,'接触冷感UVパーカー':184,'害虫ブロッカー':164,'偏光・調光サングラス':158,
'4WAY':152,'2WAYシートボックス':147,'完全遮光・接触冷感UVハット':118,'姿勢サポートチェア':105,
'完全遮光・形状記憶':94,'優先配送':86,'バランスケアスリッパ':82,'接触冷感UVアームカバー':64,
'5WAY腰掛けファン':63,'むくみ取りかっさ':49,'携帯電動シェーバー':37,'卓上冷感クーラー':36,
'ナノバブルシャワーヘッド':22,'3D足臭リセットブラシ':21,'瞬間冷感ポンチョ':13,'3WAYサーキュレーター':11,
'健康サンダル':7,'ビジュアル耳かき':5,'壁掛けディスペンサー':4,'ヘアドライタオル':3,'湯上がりガーゼワンピース':3,
'ジェットウォッシャー':2,'UV歯ブラシ除菌器':2,'瞬間冷却ハンディファン':1,'姿勢サポートベルト':1,
'癒しの指圧マット':1,'1秒折り畳みチェア':1,'リカバリーサンダル':1,'ネックマッサージャー':1}

# --- 30日(8/03-9/01) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック）---
MF_RAW = {'ナノガラス脱毛パッド':(2380451,1284332,32692),'W固定スマホ車載ホルダー':(919242,485280,13735),
'形状記憶日傘':(775749,228028,8680),'カタログ全部（テスト）':(623673,160347,5823),
'害虫ブロッカー':(567109,261299,5129),'ムダ毛シェーバー':(565926,460395,5549),
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':(504476,120225,3755),'接触冷感UVパーカー':(439972,138900,4521),
'偏光・調光サングラス':(428774,191554,4854),'快適マジックインソール':(399001,239571,6072),
'2WAYシートボックス':(351011,120103,3429),'完全遮光・形状記憶・晴雨兼用・UV日傘':(337679,85477,3829),
'姿勢サポートチェア':(316757,199659,3875),'完全遮光・接触冷感UVハット':(281397,64394,3064),
'5WAY腰掛けファン':(203277,68303,2776),'バランスケアスリッパ':(194778,131812,2309),
'接触冷感UVアームカバー':(186988,46245,1394),'卓上冷感クーラー':(125863,47722,1935),
'むくみ取りかっさ':(97749,26701,827),'3D足臭リセットブラシ':(85838,24927,338),
'携帯電動シェーバー':(84398,38821,666),'瞬間冷感ポンチョ':(77762,16894,706),
'ナノバブルシャワーヘッド':(67112,30550,922),'3WAYサーキュレーター扇風機':(49825,11665,442),
'健康サンダル':(41581,13873,385),'ビジュアル耳かき':(26464,9402,148),'UV歯ブラシ除菌器':(13429,4898,109),
'高吸水・速乾ヘアドライタオル':(10669,2706,75),'カタログ全部（テスト） 夏以外':(6080,1903,50),
'1秒折り畳みチェア':(5704,1773,49)}
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
COSTa['ナノガラス脱毛パッド'] = (855 * 757 + 373 * 740) / 1228          # 30日実測ミックスの加重平均【近似】
COSTa['壁掛けディスペンサー'] = (41 * 2528 + 13 * 1981) / 54
PRICEa['壁掛けディスペンサー'] = 363920 / 54
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
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
sh('収益', [f'LOOTY 収益レポート 2026-09-02（昨日 = 9/1 火）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★8月 最終確定（8/31広告費の上書き後）: 実売 {aus:,.0f} / 原価 {auc:,.0f} / 広告 {aua:,.0f} → 利益 {aup:,.0f}円（{aup/aus:.1%}）／1日あたり {aup/31:,.0f}円',
  f'★9月は9/1の1日のみ: 利益 {round(_pl[-1][3]):,}円。日予算244,000円/日の体制での滑り出し',
  f'⚠️ 3日移動平均利益 {p3ma:,.0f}円 が非常ブレーキ基準130,000円を下回った（詳細は「本日の判定」シート。'
  '基準は日予算430,000〜500,000円時代に設定したもので、現体制244,000円/日では利益の絶対水準が構造的に低い。'
  '両日とも黒字・MER平常のため出血ではなく、機械発動はせず基準の再校正を提案）',
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
sh('シンプル判定', ['LOOTY 2026-09-02 定例（昨日=9/1 火）',
 '状態: 🚨縮小・停止=7日MER<分岐 or 7日利益マイナス ／ 🔧改善=3日MER<分岐 or 余裕<0.30 ／ 🚀伸ばす候補=7日MER≥目標かつ週消化率≥95% ／ ✅維持',
 '3窓判定（3日/5日/7日・すべて9/1終端）が本番の意思決定ルール。窓が1つでも割れたら据え置き＝動かさない',
 '「広告費1円あたり利益」= 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）。頑健性は×0.6/0.7/0.8 の3端で符号が変わらないかを見る'],
 ['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,9,9,9,8,8,12,12,12,10,12,13,14,30], {7:'#,##0',8:'#,##0',9:'#,##0',10:'0.0%'})

# ---------- 2 ネクストアクション ----------
NA = [
 ['✅ 回復','昨日(9/1 火)は8/31の底から反発',
  '実売435,402（前日比 +10.4%）・利益94,009円（21.6%）・MER 1.90。'
  '点数/注文も 1.083 → **1.148** に回復（監視トリガー「2日連続1.10割れ」は不発）。'
  'かっさも15時台以降に3個入り、宣言していた事故ライン（購入ゼロのまま8,580円消化）は**未到達のままリセット**',
  '—','完了'],
 ['🔴 判定執行','完全遮光・接触冷感UVハット → ✅合格（6,000円で継続）',
  '宣言基準「6,000円での3日MER ≥ 分岐1.42。割れていれば停止」。実測: クリーン2日(8/31-9/1) 実売23,904/広告11,142 = '
  '**MER 2.15**、変更日8/30を含めた3日でも1.78。どちらの窓でも分岐超え。'
  '9/1は実売14,940（3個）と量も戻った。3日連続分岐割れは8/31で途切れた',
  '—','本日 執行済み'],
 ['🔴 判定執行','カタログ 3日判定（8/30-9/1）→ ✅据え置き（18,000円）',
  'CPA基準: 注文UTM(utm_term=6966272711408)で286注文を1件ずつ帰属 → **19注文23点**。消化52,070円 → '
  'CPA(点) 2,264円 vs 全店1点あたり粗利 3,271円 = **倍率1.45**（3日損益 +23,171円）。前回8/29の1.12から改善。'
  'share基準 0.99（点数シェア7.2% ÷ 消化シェア7.3%）も1.0圏に回復。次回 **9/5**',
  '—','本日 執行済み'],
 ['⏸ 延期','バランスケアスリッパ 増額判定 → 明朝9/3に執行（理由: 3クリーン日目が本日でまだ終わっていない）',
  '8/30に10,000→12,000。判定は「変更後3クリーン日(8/31-9/2)の1日あたり利益 ≥ 変更前7日実測 5,076円/日」。'
  '2日時点の実測は **6,059円/日（8/31 +3,894 / 9/1 +8,225）で基準超え・合格見込み**だが、'
  '窓が1日足りないまま前倒ししない（宣言済みルール）。合格なら機械判定は12,000→15,000（+25%）が次の一手',
  '—','9/3朝'],
 ['🚨 要判断','偏光・調光サングラス — 停止のユーザー実行待ち（3日目）',
  '消化 8/30 2,832 → 8/31 152 → **9/1 126円**。ACTIVE・予算5,000のまま配信死が継続。'
  '9/2判定（3日MER vs 分岐1.30）は分母消失で成立しない。**キャンペーン停止の実行を推奨**（Shopify/Metaの操作はユーザー）。'
  '再挑戦するなら9月中旬以降に「秋の再テスト」（秋CR前提・判定7日CPA(注文)<2,900・減額禁止で継続or停止の二択）',
  '+約150円/日＋管理簡素化','ユーザー実行待ち'],
 ['⚠️ 基準の再校正','非常ブレーキ（3日移動平均利益<130,000円）が数値上は点灯。ただし機械発動しない',
  f'3日移動平均 {p3ma:,.0f}円。この基準は日予算430,000〜500,000円時代（8/6）に設定したもので、'
  '現体制は244,000円/日と半分。8/30-9/1は3日とも黒字（+164,143 / +74,019 / +94,009）・MERもz平常で「出血」ではなく、'
  '発動措置（カタログ減額・赤字商品一律−25%）の前提を満たさない。カタログは倍率1.45の黒字で削る根拠がない。'
  '**提案: ブレーキ閾値をユーザー宣言の最低ライン「1日利益100,000円」に合わせて 3日移動平均<100,000円 へ再設定**（宣言済み判定には影響しない）',
  '—','ユーザー承認待ち'],
 ['👀 明日の判定','9/3朝: 快適マジックインソール／むくみ取りかっさ／ビジュアル耳かき（事後確認）',
  'インソール: P2(8/31-9/2)の1日利益 ≥ 23,356円 が基準。2日実測 +9,380/+17,148 = 計26,528円 → 3日で70,068円に届くには'
  '本日+43,540円が必要で**不合格がほぼ確定**（→27,000へ戻す。グリーン全7サイズ在庫0を併記）。'
  'かっさ: P2の1日利益 ≥ 6,625円 が基準。2日実測 −618/−3,568 = **計−4,186円で不合格がほぼ確定**（→10,000へ巻き戻し。停止ではない）。'
  '耳かき: 9/1にユーザーがPAUSED実行済み（テスト失敗確定・4日+残 消化26,459円/6個/−6,453円）',
  '—','9/3朝'],
 ['👀 判定日','優先配送 790円 — 9/4','宣言済み基準「14日で件数 ≥ 28件」。7日実測 **6件**（アタッチ率 6/721 = 0.83%）。'
  '前週4件と合わせ14日10件前後の見込みで**不合格がほぼ確定**。9/4に536円へ戻すか廃止かを判断','—','9/4'],
 ['👀 判定日','2WAYシートボックス — 9/5朝','9/1に11,000→8,000（−27%）。判定: クリーン3日(9/2-4)の1日利益 ≥ 3,913円。'
  '9/1実績: 実売17,679 / 広告7,402 / 利益+2,900円（変更当日なので窓には入れない）','—','9/5朝'],
 ['👀 監視','点数/注文 1.148（9/1）— 回復基調だが1.15にはあと一歩',
  '8/31 1.083 → 9/1 1.148。「2日連続1.10割れでセット化検討」は不発。9/2も1.15台復帰を確認するまで監視継続',
  '—','9/2'],
 ['🟡 推奨','アップセル手動ペア5組の設定',
  'data/lp/upsell-pairs-2026-08-26.txt の5組をアプリに手入力。判定は実施+14日で異商品ミックス率3.0%以上',
  '週+約4万円','任意（持ち越し7日目）'],
 ['🟡 推奨','カテゴリタグ40件の付与',
  'data/tags/category-mutation-2026-08-23.graphql を GraphiQL で1回実行 ＋ ナノバブルの季節タグ是正','—','任意（持ち越し10日目）'],
 ['🟡 推奨','コレクション冒頭文7本の貼り付け',
  'data/lp/collection-intro-2026-08-23.txt。あわせて「暖房・防寒グッズ」コレクションのAmazon由来HTML説明を削除','—','任意（持ち越し10日目）'],
 ['🟡 推奨','CJで原価確認',
  'あったかインソール 1,000円以下 ／ 外反母趾サポーター 800円以下 なら秋冬のテスト枠へ。'
  '原資はサングラス停止で空く5,000円＋耳かき停止で空いた5,000円','—','任意'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('前日 9/1(火)', R['N1'], R['K1'], R['ACCT1']), ('3日 8/30-9/1', R['N3'], R['K3'], R['ACCT3']),
        ('7日 8/26-9/1', R['N7'], R['K7'], R['ACCT7']), ('30日 8/03-9/01', R['N30'], R['K30'], R['ACCT30']),
        ('9月累積 9/01', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過: Σ商品gross=全店444,410 ／ Σ値引=9,008 ／ Σキャンペーン広告費=229,722円（9/1・アカウントレベルと差0円）',
 '✅ 8/31の広告費は宣言どおり今朝再取得して上書き済み: 223,174 → **223,671円**（+497円/+0.22%。8月確定利益は同額だけ減少）',
 '⚠️ 9/1の広告費は 9/2朝 の取得。Metaの確定まで +0.1%程度動きうるので、明朝に再取得して上書きする',
 '決済ブレンド率 **3.436%**（2026-09-01再計測。次回10/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(9/1 火) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','9/1(火)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '9/1(火)の利益 94,009円 は 7日平均比 −31%。ただし火曜は曜日指数93.4の弱い日で、前週火曜(8/26)比では '
  f'実売 {S1/sum(Sd[n]["2026-08-26"][0]-Sd[n]["2026-08-26"][1] for n in Sd if "2026-08-26" in Sd[n]) - 1:+.1%}。'
  'MER 1.90 は7日平均2.11の90%で平常圏。単日で動かさない').font = Font(name='Arial', size=10, color='CC0000')

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
sh('商品別', ['商品別（7日 8/26-9/1 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化（差0円・w0901.pyでassert済み）',
  '当月累積利益は9月分（=9/1の1日分）。8月確定は「収益」シート冒頭',
  '★3D足臭(8/29停止)・耳かき(9/1停止)・サングラス(配信死)は7日窓に残消化が入っている'],
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
end = datetime.date(2026, 8, 30); WK = []
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
sh('週次診断', ['全店の週次分解（完全週のみ・最新は8/24-30週）。原価はナノガラス/ディスペンサーのみ加重平均単価【近似】',
  '★夏物の崩壊が8月前半の正体。壊れたのは季節物だけで、通年物へ入れ替えて回復した',
  '★8月後半は日予算244,000〜255,000で運転。日予算590,000だった7月とは水準が違うので、利益額の絶対比較はしない'],
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
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(8/03-9/01)」。他シートの7日窓と混ぜて読まないこと',
  'クリックは **アウトバウンドクリック**（data_query 実測・Asia/Tokyo）',
  '✅ 検算: 全31キャンペーンで data_query の消化 = CSV(8/03-9/01) が許容差以内で一致（コード内assert）',
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
  '非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（⚠️ 現体制244,000円/日に対して基準が古い。再校正を提案中 — ネクストアクション参照）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['9/2','完全遮光・接触冷感UVハット','6,000円での3日MER ≥ 分岐1.42。割れていれば夏物なので停止',
  'クリーン2日(8/31-9/1): 実売23,904 / 広告11,142 = **MER 2.15**。変更日8/30を含む3日でも1.78。両窓とも分岐超え',
  '✅ 合格 — 6,000円で継続',
  '3日連続分岐割れ(8/28-30)は8/31で途切れ、9/1は3個・実売14,940と量も回復'],
 ['9/2','カタログ 3日判定（8/30-9/1）','CPA基準（注文UTM実測の帰属）で倍率 ≥1.00 → 据え置き',
  '286注文をUTMで1件ずつ帰属: カタログ19注文23点。消化52,070円 → CPA(点)2,264円 vs 全店粗利/点3,271円 = **倍率1.45**。'
  'share基準0.99。3日損益 +23,171円',
  '✅ 据え置き（18,000円）',
  '前回8/29の倍率1.12から改善。次回 **9/5**'],
 ['9/2→9/3','バランスケアスリッパ 増額判定','変更後3クリーン日(8/31-9/2)の1日利益 ≥ 5,076円（変更前7日実測 35,532÷7）',
  '2日時点: 8/31 +3,894 / 9/1 +8,225 = **6,059円/日で基準超え**。ただし3日目(9/2)が未了',
  '⏸ 明朝9/3に執行（前倒ししない）',
  '合格なら機械判定は 12,000→15,000（+25%）が次の一手。3窓判定も🚀（目標超×消化95%↑）'],
 ['9/2','偏光・調光サングラス','宣言は「3日MER vs 分岐1.30」→ 分母消失で成立しない',
  '消化 8/30 2,832 → 8/31 152 → 9/1 **126円**。ACTIVE・予算5,000のまま配信死継続',
  '🚨 停止のユーザー実行待ち（3日目）',
  '空く5,000円は新商品テスト枠へ保留。秋の再テスト条件は decisions.md に宣言済み'],
 ['9/3','快適マジックインソール 増額判定（30,000の実験）','P2(8/31-9/2)の1日あたり利益 ≥ 23,356円（P1=8/28-29実測）',
  'P2 2日実測: 8/31 +9,380 / 9/1 +17,148 = 計26,528円。3日合格には本日 **+43,540円** が必要',
  '進行中（不合格ほぼ確定）',
  '不合格なら27,000へ戻す（停止ではない）。「グリーン」全7サイズ在庫0の影響を判定時に必ず併記'],
 ['9/3','むくみ取りかっさ 増額判定（13,000の実験）','P2(8/31-9/2)の1日あたり利益 ≥ 6,625円（P1=8/26-29の10,000円クリーン4日実測）',
  'P2 2日実測: 8/31 −618 / 9/1 −3,568 = **計−4,186円**。3日合格には本日 **+24,058円** が必要（数学的にほぼ不可能）',
  '進行中（不合格ほぼ確定）',
  '不合格の処置は **10,000へ巻き戻し**（8/26-29に実測で回っていた水準へ。停止でも中間額でもない）。'
  '9/1は3個売れて事故ライン（購入ゼロで8,580円消化）は未到達のままリセット'],
 ['9/4','優先配送 790円','14日で件数 ≥ 28件','7日実測 6件（アタッチ率 0.83%）。前週4件 → 14日10件前後の見込み',
  '🚨 不合格がほぼ確定','値上げ(536→790)で件数が落ちた。536円へ戻すか廃止かの判断材料を9/4に揃える'],
 ['9/5','2WAYシートボックス 減額判定','クリーン3日(9/2-4)の1日利益 ≥ 3,913円（変更前7日実測 27,394÷7）',
  '9/1(変更当日・窓外): 実売17,679 / 広告7,402 / 利益+2,900円','進行中',''],
 ['9/5','カタログ 3日判定','同上の形式で再判定','—','—',''],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日の執行は2件: UVハット=✅合格（6,000円継続）／ カタログ=✅据え置き（倍率1.45）',
  '★スリッパの増額判定は3クリーン日目(9/2)が未了のため明朝9/3に執行（前倒ししない）',
  '★明日9/3はインソール・かっさの増額判定日。どちらも2日時点で不合格がほぼ確定（戻し先はそれぞれ27,000／10,000）'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-09-01b': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['前日(9/1昼・9/1b)スナップショット → 本日(9/2)。data_query（9/1時点）で13セット確認',
  '合計 **244,000円/日 — 変更なし**（ビジュアル耳かきは CAMPAIGN_PAUSED のため除外）',
  '🚨 サングラス: 予算5,000・ACTIVE のまま消化 9/1 126円。配信死が3日目。停止のユーザー実行待ち',
  '⚠️ 明日9/3の判定が不合格なら: インソール 30,000→27,000 ／ かっさ 13,000→10,000（どちらも「戻し」であって新たな減額ではない）'],
 ['商品/キャンペーン','変更前','変更後','差','変化率','7日MER','分岐','目標','7日余裕','3日MER','3日余裕',
  '倍率7日','倍率3日','消化率(7日)','1円あたり利益','頑健性','印'],
 BR, [26,10,10,9,9,8,7,7,9,8,9,9,9,12,13,14,7],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'+0.0%;-0.0%',14:'0.0%'})

# ---------- 10 CVR推移 ----------
SES = {'2026-08-04':6639,'2026-08-05':5425,'2026-08-06':5138,'2026-08-07':4827,'2026-08-08':5527,'2026-08-09':5886,
'2026-08-10':5245,'2026-08-11':6001,'2026-08-12':4900,'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,
'2026-08-16':5349,'2026-08-17':3438,'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,
'2026-08-22':3220,'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733,'2026-08-27':3145,
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       '★昨日（確定値）' if d == '2026-09-01' else ''] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★9/1は セッション2,936・注文88件 = **CVR 3.00%**。窓の平均圏で転換は健全',
  '★セッション2,700〜3,500/日 は日予算253,000→244,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(8/03-9/01)・祝日 8/11(山の日) を除外。売上=gross−値引。次回の定期更新は 9/7(月)',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  f'★9/1(火)は前週火曜(8/26 421,306円)比 **{(sum(R["N1"].values())/421306-1)*100:+.1f}%**',
  f'★{_hi[0]}曜が最強({_hi[1]:.1f})・{_lo[0]}曜が最弱({_lo[1]:.1f})。中位の曜日は窓次第で入れ替わるので差を根拠に判断しない'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])

wb.save('data/reports/report-2026-09-02.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 8月確定 {aup:,.0f}円")
