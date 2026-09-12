# -*- coding: utf-8 -*-
"""2026-09-13 定例レポート本体（昨日=9/12 土）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep0912w.pkl', 'rb'))
FEE = 0.03436   # 2026-09-01 月次再計測。次回 10/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-09-13'   # 9/13 00:2x時点（9/12bリバランス後から変更検出なし・消化パターンと整合）
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
# --- 7日(9/06-9/12) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD = {'ナノガラス脱毛パッド':268,'W固定スマホ車載ホルダー':119,'快適マジックインソール':93,
'伸縮ガラスクリーナー':77,'バランスケアスリッパ':34,'ムダ毛シェーバー':31,'姿勢サポートチェア':24,
'4-in-1マルチクリーナー':18,'ナノバブルシャワーヘッド':17,'高見えレザーヘッドレストフック':16,
'むくみ取りかっさ':13,'温感EMSフェイシャルワンド':8,'2WAYシートボックス':8,'優先配送':5,
'偏光・調光サングラス':3,'携帯電動シェーバー':3,'壁掛けディスペンサー':3,'完全遮光・形状記憶':2,
'スマートノーズEMS美顔器':2,'ジェットウォッシャー':2,'湯上がりガーゼワンピース':1,'UV歯ブラシ除菌器':1,
'接触冷感UVパーカー':1,'3D足臭リセットブラシ':1,'リカバリーサンダル':1}
STORE_ORD7, STORE_SESS7 = 740, 21739
assert sum(ORD.values()) == 751, sum(ORD.values())   # 全店740より多いのは複数商品を含む注文が両方で数えられるため

# --- 30日(8/14-9/12) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1143,'W固定スマホ車載ホルダー':499,'快適マジックインソール':330,
'ムダ毛シェーバー':179,'バランスケアスリッパ':123,'2WAYシートボックス':112,'姿勢サポートチェア':103,
'形状記憶日傘':91,'偏光・調光サングラス':81,'むくみ取りかっさ':78,'伸縮ガラスクリーナー':77,
'完全遮光・接触冷感UVハット':69,'ナノバブルシャワーヘッド':50,'4WAY':39,'優先配送':39,
'接触冷感UVパーカー':31,'接触冷感UVアームカバー':25,'完全遮光・形状記憶':22,'3D足臭リセットブラシ':22,
'害虫ブロッカー':20,'4-in-1マルチクリーナー':20,'携帯電動シェーバー':16,'温感EMSフェイシャルワンド':16,
'高見えレザーヘッドレストフック':16,'ビジュアル耳かき':6,'壁掛けディスペンサー':5,'5WAY腰掛けファン':5,
'ジェットウォッシャー':4,'ヘアドライタオル':4,'スマートノーズEMS美顔器':2,'癒しの指圧マット':2,
'健康サンダル':2,'湯上がりガーゼワンピース':2,'ネックマッサージャー':1,'UV歯ブラシ除菌器':1,
'瞬間冷感ポンチョ':1,'姿勢サポートベルト':1,'卓上冷感クーラー':1,'1秒折り畳みチェア':1,'リカバリーサンダル':1}

# --- 30日(8/14-9/12) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック）---
MF_RAW = {'ナノガラス脱毛パッド':(2399911,1246233,31710),'W固定スマホ車載ホルダー':(1000954,436198,12864),
'快適マジックインソール':(705470,436606,10501),'カタログ全部（テスト）':(550295,138137,4876),
'ムダ毛シェーバー':(530373,424708,4888),'形状記憶日傘':(353856,86750,3400),
'姿勢サポートチェア':(317364,183554,3875),'2WAYシートボックス':(314655,97119,2686),
'バランスケアスリッパ':(292566,198330,3723),'偏光・調光サングラス':(218472,91400,2480),
'完全遮光・接触冷感UVハット':(201260,44109,2055),'むくみ取りかっさ':(180745,52807,1584),
'ナノバブルシャワーヘッド':(174318,82965,2032),'接触冷感UVパーカー':(114601,35256,1011),
'3D足臭リセットブラシ':(85838,24927,338),'4WAY 取り付けOK 小型瞬間冷却ハンディファン':(82537,21507,620),
'伸縮ガラスクリーナー':(75591,25809,1031),'4-in-1マルチクリーナー':(73163,20969,491),
'接触冷感UVアームカバー':(71140,15863,565),'温感EMSフェイシャルワンド':(64858,15636,456),
'完全遮光・形状記憶・晴雨兼用・UV日傘':(64107,14327,628),'害虫ブロッカー':(59999,26647,562),
'高見えレザーヘッドレストフック':(34098,8413,325),'5WAY腰掛けファン':(28284,7864,350),
'ビジュアル耳かき':(26464,9402,148),'高吸水・速乾ヘアドライタオル':(10669,2706,75),
'カタログ全部（テスト） 夏以外':(6080,1903,50),'1秒折り畳みチェア':(5704,1773,49),
'卓上冷感クーラー':(735,293,11)}
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
COSTa['ナノガラス脱毛パッド'] = (923 * 757 + 323 * 740) / 1246          # 30日実測ミックスの加重平均【近似】
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
sh('収益', [f'LOOTY 収益レポート 2026-09-13（昨日 = 9/12 土）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★9月累積（9/01-12・{len(CUM)}日）: 実売 {cs:,.0f} / 利益 {cp:,.0f}円（{cp/cs:.1%}）／1日あたり {cp/len(CUM):,.0f}円（8月確定は {aup:,.0f}円・{aup/31:,.0f}円/日）',
  '★9/12(土)は 実売 **568,890円**・利益 **+207,700円前後（36.5%）**・MER **2.59** — **利益額・利益率とも9月最高。北極星の35%を初めて超えた日**',
  '★前週土曜(9/5 534,465円)比 **+6.4%**。広告費219,567円は9月で2番目に少ない＝「安く多く売れた」理想形',
  '🚀 **ガラスクリーナー 20,000円初日に32個・実売121,788円・利益+68,135円・MER7.13**。6日で予算2.5倍にした攻めが正解だった',
  '🚀 ナノガラス 48個・+73,898円・倍率1.95 ／ インソール 23個・+43,395円・MER3.12（32,000の2日目も基準超え）／ チェア+17,985円・スリッパ12,000初日+13,677円',
  f'✅ 全店CVR **3.74%（9月最高を更新）**・カゴ投入率6.77%も最高。セッション3,132・注文117件。3日移動平均利益 {p3ma:,.0f}円',
  '✅ 朝6時の同時刻カットは6件で「静か」に見えたが終日117件＝**朝の断面は構造的に当てにならない**の実証がまた1件',
  '⚠️ 負け組: ナノバブル−4,383円（11,000復帰初日もまだ赤・3日連続）／ムダ毛−2,805円＋返品1点（12,000クリーン1日目・9/15判定は未達ペース）／W固定+9,097円（33,000の2日目でペース減速）',
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
sh('シンプル判定', ['LOOTY 2026-09-13 定例（昨日=9/12 土）',
 '状態: 🚨縮小・停止=7日MER<分岐 or 7日利益マイナス ／ 🔧改善=3日MER<分岐 or 余裕<0.30 ／ 🚀伸ばす候補=7日MER≥目標かつ週消化率≥95% ／ ✅維持',
 '3窓判定（3日/5日/7日・すべて9/12終端）が本番の意思決定ルール。窓が1つでも割れたら据え置き＝動かさない',
 '「広告費1円あたり利益」= 限界MER×粗利率 − 1（限界MER = 平均MER×0.7）。頑健性は×0.6/0.7/0.8 の3端で符号が変わらないかを見る'],
 ['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,9,9,9,8,8,12,12,12,10,12,13,14,30], {7:'#,##0',8:'#,##0',9:'#,##0',10:'0.0%'})

# ---------- 2 ネクストアクション ----------
NA = [
 ['🏆 記録','**利益率36.5%＝北極星35%を初超過**（利益+20.8万円も9月最高）',
  '広告費が9月2番目に少ない日（219,567円）に売上が前週土曜比+6.4%＝効率と規模が同時に立った。'
  '要因: ①ガラスクリーナー20,000初日の爆発 ②ナノガラス好調 ③CVR3.74%・カゴ投入6.77%の9月最高',
  '—','—'],
 ['📋 本日の執行','**なし**（9/13朝に判定日の商品はない）',
  '明日9/14朝: インソール32,000（2日連続基準超え・確定方向）／W固定33,000（2日平均24,738円 vs 基準25,106円で**攻防**）＋曜日指数更新・unitCost週次再取得',
  '—','9/14朝'],
 ['🚀 記録','ガラスクリーナー 20,000円初日: 32個・+68,135円・MER7.13',
  '8,000→20,000へ6日で2.5倍にした攻めの増額が正解だったことがほぼ確定。9/16朝判定（3日倍率≥1.3かつCPA≤2,837円）は現状圧勝ペース。'
  '出稿6日で77注文・値引累計14,000円超＝まとめ買い戦略の代表作に',
  '—','9/16朝'],
 ['⚠️ 要注意','ナノバブル — 3日連続赤字（−11,427→−8,021→−4,383円）',
  '11,000へ戻した初日も赤字。7日窓では+10,283円前後だが直近3日の悪化が続く。'
  '**新判定を宣言: 9/15朝、11,000でのクリーン3日(9/12-14)の利益合計 ≥ 0円**。割れたら8,000へ減額を提案',
  '—','9/15朝'],
 ['👀 進行中','ムダ毛12,000 クリーン1日目 −2,805円（9/15判定は未達ペース）',
  '基準: 3日平均 ≥5,379円/日。1日目−2,805円＋返品1点。このペースなら17,000へ戻す提案になる',
  '—','9/15朝'],
 ['👀 進行中','9/16朝判定の初日: フック12,000は+2,019円と低調',
  'スリッパ12,000は+13,677円（基準9,694円/日を初日クリア）。フックは増額後に失速気味（5個・MER1.93）。'
  'まだ1日目・学習再配分の揺れの可能性が高いので触らない',
  '—','9/16朝'],
 ['🔴 明朝','9/12広告費 219,567円の再取得・確認＋**月曜タスク**（曜日指数更新・全商品unitCost再取得）',
  '9/11は 229,108→**229,184**（+76円）で確定済み・上書き実施',
  '—','明朝'],
 ['🟡 実行待ち','購入後クーポン（Shopify Flow）／Selleasy／優先配送536円／カゴ落ちメール／GSCサイトマップ登録',
  'クーポン判定10/7。GSC登録はブログ42本のインデックス判定（10月）の前提。※9/12は優先配送の購入0件',
  '合計+20万円/月規模','実行待ち'],
 ['🟡 推奨','秋テスト第2波（9/15前後）',
  'ガラス・フックの2連勝で「複数個買う理由」基準は実証済み。次弾: ◎あったかインソール／着圧ソックス2-3足／衣類圧縮袋セット',
  '当たり1本=週6万円〜','今週'],
 ['🟡 提案','非常ブレーキ閾値の再校正（130,000→100,000円）','承認待ち継続。直近3日移動平均は16万円超で当面発動リスクなし','—','ユーザー判断'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('前日 9/12(土)', R['N1'], R['K1'], R['ACCT1']), ('3日 9/10-12', R['N3'], R['K3'], R['ACCT3']),
        ('7日 9/06-12', R['N7'], R['K7'], R['ACCT7']), ('30日 8/14-9/12', R['N30'], R['K30'], R['ACCT30']),
        ('9月累積 9/01-12', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過: Σ商品gross=全店587,200 ／ Σ値引=18,310 ／ Σ広告費=219,567円（9/12・広告セット合算。アカウントレベル219,576円と9円差=0.004%）',
 '✅ 9/11の広告費は再取得で確定済み（229,108円 → **229,184円**・+76円。9/13 00:2xに上書き。adset合算=アカウント差0円）',
 '⚠️ 9/12の広告費は 9/13 00:2x の取得【暫定】。確定まで+0.1%程度動く → 明朝に再取得して確認する',
 '★ガラスクリーナー・ヘッドレストフックの原価は保守側の最高値バリアント単価で計上（フックは黒1,275だが1,344で計上＝利益は保守側）',
 '★9/12の返品は3点（ムダ毛1・害虫1・サングラス1＝計3,980円ほか）。A案につき売上・利益とも控除しない',
 '決済ブレンド率 **3.436%**（2026-09-01再計測。次回10/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(9/12 土) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','9/12(土)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '9/12(土)は利益+20.8万円・利益率36.5%で9月最高、北極星35%を初超過。牽引はナノガラス48個とガラスクリーナー32個（20,000初日にMER7.13）。CVR3.74%・カゴ投入6.77%も9月最高で、質と量が同時に来た日。負けはナノバブル・ムダ毛の小口2本のみ').font = Font(name='Arial', size=10, color='CC0000')

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
sh('商品別', ['商品別（7日 9/06-9/12 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化（差0円・w0908.pyでassert済み）',
  '当月累積利益は9月分（9/01-08・8日）',
  '★伸縮ガラスクリーナーは9/7出稿（稼働6日）・高見えレザーヘッドレストフックは9/9昼出稿（稼働3.5日）。7日ベースで他商品と単純比較しないこと',
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
 ['9/13','（本日の判定なし）','増額組のクリーン測定中','—','—','—'],
 ['9/14','快適マジックインソール 32,000の判定（クリーン3日 9/11-13）','3日平均利益 ≥24,134円/日（割れたら27,000へ）',
  '9/11 +24,511 ／ 9/12 **+43,395** = 2日平均33,953円','進行中（**確定方向**）',''],
 ['9/14','W固定 33,000の判定（クリーン3日 9/11-13）','3日平均利益 ≥25,106円/日（割れたら30,000へ）',
  '9/11 +40,379 ／ 9/12 +9,097 = 2日平均24,738円','進行中（**攻防・9/13次第**）',''],
 ['9/14(月)','曜日指数の定期更新・unitCost週次再取得','毎週月曜タスク','','待機',''],
 ['9/15','ムダ毛シェーバー 12,000の判定（クリーン3日 9/12-14）','3日平均利益 ≥5,379円/日',
  '1日目 −2,805円＋返品1点','進行中（未達ペース）','未達なら17,000へ戻す'],
 ['9/15','ナノバブル 11,000の再判定（クリーン3日 9/12-14）※新規宣言','3日利益合計 ≥ 0円',
  '3日連続赤字（−11,427→−8,021→−4,383円）。復帰初日も赤','進行中（未達ペース）','割れたら8,000へ減額を提案'],
 ['9/16','ガラスクリーナー 20,000の判定（クリーン3日 9/13-15）','3日倍率≥1.3 かつ CPA(個)≤2,837円',
  '初日(9/12・非クリーン) 32個・+68,135円・MER7.13・CPA534円','待機（圧勝ペース）','割れたら16,000へ'],
 ['9/16','フック 12,000の判定（クリーン3日 9/13-15）','3日倍率 ≥1.3（割れたら10,000へ）',
  '初日(9/12・非クリーン) 5個・+2,019円・MER1.93（倍率1.34）','待機（ぎりぎり圏）',''],
 ['9/16','スリッパ 12,000の判定（クリーン3日 9/13-15）','3日平均利益 ≥9,694円/日で確定',
  '初日(9/12・非クリーン) +13,677円・MER3.27','待機（クリアペース）',''],
 ['9/18','カタログ 14,000の判定（クリーン7日 9/11-17）','7日Meta-ROAS ≥2.0で継続／<2.0なら9,000へ',
  '9/12は10,866円消化（78%）と絞れてきた','待機',''],
 ['10/7','購入後クーポン（LOOTY500）の判定','30日リピート率 >6.38%で継続','Shopify Flow設定はユーザー実行待ち','待機',''],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日の執行: **なし**。体制は 245,000円/日・12セット。新規宣言1件: ナノバブル9/15朝判定（クリーン3日利益合計≥0円）',
  '★次: 9/14朝 インソール/W固定＋月曜タスク → 9/15朝 ムダ毛/ナノバブル → 9/16朝 ガラス/フック/スリッパ → 9/18朝 カタログ',
  '★倍率の定義: **MER ÷ 分岐MER**。1.0未満＝赤字',
  '★セール明け2日目(9/12)も反動なし＝「セール吸引」仮説はほぼクローズ（9/13の日曜で最終確認）'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-09-12b': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['前日(9/12bリバランス後)スナップショット → 本日(9/13)',
  '合計 245,000 → **245,000円/日**。9/12b以降の変更検出なし（消化パターンとも整合）',
  '★体制: 9/14〜9/16に判定7本が並ぶ。判定日まで予算を動かさないのが判定精度のために望ましい',
  '★9/12の消化は 219,567円＝予算245,000円の89.6%。土曜として静かな消化で、その分MERが2.59へ伸びた',
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
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936,'2026-09-02':3142,'2026-09-03':3340,'2026-09-04':3293,'2026-09-05':3217,'2026-09-06':3752,'2026-09-07':2787,'2026-09-08':2739,'2026-09-09':2801,'2026-09-10':3514,'2026-09-11':3014,'2026-09-12':3132}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88,'2026-09-02':92,'2026-09-03':103,'2026-09-04':74,'2026-09-05':106,'2026-09-06':122,'2026-09-07':96,'2026-09-08':95,'2026-09-09':98,'2026-09-10':116,'2026-09-11':96,'2026-09-12':117}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       ('★昨日（CVR 3.74%＝9月最高を更新）' if d == '2026-09-12' else '（CVR 3.19%）' if d == '2026-09-11'
        else '（−2σトリガー発動日）' if d == '2026-09-04' else '')] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★9/12は セッション3,132・注文117件 = **CVR 3.74%（9月最高を更新）**',
  '★チェックアウト完了率: 9/11 52.7% → 9/12 **56.9%**（111/195）。**カゴ投入率 6.77%（212/3,132）は9月最高**',
  '★点数/注文 1.197（140点/117注文）。朝6時時点の「CVR1.56%」が終日3.74%へ＝朝の断面CVRは判断に使わない（実証2例目）',
  '★セッション2,700〜3,800/日 は日予算240,000〜253,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(8/14-9/12)。売上=gross−値引。次回の定期更新は 9/14(月)＝明日',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  '★9/12(土)は前週土曜(9/5 534,465円)比 **+6.4%**。土曜は指数110.1の強い曜日'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])

wb.save('data/reports/report-2026-09-13.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 8月確定 {aup:,.0f}円")
