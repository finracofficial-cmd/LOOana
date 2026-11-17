# -*- coding: utf-8 -*-
"""2026-11-18 定例レポート本体（昨日=11/17 火。11/16の広告費は確定値に上書き）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep1117w.pkl', 'rb'))
FEE = 0.03325   # 2026-11-02 月次再計測（直近100注文 #30857〜#30956・553,322円）。次回 12/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-11-18'   # 11/18 00時台の全セット（data_query。マルチクリップ 10,000 は Meta 直読でも確認）＝197,600
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 197600, sum(BUD.values())
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]
# 8行未満のスナップショットは変わった行だけ＝広告セット単位で前の状態に上書きして積む（moves1116.py と同じ）。その日の最後の状態をその日の予算にする
_ROWS = collections.defaultdict(dict)
for r in body: _ROWS[r[0]][(r[1], r[2])] = int(r[3])
_ST = {}; _STK = {}
for _k in sorted(_ROWS):
    _ST = dict(_ROWS[_k]) if len(_ROWS[_k]) >= 8 else {**_ST, **_ROWS[_k]}
    _STK[_k] = dict(_ST)
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for _k in sorted(_STK):
    _sum = collections.defaultdict(int)
    for (_c, _a), _v in _STK[_k].items(): _sum[_c] += _v
    for _c in set(_sum) | set(BSNAP):
        BSNAP[_c][_k[:10]] = _sum.get(_c, 0)

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
MULTI = {'高見えレザーヘッドレストフック': ('高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv2', '高見えレザーヘッドレストフックv3', '高見えレザーヘッドレストフックv4'), '快適マジックインソール': ('快適マジックインソール', '快適マジックインソールv2', '快適マジックインソール v3')}   # w1116.py と同じ
BNAME = {n: n for n, c in MAP.items() if c.endswith('v2')}   # 予算の記録は元の商品名（ノーズ・シェーバー）
INV.update({'高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv3': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック', '快適マジックインソールv2': '快適マジックインソール', '快適マジックインソール v3': '快適マジックインソール'})
# --- 7日(11/11-11/17) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1117/ord7_raw.json から生成）---
ORD = {'伸縮ガラスクリーナー':109,'W固定スマホ車載ホルダー':64,'ワイド水切りワイパー':64,'ナノガラス脱毛パッド':62,'優先配送 (VIP特典)':80,'マグネットドアクッション':33,
'快適マジックインソール':29,'4-in-1マルチクリーナー':24,'伸縮ワックス洗車ブラシ':22,'スマートノーズEMS美顔器':20,'3WAY着る電気ブランケット':11,'優先配送':11,
'360°マルチクリップ車載スマホホルダー':10,'携帯電動シェーバー':9,'防風あったか裏起毛パンツ':8,'クリアビューレインガードフィルム':5,'高見えレザーヘッドレストフック':3,'すき間収納シートポケット':2,
'2WAYシートボックス':2,'高見えレザードアポケット':1,'ファスナー修理キット':1,'コードレスダブルミスト加湿器':1,'ムダ毛シェーバー':1}
STORE_ORD7, STORE_SESS7 = 474, 17193   # 注文=ShopifyQL 7日直接・セッション=日次の合計
assert sum(ORD.values()) == 572, sum(ORD.values())   # 全店474より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）

# --- 30日(10/19-11/17) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1117/ord30_raw.json から生成）---
ORD30 = {'ナノガラス脱毛パッド':551,'伸縮ガラスクリーナー':488,'W固定スマホ車載ホルダー':398,'優先配送 (VIP特典)':471,'伸縮ワックス洗車ブラシ':195,'快適マジックインソール':173,
'ワイド水切りワイパー':162,'ポータブルヒートシーラー':113,'4-in-1マルチクリーナー':110,'マグネットドアクッション':109,'クリアビューレインガードフィルム':55,'高見えレザーヘッドレストフック':47,
'姿勢サポートチェア':38,'コードレスダブルミスト加湿器':37,'優先配送':30,'スマートノーズEMS美顔器':21,'ナノバブルシャワーヘッド':17,'携帯電動シェーバー':13,
'壁掛けディスペンサー':12,'3WAY着る電気ブランケット':11,'360°マルチクリップ車載スマホホルダー':10,'高見えレザードアポケット':10,'防風あったか裏起毛パンツ':8,'2WAYシートボックス':5,
'完全遮光・形状記憶':4,'バランスケアスリッパ':3,'ムダ毛シェーバー':3,'偏光・調光サングラス':3,'ネックマッサージャー':3,'むくみ取りかっさ':2,
'すき間収納シートポケット':2,'ファスナー修理キット':2,'5WAY腰掛けファン':2,'健康サンダル':1,'UV歯ブラシ除菌器':1,'シリコンホールド膝サポーター':1,
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':1,'オートソープディスペンサー':1,'1秒折り畳みチェア':1,'コードレス毛玉クリーナー':1,'姿勢サポートベルト':1,'電動温熱カッサ':1,
'ロングニトリル家事手袋':1,'ヘアドライタオル':1,'形状記憶日傘':1}
assert sum(ORD30.values()) == 3120, sum(ORD30.values())

# --- 30日(10/19-11/17) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1117/mf30_raw.txt から生成）---
MF_RAW = {'ナノガラス脱毛パッド':(1257178,1047883,15699),'伸縮ガラスクリーナー':(1059696,415510,13698),
'W固定スマホ車載ホルダー':(896219,435173,13111),'快適マジックインソール':(581284,343877,5949),
'伸縮ワックス洗車ブラシ':(431369,102492,4484),'ワイド水切りワイパー':(280371,86649,3102),
'ポータブルヒートシーラー':(275515,68533,3696),'カタログ全部（テスト）':(267787,75919,2666),
'4-in-1マルチクリーナー':(262418,120396,4117),'マグネットドアクッション':(215660,60886,2864),
'コードレスダブルミスト加湿器':(155180,38713,1409),'高見えレザーヘッドレストフック':(154885,25645,916),
'姿勢サポートチェア':(153646,73146,1876),'クリアビューレインガードフィルム':(107502,25674,1079),
'ナノバブルシャワーヘッド':(59819,36674,880),'スマートノーズEMS美顔器v2':(47237,25597,547),
'ディスペンサー':(46419,11284,311),'3WAY着る電気ブランケット':(43470,7250,375),
'高見えレザードアポケット':(32026,7234,227),'携帯電動シェーバーv2':(29535,13268,254),
'防風あったか裏起毛パンツ':(26756,9662,376),'快適マジックインソール v3':(21451,8898,181),
'360°マルチクリップ車載スマホホルダー':(17675,7671,232),'バランスケアスリッパ':(14122,6795,140),
'2WAYシートボックス':(10563,3587,68),'ふわとろ高密度ブランケット':(10366,3684,60),
'シリコンホールド膝サポーター':(9280,4398,71),'コードレス毛玉クリーナー':(7993,3061,55),
'高見えレザーヘッドレストフックv4':(6158,1088,40),'UV歯ブラシ除菌器':(5660,2031,50),
'健康サンダル':(5033,1946,36),'すき間収納シートポケット':(4911,957,31),
'ファスナー修理キット':(4492,1269,44),'高見えレザーヘッドレストフックv2':(4303,918,30),
'アーチフィット逆ヒールサンダル':(3922,910,15),'裏起毛タッチ防寒グローブ':(2695,905,30),
'快適マジックインソールv2':(17,2,0)}
MF = {}
for _k, _v in MF_RAW.items():
    _n = INV.get(_k, _k); _o = MF.get(_n, (0, 0, 0)); MF[_n] = tuple(a + b for a, b in zip(_o, _v))   # フックは旧＋v2 を足して1行

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
VEXG = {'防風あったか裏起毛パンツ': ({'S':3980,'M':3980,'L':3980,'XL':3980,'XL灰':3980,'XXL':3980}, {'S':1140,'M':1148,'L':1219,'XL':1233,'XL灰':1338,'XXL':1251}),
        'すき間収納シートポケット': ({'標準':3980,'赤':3980}, {'標準':760,'赤':956})}
VEXC = collections.defaultdict(float); _vg = collections.defaultdict(int)
for r_ in csv.DictReader(open('data/daily/daily_variant.csv')):
    if r_['name'] in VEXG:
        _p, _c = VEXG[r_['name']]
        VEXC[(r_['name'], r_['date'])] += int(r_['gross']) / _p[r_['cost_group']] * _c[r_['cost_group']]
        _vg[(r_['name'], r_['date'])] += int(r_['gross'])
for (_n, _d), _g in _vg.items(): assert Sd[_n][_d][0] == _g, (_n, _d, _g, Sd[_n][_d][0])   # バリアント合計 = 商品gross
for _n in VEXG:
    for _d in Sd[_n]: assert not Sd[_n][_d][0] or (_n, _d) in VEXC, (_n, _d)                 # 売れた日はすべてバリアント実測がある
def pricea(n, d):
    return 6980 if (n == 'スマートノーズEMS美顔器' and d >= '2026-11-14') else PRICEa[n]   # 11/14 16:51 値上げ（w1115.py の PRICEBYDATE と同じ）
def ucost(n, d):
    return 732 if (n == '高見えレザーヘッドレストフック' and d >= '2026-10-07') else COSTa[n]
ALLD = sorted({d for v in Sd.values() for d in v if d <= D1[0]})
D5 = ALLD[-5:]
def win(n, days):
    g = sum(Sd[n][d][0] for d in days if d in Sd[n]); dc = sum(Sd[n][d][1] for d in days if d in Sd[n])
    c = sum((VEXC[(n, d)] if n in VEXG else Sd[n][d][0] / pricea(n, d) * ucost(n, d)) for d in days if d in Sd[n]) if g and n in PRICEa and n in COSTa else 0
    a = sum(ADd[_c].get(d, 0) for _c in MULTI.get(n, (MAP.get(n, n),)) for d in days)
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
        if n in VEXG: c += VEXC[(n, d)]
        elif n in PRICEa and n in COSTa: c += g / pricea(n, d) * ucost(n, d)
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
                 round(ma) if ma else '', '',
                 '★昨日' if d == D1[0] else ''])
# 10月確定（10/31広告費の上書き後の最終値）と11月の滑り出し
AUG = [d for d in ALLD if '2026-10-01' <= d <= '2026-10-31']
assert len(AUG) == 31
_au = [dayblk(d) for d in AUG]
aus = sum(x[0] for x in _au); auc = sum(x[1] for x in _au); aua = sum(x[2] for x in _au); aup = aus-auc-aua
_cum = [dayblk(d) for d in CUM]
cs = sum(x[0] for x in _cum); cc = sum(x[1] for x in _cum); ca = sum(x[2] for x in _cum); cp = cs-cc-ca
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
sh('収益', [f'LOOTY 収益レポート 2026-11-18（昨日 = 11/17 火）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★11月累積（11/01〜・{len(CUM)}日）: 実売 {cs:,.0f} / 利益 {cp:,.0f}円（{cp/cs:.1%}）／1日あたり {cp/len(CUM):,.0f}円（10月確定は {aup:,.0f}円・{aup/31:,.0f}円/日）',
  '★11/17(火)は 実売 **314,364円**・利益 **+35,371円（11.3%）**・MER 1.61・倍率1.18（15日で15位＝最下位）。広告費は195,748円（暫定）で前日185,255円（確定）から+5.7%。祝日でない火曜の平均（実売461,518円・利益113,877円）比 実売−31.9%・利益−78,506円、前週火11/10（実売365,233円）比−13.9%。偶然か: MER 1.61・倍率1.18 とも**偶然でも起きるが端（下）**（1日目。3日続けば本物とみる）。外れた要素は購入率だけ（2.37%・ふだん2.55〜3.26%・−18%）。CPM・クリック率・来訪÷クリック・客単価は範囲内',
  '★注文60件・セッション2,534（前週火2,260・前日2,418）・CVR **2.37%**（前週火3.32%・前日3.14%・ふだんの範囲の下の外）・カゴ投入率**4.66%**（118/2,534・過去30日で最低）・決済完了 60/107＝56.1%（中央値54.7%・平常）',
  '★3日平均の利益 **93,905円/日**（11/15 +120,962・11/16 +125,381・11/17 +35,371）。数字として載せるだけ（ブレーキは11/12に廃止）',
  '🔁 11/17（ユーザー）: 00時台 ノーズ v2 12,000→16,000・インソール v3 8,000→12,000・シェーバー v2 11,000→8,000・洗車ブラシ 12,000→9,000（一覧は9,600）・ガラス sabu 19,000→22,000（一覧は22,800）→ 10時台 ブランケット広告A のショップ オフ（商品の拡張 OFF→ON）→ 18時台 新商品 裏起毛タッチ防寒グローブ 8,000（夜から配信）／マルチクリップ 8,000→10,000（時刻は未確認・11/18 00時台に検知・一覧にない変更）',
  '✅ 本日（11/18 水）の判定（11/17 終日の数字）: ⬇ ガラス sabu 22,000→19,000（4-2: 上げた11/17が1.19）／⬇ W固定 主力10,000→8,000・-sab 13,000→10,400（2: 11/16 0.88・11/17 0.97）／⬇ ブランケット 10,000→8,000（2: 0.44・0.69）／⬆ マルチクリップ 10,000→14,000（3-A: 前日1.88・通算1.86・消化114%）／⬆ ナノ 18,000→21,600・ドア 9,600→11,520・4-in-1 8,000→9,600（3-B）',
  '✅ 11/16広告費を確定上書き: 184,018→**185,255円**（+1,237）→ 11/16利益 +126,618→**+125,381円**に確定。11/17分195,748円は暫定（11/18 00時台の取得・時間別では195,902円）・次回確定',
  '原価は日次のバリアント構成が取れないナノガラス/壁掛けディスペンサーのみ30日実測ミックスの加重平均単価【近似】。'
  '期間別サマリー（次シート）はバリアント別実数量の正確値'],
 ['日付','曜','実売','原価','広告費','利益','利益率','手数料後利益','MER','3日移動平均利益','（ブレーキ欄は11/12廃止）','備考'],
 PROF, [12,5,13,12,12,13,9,14,8,16,9,10],
 {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'#,##0',9:'0.00',10:'#,##0'})

# ---------- 1 シンプル判定 ----------
def blk(n, N, K, A_):
    s = N.get(n, 0); k = K.get(n, 0); a = A_.get(n, 0); return s, k, a, s - k - a
# --- 予算アクション用: 最新スナップショット（同日の追記 b/c を含む）と最終変更日 ---
_keys = sorted({r[0] for r in body})
LATEST = max(k for k in _keys if k[:10] == SNAP[:10])
BUDL = collections.defaultdict(int)
for r in body:
    if r[0] == LATEST: BUDL[r[1]] += int(r[3])
_BK = collections.defaultdict(lambda: collections.defaultdict(int))
for _k in _STK:
    for (_c, _a), _v in _STK[_k].items(): _BK[_k][_c] += _v   # 積み上げた状態（キャンペーン合計）
def last_change(cp):
    """予算が最後に変わったスナップショットの日付（その日を変更後の初日とする＝実験P2の慣行と同じ）"""
    ch, prev = None, None
    for k in _keys:
        v = _BK[k].get(cp, 0)
        if prev is not None and v != prev and v: ch = k[:10]   # 再開（0→予算あり）も変更として扱う
        prev = v
    return ch
# 宣言済みの判定日（decisions.md の判定カレンダー）。判定日前は動かさない
CAL = {'伸縮ガラスクリーナー': ('2026-11-18', '📌⬇ sabu 22,000→19,000（4-2: 上げた11/17が1.19≦1.25 → 上げる前に戻す）｜11/17 15個（11注文）・倍率1.19・+6,526円（11/16 2.18）。注文11は期待18.3に対して少ない側の端（4.7%）。入口ページの購入 9／期待16.5（3%）・カート 22／30.2。Meta購入は主力A 8・sabu 2・B 0。7日1.69・+158,078円。次に動かすのは11/20から'),
       'W固定スマホ車載ホルダー': ('2026-11-18', '📌⬇ 主力 10,000→8,000・-sab 13,000→10,400（基準2: 11/16 0.88・11/17 0.97）｜11/17 9個（7注文）・−861円。注文7は期待11.4に対して少ない側の端（11.9%）。7日1.29。次は11/20'),
       '壁掛けディスペンサー': ('2026-10-24', '📌停止（10/24判定）｜再開後7日(10/17-23)倍率0.98<1.25 → 宣言どおり停止（14個・−1,102円・返品0）。ユーザーがMetaで停止'),
       '4-in-1マルチクリーナー': ('2026-11-18', '📌⬆ 8,000→9,600（3-B: 7日1.70・消化100%・前回11/11）｜11/17 2個・倍率1.01（11/16 4.89）。4-2: 11/18終日が1.25以下なら8,000に戻す'),
       'ポータブルヒートシーラー': ('2026-11-10', '11/10 00:29 停止（ユーザー）。7日1.15・30日1.48。11/10の広告費7円は停止直後の残り'),
       '高見えレザーヘッドレストフック': ('2026-11-16', '11/16 v2→v3（承認後も配信0・理由は未確認）→v4（昼から配信・6,136円・0個）→ 22時台にユーザーが停止。11/15〜16の通算 3個・倍率0.86・−1,491円。基準（事故停止9,744円・2日目のクリック率）には当たっていなかった＝一覧にない変更'),
       'ナノバブルシャワーヘッド': ('2026-10-26', '10/26 00:19 ユーザーが停止（先週倍率1.45・+24,768円）。再開はいつでも可'),
       'コードレスダブルミスト加湿器': ('2026-11-12', '11/12 00時台停止。11/12 に2個売れたが、ワイド水切りワイパーの広告から来訪（広告なしの売上）。通算0.98＝復活させない'),
       '高見えレザードアポケット': ('2026-10-29', '10/24 2日目判定: CTR3.09%＝延長も停止もしない帯。ユーザーが11,000へ増額済み。10/22-24 12個・倍率1.47・+11,588円（10/24は着地75・カート0・0個。実ブラウザでカート追加は正常）。10/29: 7日(10/22-28)の利益≥0で継続'),
       '伸縮ワックス洗車ブラシ': ('2026-11-20', '11/17 0個・−7,583円（11/16 0.99）。2日続けて1.25未満だが11/17に12,000→9,000（一覧は9,600）にしたので基準4で11/20から。Meta が11/17に配信をほぼ全部 広告Bへ（B のクリック率2.27%・A は3.5〜4.5%）。来訪40（ふだん1日160前後）。7日0.97・3日0.81'),
       'バランスケアスリッパ': ('2026-11-12', '11/12 10時台 再開8,000 → 22時台 停止（ユーザー）。4,286円・クリック30（1.6%）・カート0・0個。事故停止11,028円と2日目判定の前'),
       'ナノガラス脱毛パッド': ('2026-11-18', '📌⬆ 18,000→21,600（3-B: 7日1.83・消化100%・前回11/14）｜11/17 10個・倍率1.70・+12,603円。入口ページのカート率 3.1%（ふだん4.8%）は月ごとに下がっている（6月7.9%→10月6.0%→11月4.9%）。クリック率は下がっていない（動画を足す基準に当たらない）。4-2: 11/18終日が1.25以下なら18,000に戻す'),
       '姿勢サポートチェア': ('2026-11-11', '11/11 20:28 停止（ユーザー）。11/8 0.78・11/9 0.51・11/10 1.05・11/11 0個（広告6,986円）。7日(11/5-11)1.00・+98円・14日1.26・30日1.28'),
       '2WAYシートボックス': ('2026-11-11', '11/11 00:24 再開8,000 → 09:48 停止（ユーザー）。4,871円・1個（粗利3,433円・倍率0.70）。再開の判定は取りやめ'),
       'マグネットドアクッション': ('2026-11-18', '📌⬆ 9,600→11,520（3-B: 7日1.86・消化99%・前回11/15）｜11/17 5個・倍率1.80・+7,544円。動画を足す基準（ゆっくり: 直近7日のクリック率4.43%←前14日4.96%・−11%）に当たる。広告Bは11/15から配信0→足すなら新しい動画で C。4-2: 11/18終日が1.25以下なら9,600に戻す'),
       'ふわとろ高密度ブランケット': ('2026-11-01', '11/1 21:20頃 ユーザーが停止。2日 10,366円・カート0・購入0'),
       'ファスナー修理キット': ('2026-11-03', '11/3 11:30出稿8,000 → 〜22:59 ユーザーが停止。初日確定 4,476円・表示1,265・CTR3.48%・1個（倍率0.78）'),
       'コードレス毛玉クリーナー': ('2026-11-05', '11/5 01:10 キャンペーン停止（ユーザー）。再開後 4,210円（11/4 3,979・11/5 231）・広告経由0個（11/5に停止中で1個売れた）'),
       'ワイド水切りワイパー': ('2026-11-20', '11/17 8個・倍率1.28・+5,075円（11/16 0.89）。7日1.41・消化91%。上げの1.5に届かず、2日続けての1.25未満でもない＝据え置き。広告Bが100%'),
       'クリアビューレインガードフィルム': ('2026-11-12', '11/12 09時台 12,000→10,000・11時台 元のセット停止・コピー5,000・19時台 キャンペーン停止（ユーザー）。11/12 7,518円・0個。7日(11/6-12)2.07・+114,184円。休ませてからの再開の候補'),
       'シリコンホールド膝サポーター': ('2026-11-09', '11/9 20時台にキャンペーン停止（11/10 00時台の直読で判明・操作したのはユーザーと思われるが未確認）。2日（11/8-9）: 広告9,277円・表示4,396・クリック71（CTR1.62%）・Metaカート4・Shopify 1個・利益−5,883円。2日目の停止基準（CTR<2.5%かつカート0）はカート4で厳密には未該当'),
       'アーチフィット逆ヒールサンダル': ('2026-11-11', '11/11 00:15 停止（ユーザー）。配信2日で3,913円・表示909・0個。11/12の2日目判定は取りやめ'),
       '防風あったか裏起毛パンツ': ('2026-11-15', '11/15 00:3x キャンペーン停止（ユーザー・基準は−20%）。出してから4日の通算 12個・倍率1.11・+3,071円'),
       'すき間収納シートポケット': ('2026-11-12', '11/12 10時ごろ停止（ユーザー）。11/11-12 通算4,911円・1個・倍率0.66。2日目判定の前'),
       'UV歯ブラシ除菌器': ('2026-11-12', '11/12 09時台 再開10,000 → 14時台 広告B追加 → 22時台 停止（ユーザー）。5,651円・クリック52・カート0・0個。事故停止17,220円と2日目判定の前'),
       '3WAY着る電気ブランケット': ('2026-11-18', '📌⬇ 10,000→8,000（基準2: 11/16 0.44・11/17 0.69）｜11/13出稿。11/17 2個・−3,431円。通算(5日)16個・1.26・+11,499円。11/17 10時台にショップ オフ（判定は11/20朝・予算を下げたので量が変わる点に注意）。7日は11/20朝'),
       'スマートノーズEMS美顔器': ('2026-11-20', '4-2: 上げた11/17が1.45＞1.25＝据え置き。11/17 6個・+8,429円・消化117%。通算(4日)1.92・+43,303円。3-A（前日1.86以上）には届かない。3-B は11/20から。7日は11/21朝'),
       '携帯電動シェーバー': ('2026-11-20', '11/17 3個・倍率1.14・+1,182円（11/16 0.63）。2日続けて1.25未満だが11/17に11,000→8,000にしたので基準4で11/20から。通算(4日)1.21・+6,086円。7日は11/21朝'),
       '360°マルチクリップ車載スマホホルダー': ('2026-11-18', '📌⬆ 10,000→14,000（3-A: 前日1.88・通算1.86・消化114%）｜11/17 ユーザーが8,000→10,000（一覧にない変更・時刻は未確認）。11/17 7個・+10,050円。2日目のクリック率3.02%（2.5〜4.5%＝継続）。7日は11/23朝。4-2: 11/18終日が1.25以下なら10,000に戻す'),
       '裏起毛タッチ防寒グローブ': ('2026-11-19', '11/17 18時台に新商品（8,000・広告A・審査後に夜から配信）。1日目 2,682円・0個・クリック率3.35%（30/896）。分岐の売上÷広告費1.24。2日目のクリック率は11/19朝（11/18終日）・7日は11/24朝・事故停止の線 9,606円'),
       'むくみ取りかっさ': ('2026-10-21', '10/21判定済み: 再開後7日(10/14-20)倍率1.18 <1.25 → 停止。Metaは10/16から配信なし＝再開しない（期間利益+4,520円）'),
       '快適マジックインソール': ('2026-11-20', '4-2: 上げた11/17が1.40＞1.25＝据え置き。11/17 6個（4注文）・+5,218円。2日目のクリック率1.94%（2.5%未満だがカートあり＝止めない）。2日通算3.01・+43,502円。7日は11/23朝（旧の最後の7日1.54と比べる）'),}
TODAY = SNAP[:10]
# ===== 予算判断ルール（2026-10-20ユーザーと合意。タブ「予算ルール」・SKILL.md「予算判断の基本ルール」が正）=====
NEWRULE_FROM = '2026-10-20'   # 宣言済みの判定（CAL）が優先。それ以外の商品はこの日から週次ルールで表示
import os
_NR_TEST = os.environ.get('NEWRULE_TEST') == '1'   # 検証用: 月曜扱いで新ルールを当てる
_d1 = datetime.date.fromisoformat(R['D1'][0])
_lsun = _d1 - datetime.timedelta(days=(_d1.weekday() + 1) % 7)
LW = [(_lsun - datetime.timedelta(days=6 - i)).isoformat() for i in range(7)]    # 先週の月〜日
PW = [(_lsun - datetime.timedelta(days=13 - i)).isoformat() for i in range(7)]   # その前の週
_td = datetime.date.fromisoformat(TODAY)
IS_MON = _td.weekday() == 0 or _NR_TEST
NEXT_MON = TODAY if _td.weekday() == 0 else (_td + datetime.timedelta(days=7 - _td.weekday())).isoformat()
_md = lambda d: d[5:].replace('-', '/')
def _rt(n, days):
    s, c, a = win(n, days); return ((s - c) / a if a else None), s - c - a, a, s - c
def weekly_rule(n, cp, small, chg):
    rw, pw_, aw, gw = _rt(n, LW); _, pp, _, _ = _rt(n, PW)
    bw = sum(BSNAP[cp].get(d, 0) for d in LW); uw = aw / bw if bw else None
    basis = f'先週の月〜日（{_md(LW[0])}〜{_md(LW[-1])}）'
    if rw is None: return '—', '先週の広告費なし', None, basis
    head = f'先週 倍率{rw:.2f}・利益{pw_:+,.0f}円' + (f'・予算消化{uw:.0%}' if uw else '')
    if not IS_MON:
        return f'⏸次の判定 {_md(NEXT_MON)}(月)', head + '。火〜日は触らない（事故停止のみ例外）', rw, basis
    if chg and LW[0] <= chg <= LW[-1]:   # 先週中に予算を動かした → 答え合わせ
        _bp = BSNAP[cp].get((datetime.date.fromisoformat(chg) - datetime.timedelta(days=1)).isoformat())
        post_ = [d for d in LW if d >= chg]
        pre_ = [d for d in ALLD if d < chg][-7:]
        pre_ = [d for d in pre_ if BSNAP[cp].get(d) == _bp] or pre_
        _, _, ap, gp = _rt(n, post_); _, _, a0, g0 = _rt(n, pre_)
        da = ap / len(post_) - a0 / len(pre_); dg = gp / len(post_) - g0 / len(pre_)
        _src = f'{_md(chg)}変更。比較 {_md(pre_[0])}〜{_md(pre_[-1])} → {_md(post_[0])}〜{_md(post_[-1])}'
        if len(pre_) < 3 or len(post_) < 3: return '⏸そのまま（答え合わせ: 比べられる日が3日未満）', head + '。' + _src, rw, basis
        if abs(da) < 1000: return '⏸そのまま（答え合わせ: 差が小さく測れない）', head + '。' + _src, rw, basis
        inc = dg / da
        if da > 0: act = '✅答え合わせ合格 → 維持' if inc >= 1.0 else '↩答え合わせ不合格 → 元の予算へ戻す'
        else: act = '✅減らして正解 → 維持' if inc < 1.0 else '↩削りすぎ → 元の予算へ戻す'
        return act, head + f'。答え合わせ（{_src}）: 増減した粗利÷増減した広告費＝{inc:.2f}（1日あたり 広告{da:+,.0f}円・粗利{dg:+,.0f}円）', rw, basis
    if not small:
        if rw < 1.25: act = '🔻2〜3割減らす'
        elif rw < 1.43: act = '↘2割減らす'
        elif rw < 1.86: act = '⏸そのまま'
        elif uw is not None and uw >= 0.95: act = '⬆2割増やす'
        else: act = '⏸そのまま（予算を使い切れていない）'
        return act, head, rw, basis
    if pw_ < 0:
        return ('🔻停止（2週続けて赤字）' if pp < 0 else '⚠️注意（1週目の赤字）'), head + f'。その前の週の利益{pp:+,.0f}円', rw, basis
    if rw >= 1.86 and uw is not None and uw >= 0.95: return '⬆2割増やす（小さい商品の例外）', head, rw, basis
    return '⏸継続', head, rw, basis
SMALL = 10000
def band(r, wu, small):
    if r is None: return '—'
    if r < 1.25: return '🔻減額・停止'
    if r < 1.43: return '⏸据え置き（小予算・テストしない）' if small else '↘減額テスト（−20〜25%）'
    if r < 1.86: return '⏸据え置き（最適帯）'
    if wu is not None and wu >= 0.95: return '⬆増額テスト（+20〜25%）'
    return '⏸据え置き（倍率は高いが予算を使い切れていない）'

SIMPLE = []; ACT = []
NAMES7 = sorted(set(R['N7']) | {n for n, v in R['A7'].items() if v > 0}, key=lambda x: (-R['N7'].get(x, 0), -R['A7'].get(x, 0)))
for n in NAMES7:
    a7 = R['A7'].get(n, 0)
    if not a7: continue
    s7, k7, _, p7 = blk(n, R['N7'], R['K7'], R['A7'])
    if not s7:
        _cur = BUDL.get(BNAME.get(n, MAP.get(n, n))); _a1 = R['A1'].get(n, 0); _a3 = R['A3'].get(n, 0)
        _act = '⛔停止中（販売0）' if not _cur else '🆕新商品・学習中（販売0）'
        _memo = CAL.get(n, ('', ''))[1] or ('売上0のまま停止' if not _cur else '購入0のまま分岐CPA×3を消化したら事故停止')
        ACT.append(_act)
        SIMPLE.append([n, _cur if _cur else '停止中', _act, 0, '7日', 0, 0 if _a3 else '', 0 if _a1 else '', _memo,
            0, 0 if _a3 else '', 0 if _a1 else '', '', '', round(p7), round(-_a3), round(-_a1), '', '', '', '🚨縮小・停止', ''])
        continue
    s3, k3, a3, p3 = blk(n, R['N3'], R['K3'], R['A3']); s1, k1, a1, p1 = blk(n, R['N1'], R['K1'], R['A1'])
    gm = 1 - k7 / s7; be = 1 / gm; tg = 1 / (gm - 0.35) if gm - 0.35 > 0 else None; mer = s7 / a7
    cp = MAP.get(n, n); bcp = BNAME.get(n, cp); days = [d for d in D7 if d in BSNAP[bcp]]
    wu = (a7 / sum(BSNAP[bcp][d] for d in days)) if len(days) == 7 and sum(BSNAP[bcp][d] for d in days) else None
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
    # --- 倍率（MER÷分岐）と予算アクション ---
    r7 = mer / be; r3 = (s3 / a3) / be if a3 else None; r1 = (s1 / a1) / be if a1 else None
    cur = BUDL.get(bcp); small = bool(cur) and cur <= SMALL
    first_ad = min((d for d, v in ADd[cp].items() if v > 0), default=None)
    chg = last_change(bcp)
    post = [d for d in ALLD if chg and d >= chg]
    if chg and chg > D7[0]:
        if post:
            sp, cp_, ap = win(n, post); rj = (sp / ap) / be if ap else None
            basis = f'変更後{len(post)}日（{chg[5:].replace("-", "/")}〜）'
        else:
            rj, basis = r7, f'7日（{chg[5:].replace("-", "/")} 変更後の実績はまだ無い）'
    else:
        rj, basis = r7, '7日'
    if not cur:
        act, memo, rj, basis = '⛔停止中', '予算ゼロ（停止済み）', None, '—'
    elif first_ad and first_ad > D7[0] and not (n in CAL and CAL[n][0] == TODAY and CAL[n][1].startswith('📌')):
        act, memo = '🆕新商品・学習中（触らない）', CAL.get(n, ('', '購入50件まで判定保留'))[1]
    elif n in CAL and CAL[n][0] == TODAY and CAL[n][1].startswith(('10/19判定済み',)):
        act, memo = '📌本日判定 → 継続（12,000のまま）', CAL[n][1] + f'。参考: 倍率だけで見た帯＝{band(rj, wu, small)}'
    elif n in CAL and CAL[n][0] == TODAY and CAL[n][1].startswith(('10/17判定済み',)):
        act, memo = '📌本日判定 → 減額のまま（合格）', CAL[n][1] + f'。参考: 倍率だけで見た帯＝{band(rj, wu, small)}'
    elif n in CAL and CAL[n][0] == TODAY and CAL[n][1].startswith(('10/16判定済み',)):
        act, memo = '📌8,000へ戻す（10/16判定・未実施）', CAL[n][1] + f'。参考: 倍率だけで見た帯＝{band(rj, wu, small)}'
    elif n in CAL and CAL[n][0] == TODAY and CAL[n][1].startswith('📌'):
        act, memo = CAL[n][1].split('｜')[0], CAL[n][1].split('｜', 1)[1] + f'。参考: 倍率だけで見た帯＝{band(rj, wu, small)}'
    elif n in CAL and CAL[n][0] > TODAY:
        act, memo = f'⏳判定待ち（{CAL[n][0][5:].replace("-", "/")}）', CAL[n][1] + f'。参考: いまの帯＝{band(rj, wu, small)}' + ('（変更後の日数が少ない・参考値）' if basis != '7日' and len(post) < 3 else '')
    elif chg and chg > D7[0] and len(post) < 3 and TODAY < NEWRULE_FROM:
        _j = (datetime.date.fromisoformat(chg) + datetime.timedelta(days=3)).isoformat()
        act, memo = f'⏳変更直後・据え置き（{_j[5:].replace("-", "/")}判定）', f'変更後のデータが{len(post)}日分しかない。参考: いまの帯＝{band(rj, wu, small)}'
    elif TODAY >= NEWRULE_FROM or _NR_TEST:
        act, memo, rj, basis = weekly_rule(n, bcp, small, chg)
    else:
        act = band(rj, wu, small)
        memo = '小予算: 倍率<1.25になったら減額・停止' if small and rj is not None and rj >= 1.25 else ''
        if rj is not None and r3 is not None and r3 < 1.25 <= rj: memo = (memo + '／' if memo else '') + '⚠️3日倍率が1.25割れ・次回要注意'
        if act.startswith('🔻'): memo = '小予算 → 停止を提案（ユーザー判断）' if small else '−25%減額か停止（ユーザー判断）'
    ACT.append(act)
    SIMPLE.append([n, cur if cur else '停止中', act, round(rj, 2) if rj is not None else '', basis,
        round(r7, 2), round(r3, 2) if r3 is not None else '', round(r1, 2) if r1 is not None else '', memo,
        round(mer, 2), round(s3 / a3, 2) if a3 else '', round(s1 / a1, 2) if a1 else '',
        round(be, 2), round(tg, 2) if tg else '', round(p7), round(p3), round(p1),
        round(wu, 3) if wu else '', round(per, 3), rob, st, tri])
NC = len(SIMPLE[0])
_shown = {BNAME.get(r[0], MAP.get(r[0], r[0])) for r in SIMPLE}
for _cp in sorted(BUDL, key=lambda c: -BUDL[c]):
    if _cp not in _shown: SIMPLE.append([_cp + ('　※全商品横断' if 'カタログ' in _cp else ''), BUDL[_cp]] + ['—'] * (NC - 2))
assert sum(r[1] for r in SIMPLE if isinstance(r[1], int)) == sum(BUDL.values())
SIMPLE.append(['合計（Meta日予算）', sum(BUDL.values())] + [''] * (NC - 2))
_ws = sh('シンプル判定', [f'LOOTY {SNAP} 定例（昨日={D1[0][5:].replace("-", "/")}）',
 '■ 予算をどうするかは「予算アクション」列だけ見ればよい。根拠は「判断倍率」（倍率 = MER ÷ 分岐MER。1.00で広告費トントン）',
 '■ 倍率の帯: 1.25未満=🔻減額・停止 ／ 1.25〜1.43=↘減額テスト ／ 1.43〜1.86=⏸据え置き（最適帯） ／ 1.86以上かつ週消化率95%以上=⬆増額テスト（+20〜25%）',
 '　なぜ1.43: 追加で使った広告費の効き（限界MER）は平均MERの約0.7倍（8/6実測）。1.43×0.7=1.00＝最後の1円がトントンになる線。1.25〜1.67は前提0.6〜0.8次第で黒字にも赤字にもなる「符号割れ」帯',
 '■ 2026-10-20から判断ルールを変更（タブ「予算ルール」）: 日予算1万円超は毎週月曜に先週の月〜日の倍率で判定・火〜日は「次の判定日」を表示／1万円以下は2週続けて赤字で停止／判定日を宣言済みの商品はその基準',
 '■ 判断倍率は原則「7日倍率」。7日以内に予算を変えた商品は「変更後の日だけ」の倍率で見る（変更前の予算の成績で判断しない）',
 f'■ 例外: 予算{SMALL:,}円以下の小さい商品は効果が小さいのでテストしない（1.25未満で減額・停止だけ）／広告開始7日以内は新商品で触らない／判定日を宣言済みの商品はその日まで動かさない（⏳）',
 '■ 3日・前日倍率は監視用（単日で動かさない）。増額・減額の結果は判定日に増分MERで合否を出す',
 f'現日予算 = {LATEST} 時点のMeta日予算（広告セット合計）。最終行に全体合計 {sum(BUDL.values()):,}円'],
 ['商品','現日予算','予算アクション','判断倍率','判断に使った期間','7日倍率','3日倍率','前日倍率','次回判定・メモ',
  '7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','週消化率','1円あたり利益','頑健性','状態','3窓判定'],
 SIMPLE, [26,11,30,9,18,8,8,8,44,8,8,8,7,7,12,12,12,9,11,12,12,28],
 {2:'#,##0',4:'0.00',6:'0.00',7:'0.00',8:'0.00',15:'#,##0',16:'#,##0',17:'#,##0',18:'0.0%'})
_FILL = {'🔻': 'F8CBAD', '↘': 'FCE4D6', '⏸': 'E2EFDA', '⬆': 'C6EFCE', '⏳': 'FFF2CC', '🆕': 'DDEBF7', '⛔': 'D9D9D9'}
for _row in _ws.iter_rows(min_col=3, max_col=3):
    _c = _row[0]
    if isinstance(_c.value, str) and _c.value[:1] in _FILL:
        _c.fill = PatternFill('solid', fgColor=_FILL[_c.value[:1]]); _c.font = Font(name='Arial', size=10, bold=True)
for _row in _ws.iter_rows(min_col=4, max_col=4):
    if isinstance(_row[0].value, float): _row[0].font = Font(name='Arial', size=10, bold=True)

# ---------- 2 ネクストアクション ----------
NA = [
 ['📊 11/17(火)','実売 **314,364円**・利益 **+35,371円（11.3%）**・MER1.61・倍率1.18',
  'MER・倍率とも偶然でも起きるが端（下・1日目）。外れたのは購入率だけ（−18%）。下がったのは商品ページ→カート（4.66%・30日で最低）で、最大はガラスのページ','—','監視'],
 ['⬇️ 今日下げるもの','ガラス sabu 22,000→19,000／W固定 10,000→8,000・13,000→10,400／ブランケット 10,000→8,000',
  '4-2（ガラス: 上げた11/17が1.19）・基準2（W固定: 0.88・0.97／ブランケット: 0.44・0.69）','ユーザー','11/20'],
 ['⬆️ 今日上げるもの','マルチクリップ 10,000→14,000／ナノ 18,000→21,600／ドア 9,600→11,520／4-in-1 8,000→9,600',
  '3-A（マルチクリップ: 前日1.88・通算1.86・消化114%）・3-B（ナノ 7日1.83・ドア1.86・4-in-1 1.70・消化99〜100%）','ユーザー','11/19（4-2）'],
 ['⏸ 動かさないもの','ノーズ・インソール v3・洗車ブラシ・シェーバー・ワイパー・グローブ・カタログ',
  'ノーズ・インソールは4-2を通過（1.45・1.40）。ブラシ・シェーバーは2日続けて1.25未満だが11/17に動かしたので11/20から','—','11/20'],
 ['🎬 動画を足すもの','ドア（ゆっくりした落ち込み −11%）',
  '広告Bは11/15から配信0。足すなら新しい動画で C（動画以外はAと同じ）','ユーザー','—'],
 ['🆕 新商品','グローブ 1日目（夜だけ・2,682円・0個）／マルチクリップ 2日目 クリック率3.02%＝継続',
  '事故停止の線 9,606円（購入0のとき）。グローブの2日目は11/19朝','—','11/19'],
 ['📈 3日平均の利益','93,905円/日',
  '数字として載せるだけ（ブレーキは廃止）','—','—'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 2a 予算ルール（常設・2026-10-20ユーザーと合意）----------
BR_RULE = [
 ['物差し','倍率 ＝（売上 − 原価）÷ 広告費。1.0未満は赤字','Shopifyの実売・原価・Metaの広告費の実測だけで計算する'],
 ['1. いつ決めるか','終日の数字だけで決める。日中の数字では提案しない','日中は購入が遅れて積み上がり、比率が悪い方へ歪む（8/28の誤読）'],
 ['2. 下げる','2日続けて倍率1.25未満 → −20%。1回2割まで','10/20〜11/8 の45件: 2割までの下げは18件中12件で利益が増え、2割超の下げは12件中4件だった（pace_1515.py）'],
 ['3-A. 上げる（出して10日以内）','前日の終日の倍率1.86以上・出してからの通算1.86以上・予算を95%以上使った → +4,000円まで。毎日上げてよい','当たりの利益は出して2〜8日目に集中（ramp_1535.py）'],
 ['3-B. 上げる（それ以外）','7日の倍率1.5以上（店全体の平均以上）かつ消化95%以上 → +20%。次に上げるのは2日あけてから。直近2日が続けて1.25未満なら上げない（2を優先）','1.5は試行（2026-11-12）。11/26の答え合わせで 1.5〜1.86 で上げた分と 1.86以上で上げた分を分けて報告する'],
 ['4. 間隔','同じ商品は2日あける（上げも下げも。3-Aの増額だけ例外）','11/4〜11/12の9日で90回動かし、22商品中16商品を2日続けて・または1日2回動かしていた'],
 ['4-2. 上げたら確かめる','上げてから最初の終日の倍率が1.25以下なら、上げる前の予算に戻す。基準4の2日を待たない。戻したあと次に動かすのは2日あけてから','2026-11-15 ユーザー「予算を上げて1.25以下になったら戻す。効果が現れてないから」（最初の例: ワイパー 11/14 1.09 → 20,000）'],
 ['5. 新商品','8,000円で開始 → 2日目にクリック率（4.5%超で延長／2.5%未満かつカート0で停止）→ 7日で倍率1.25以上なら継続','最初の月のCTR4.5%以上11件は外れ0件／2.5%未満14件は外れ10件'],
 ['6. 事故停止','購入0のまま（売価−原価）×3 を使ったら停止','—'],
 ['7.（廃止）','合計19万円までのブレーキは使わない。3日平均の利益は毎朝の報告に数字として載せるだけ','2026-11-12 ユーザー「7はどうでもいい」'],
 ['実行','毎朝の報告の冒頭に「今日動かすもの／動かさないもの」を出す。実行はユーザー。基準を変えるときは理由とデータを添えて先に伝える','CLAUDE.md（2026-11-12）。答え合わせは 2026-11-26（木）の朝'],
]
_wr = sh('予算ルール', ['予算を動かす基準（2026-11-12 からClaudeが決めて毎朝「今日動かすもの」を出す・CLAUDE.md）。迷ったらこのタブだけ見ればよい',
  '★まとめ: ①終日の数字だけ ②下げは2日続けて1.25未満で−20% ③上げは10日以内なら前日1.86以上で+4,000まで／それ以外は7日1.5以上で+20% ④同じ商品は2日あける',
  '★新商品は「購入ゼロで（売価−原価）×3」「2日目のクリック率」「7日目の倍率1.25」の3段。旧ルール（毎週月曜に1回）は 11/12 に置き換え'],
   ['区分','ルール','なぜ（根拠）'], BR_RULE, [22, 90, 100])
for _row in _wr.iter_rows(min_row=6):
    for _c in _row: _c.alignment = Alignment(wrap_text=True, vertical='top')

# ---------- 2b 新商品リサーチ指針（常設・2026-10-17ユーザー指定）----------
RG = [
 ['1','効果が映像で一目で分かる（最重要）','実演性・高13件: 累計利益の中央値+126万・当たり以上11件・外れ0件／低16件: 中央値+0.6万・当たり0件・外れ11件','動画の最初の2秒で「効果」が見せられるか（水が吸われる・毛が取れる・風が出る等）'],
 ['2','悩みがはっきりしている','当たり: 暑い・ムダ毛・虫・足が疲れる・車でスマホが見にくい・窓が汚い','悩みを一言で言えるか'],
 ['3','安い代わりの品が身近にない','代わりなし27件: 中央値+58万／あり24件: 中央値+6万・外れ10件（手袋は見られたがクリックされなかった）','100均・ドラッグストアで代わりが買えないか'],
 ['4','需要が盛り上がる時期の入口で出す','夏物16件は外れ0件・計+3,321万。4〜5月開始が最大、7月開始は+18〜58万に縮む。冬物の保温プレートは1〜3月で+93万','山の1〜2か月前に出しているか（冬物は10月末〜11月頭）'],
 ['避ける','健康ガジェット・ケア小物・ファッション','14件で当たり0件・外れ10件（EMS・温熱カッサ・ネック・耳かき・足臭ブラシ・ヘアタオル・ワンピース・インナー・シェイプパンツ・手袋 等）','該当するなら原則出さない'],
 ['関係なし','売価・原価率','3,980〜8,990円のどの価格帯にも当たりがある（UV歯ブラシ8,980・保温プレート8,990）。原価率の帯ごとの差もない','—'],
 ['初動','出した後の見切り','最初の月のCTR4.5%以上11件は外れ0件／2.5%未満14件は外れ10件','最初の2日でCTR4.5%超→伸ばす／2.5%未満かつカート0→止める（例外: スリッパ・ムダ毛は購入率で稼ぐ型）'],
]
sh('新商品リサーチ指針', ['新商品を選ぶときの4条件（2026-10-17・全51商品の累計損益から。詳細は data/product-lifetime-2026-10-17.csv）',
  '★累計利益5,763万円のうち上位6商品で68%。新商品の当たり率を上げることが一番効く',
  '★条件1・3は結果を知ったあとに付けた判定のため、出稿前にチェックして結果と照らし合わせて確かめていく'],
   ['#','条件','根拠（実測）','確認のしかた'], RG, [8, 30, 78, 52])

# ---------- 3 全体サマリー ----------
SUMR = []
for lbl, N, K, ACC in [('前日 11/17(火)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/15-11/17', R['N3'], R['K3'], R['ACCT3']),
        ('7日 11/11-11/17', R['N7'], R['K7'], R['ACCT7']), ('30日 10/19-11/17', R['N30'], R['K30'], R['ACCT30']),
        ('11月 11/01-', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過（11/17）: Σ商品gross=全店323,120 ／ Σ値引=8,756 ／ Σ広告費=キャンペーン合算195,748円（00時台の暫定・時間別では195,902円）。11/16も gross 446,830・値引15,724 で一致・広告費は確定185,255円',
 '✅ 11/16の広告費は再取得で確定済み（184,018→**185,255円**。11/18に上書き）',
 '⚠️ 11/17の広告費は 11/18 00時台の取得【暫定】→ 次回に再取得して確認する',
 '★ガラスクリーナーの原価は保守側の最高値バリアント単価で計上。ヘッドレストフックは10/7以降のCJ原価732円で計上（11/3にproduct_tabsの1,344を訂正）',
 '★11/17の返品: なし（returns 0）。★5e-2突合: 広告なしで売れた商品はなし。Meta購入59 ÷ Shopify注文60 ＝ 98%',
 '決済ブレンド率 **3.325%**（2026-11-02再計測: 直近100注文・SP 91.2%×3.25%・KOMOJUスマホ決済7.8%・Paidy1.1%×4.1%。前回3.388%。次回12/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(11/17 火) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','11/17(火)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '11/17(火)は実売314,364円・利益+35,371円（11.3%）・MER1.61。黒字の上位はナノ10個（1.70・+12,603円）・マルチクリップ7個（1.88・+10,050円）・ノーズ6個（1.45・+8,429円）・ドア5個（1.80・+7,544円）・クリーナー15個（1.19・+6,526円）・インソール6個（1.40・+5,218円）・ワイパー8個（1.28・+5,075円）。赤字は洗車ブラシ（0個・−7,583円）・ブランケット2個（0.69・−3,431円）・グローブ（0個・−2,682円・配信初日の夜だけ）・W固定9個（0.97・−861円）・カタログ（−8,334円）').font = Font(name='Arial', size=10, color='CC0000')

# ---------- 4 商品別 ----------
P = []
for n in NAMES7:
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
sh('商品別', ['商品別（7日 11/11-11/17 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,246,147円（11/17分は暫定）',
  '当月累積利益は11月分（11/01〜・17日目）',
  '★電動眉シェーバーは10/1に停止（Phase1不合格）。7日窓に残る分は窓から抜けるまで表示',
  '★ムダ毛・電動かっさ(9/18停止)は7日窓から完全に抜けた（ムダ毛は無広告で3個=オーガニック）'],
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
    assert abs(_c - _v[0]) <= max(500, _v[0] * 0.002), (_k, _c, _v[0])   # 11/17 は CSV・ファネルとも 00時台の取得
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
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/19-11/17)」。他シートの7日窓と混ぜて読まないこと',
  'クリックは **アウトバウンドクリック**（data_query 実測・Asia/Tokyo）',
  '✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/19-11/17) が許容差以内で一致（コード内assert。11/17はCSVが00時台の暫定）。フックは旧・v2・v3・v4、インソールは旧・v2・v3 を足して1行',
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
        if g and n in PRICEa and n in COSTa: c += g/pricea(n, d)*COSTa[n]
    a = sum(ADd[cp].get(d, 0) for cp in ADd); pr[d] = (s, c, a, s-c-a)
DD = []
for j, d in enumerate(ALLD):
    if d < '2026-07-13': continue
    s, c, a, p = pr[d]; ma = sum(pr[x][3] for x in ALLD[j-2:j+1])/3
    DD.append([d, WDJ[datetime.date.fromisoformat(d).weekday()], round(s), round(c), round(a), round(p),
               round(p/s,4), round(s/a,2), round(ma), ''])
sh('日次推移', ['日次の利益は上記【近似】原価ベース。4期間サマリーはバリアント別実数量の正確値',
  '3日移動平均利益は数字として載せるだけ（合計19万円までのブレーキは 2026-11-12 に廃止・CLAUDE.md の基準7）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['11/18(水)','ガラス sabu（4-2）','上げた最初の終日が1.25以下なら戻す','11/17 1.19','**22,000→19,000**','11/20'],
 ['11/18(水)','W固定（基準2）','2日続けて1.25未満で−20%','11/16 0.88・11/17 0.97','**主力10,000→8,000・-sab 13,000→10,400**','11/20'],
 ['11/18(水)','ブランケット（基準2）','同上','11/16 0.44・11/17 0.69','**10,000→8,000**','11/20'],
 ['11/18(水)','マルチクリップ（3-A）','出して10日以内: 前日1.86以上・通算1.86以上・消化95%以上で+4,000','前日1.88・通算1.86・消化114%','**10,000→14,000**','11/19（4-2）'],
 ['11/18(水)','ナノ・ドア・4-in-1（3-B）','7日1.5以上・消化95%以上で+20%','7日 1.83・1.86・1.70／消化 100・99・100%','**18,000→21,600・9,600→11,520・8,000→9,600**','11/19（4-2）'],
 ['11/18(水)','ノーズ・インソール v3（4-2）','上げた最初の終日が1.25以下なら戻す','11/17 1.45・1.40','据え置き','11/20'],
 ['11/18(水)','洗車ブラシ・シェーバー（基準2）','2日続けて1.25未満で−20%（基準4: 2日あける）','ブラシ 0.99・0.00／シェーバー 0.63・1.14','11/17に動かしたので11/20から','11/20'],
 ['11/18(水)','動画を足す基準','直近3日が前7日より15%以上低い／直近7日が前14日より10%以上低い','ドア −11%（ゆっくり）','足すなら C','—'],
 ['11/19(木)','グローブ 2日目（基準5）／マルチクリップ・ナノ・ドア・4-in-1 の4-2','基準どおり','—','待機','—'],
 ['11/20(金)','ブランケット 7日・ショップ オフの判定／ブラシ・シェーバー・ノーズ・インソール・W固定・ガラス','基準どおり','—','待機','—'],
 ['11/21(土)','ノーズ・シェーバー 7日（11/14-20）','倍率1.25以上で継続','—','待機','—'],
 ['11/23(月)','インソール v3・マルチクリップ 7日（11/16-22）','倍率1.25以上で継続','—','待機','—'],
 ['11/26(木)','答え合わせ（11/13〜25）','基準どおり／一覧にない変更・動かしたあと2〜3日・1日あたりの利益','—','約束済み','—'],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日(11/18 水)動かすもの: ⬇ **ガラスクリーナー sabu 22,000→19,000**（4-2）／⬇ **W固定 主力 10,000→8,000・-sab 13,000→10,400**（基準2）／⬇ **ブランケット 10,000→8,000**（基準2）／⬆ **マルチクリップ 10,000→14,000**（3-A）／⬆ **ナノ 18,000→21,600**（3-B）／⬆ **ドア 9,600→11,520**（3-B）／⬆ **4-in-1 8,000→9,600**（3-B）。合計 197,600→199,120（+1,520）。動かさないもの: ノーズ（4-2: 1.45＞1.25）・インソール v3（4-2: 1.40）・洗車ブラシ・シェーバー（2日続けて1.25未満だが11/17に動かしたので基準4で11/20から）・ワイパー（7日1.41）・グローブ（新商品・2日目は11/19朝）・カタログ。動画を足すもの: ドア（ゆっくりした落ち込み −11%）。Bは11/15から配信0なので、足すなら新しい動画で C',
  '★次: 11/19(木) グローブ2日目／マルチクリップ・ナノ・ドア・4-in-1 の4-2 → 11/20(金) ブランケット7日・ショップ オフ判定／ブラシ・シェーバー・W固定・ガラス → 11/21(土) ノーズ・シェーバー7日 → 11/23(月) インソール v3・マルチクリップ7日 → 11/26(木) 答え合わせ',
  '★倍率の定義: **MER ÷ 分岐MER**。1.0未満＝赤字',
  '★10月確定: 31日で+4,174,310円（26.0%・134,655円/日）。11月は17日で+1,862,360円（109,551円/日）'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-11-17': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['前日(11/17 00時台・2026-11-17)スナップショット → 本日(11/18 00時台・2026-11-18)。変更（11/17・ユーザー）: ノーズ 12,000→16,000・インソール v3 8,000→12,000・シェーバー 11,000→8,000・ブラシ 12,000→9,000・ガラス sabu 19,000→22,000・マルチクリップ 8,000→10,000・グローブ 8,000（新商品）',
  '合計 182,600 → **197,600円/日**（+15,000。増: ノーズ+4,000・インソール+4,000・ガラス sabu+3,000・マルチクリップ+2,000・グローブ+8,000／減: シェーバー−3,000・ブラシ−3,000）。今日動かすものを実施すると 199,120円',
  '★体制: 16セット・197,600円/日（→ 今日の8件で199,120円）。合計19万円のブレーキは廃止',
  '★11/17の消化は 195,748円（暫定）。11/16は確定185,255円、11/15は確定181,491円。グローブは夜からの配信で2,682円（予算8,000の34%）',
  '★インソールは v3（新規キャンペーン）で12,000。フックは11/16に停止。ノーズ・シェーバーは v2。予算の記録は元の商品名で持つ'],
 ['商品/キャンペーン','変更前','変更後','差','変化率','7日MER','分岐','目標','7日余裕','3日MER','3日余裕',
  '倍率7日','倍率3日','消化率(7日)','1円あたり利益','頑健性','印'],
 BR, [26,10,10,9,9,8,7,7,9,8,9,9,9,12,13,14,7],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'+0.0%;-0.0%',14:'0.0%'})

# ---------- 10 CVR推移 ----------
SES = {'2026-08-04':6639,'2026-08-05':5425,'2026-08-06':5138,'2026-08-07':4827,'2026-08-08':5527,'2026-08-09':5886,
'2026-08-10':5245,'2026-08-11':6001,'2026-08-12':4900,'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,
'2026-08-16':5349,'2026-08-17':3438,'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,
'2026-08-22':3220,'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733,'2026-08-27':3145,
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936,'2026-09-02':3142,'2026-09-03':3340,'2026-09-04':3293,'2026-09-05':3217,'2026-09-06':3752,'2026-09-07':2787,'2026-09-08':2739,'2026-09-09':2801,'2026-09-10':3514,'2026-09-11':3014,'2026-09-12':3132,'2026-09-13':4246,'2026-09-14':3592,'2026-09-15':3358,'2026-09-16':3348,'2026-09-17':3418,'2026-09-18':3583,'2026-09-19':4088,'2026-09-20':4310,'2026-09-21':4571,'2026-09-22':3877,'2026-09-23':4043,'2026-09-24':3257,'2026-09-25':3236,'2026-09-26':4416,'2026-09-27':5017,'2026-09-28':3841,'2026-09-29':3426,'2026-09-30':3276,'2026-10-01':4124,'2026-10-02':3619,'2026-10-03':3578,'2026-10-04':4506,'2026-10-05':3394,'2026-10-06':3904,'2026-10-07':3692,'2026-10-08':3530,'2026-10-09':3218,'2026-10-10':3685,'2026-10-11':3163,'2026-10-12':3794,'2026-10-13':3140,'2026-10-14':3501,'2026-10-15':3231,'2026-10-16':2914,'2026-10-17':3529,'2026-10-18':3863,'2026-10-19':3094,'2026-10-20':3176,'2026-10-21':3223,'2026-10-22':3470,'2026-10-23':3054,'2026-10-24':3560,'2026-10-25':4375,'2026-10-26':3923,'2026-10-27':3198,'2026-10-28':3703,'2026-10-29':3259,'2026-10-30':2651,'2026-10-31':2660,'2026-11-01':2916,'2026-11-02':2801,'2026-11-03':3359,'2026-11-04':2387,'2026-11-05':2874,'2026-11-06':2756,'2026-11-07':3260,'2026-11-08':3741,'2026-11-09':2936,'2026-11-10':2260,'2026-11-11':2307,'2026-11-12':2434,'2026-11-13':2323,'2026-11-14':2570,'2026-11-15':2607,'2026-11-16':2418,'2026-11-17':2534}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88,'2026-09-02':92,'2026-09-03':103,'2026-09-04':74,'2026-09-05':106,'2026-09-06':122,'2026-09-07':96,'2026-09-08':95,'2026-09-09':98,'2026-09-10':116,'2026-09-11':96,'2026-09-12':117,'2026-09-13':140,'2026-09-14':102,'2026-09-15':103,'2026-09-16':99,'2026-09-17':100,'2026-09-18':96,'2026-09-19':122,'2026-09-20':135,'2026-09-21':150,'2026-09-22':117,'2026-09-23':128,'2026-09-24':107,'2026-09-25':102,'2026-09-26':142,'2026-09-27':156,'2026-09-28':117,'2026-09-29':96,'2026-09-30':110,'2026-10-01':141,'2026-10-02':113,'2026-10-03':111,'2026-10-04':129,'2026-10-05':102,'2026-10-06':124,'2026-10-07':100,'2026-10-08':92,'2026-10-09':85,'2026-10-10':127,'2026-10-11':112,'2026-10-12':114,'2026-10-13':100,'2026-10-14':91,'2026-10-15':100,'2026-10-16':85,'2026-10-17':114,'2026-10-18':108,'2026-10-19':93,'2026-10-20':76,'2026-10-21':104,'2026-10-22':112,'2026-10-23':102,'2026-10-24':105,'2026-10-25':125,'2026-10-26':95,'2026-10-27':94,'2026-10-28':83,'2026-10-29':84,'2026-10-30':72,'2026-10-31':70,'2026-11-01':112,'2026-11-02':75,'2026-11-03':88,'2026-11-04':70,'2026-11-05':80,'2026-11-06':98,'2026-11-07':94,'2026-11-08':114,'2026-11-09':79,'2026-11-10':75,'2026-11-11':72,'2026-11-12':68,'2026-11-13':58,'2026-11-14':64,'2026-11-15':76,'2026-11-16':76,'2026-11-17':60}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       ('★昨日（火曜・CVR 2.37%・注文60件・客単価5,239円・7,000円以上20%）' if d == '2026-11-17' else '（月曜・CVR 3.14%・注文76件・客単価5,672円・7,000円以上25%）' if d == '2026-11-16' else '（日曜・CVR 2.92%・注文76件・客単価5,561円・7,000円以上26%）' if d == '2026-11-15' else '（土曜・CVR 2.49%・注文64件・決済完了45.7%は15日で最低）' if d == '2026-11-14' else '（金曜・CVR 2.50%・注文58件）' if d == '2026-11-13' else '（木曜・CVR 2.79%・注文68件・6〜17時台が弱く18〜23時台は−14%）' if d == '2026-11-12' else '（水曜・CVR 3.12%・注文72件・客単価4,697円は16日で最低・18〜23時台が弱い）' if d == '2026-11-11' else '（火曜・CVR 3.32%・注文75件・来訪は16日で最少・18〜23時台は平常）' if d == '2026-11-10' else '（月曜・CVR 2.69%・注文79件・14〜17時台が弱く18〜23時台は平常）' if d == '2026-11-09' else '（日曜・CVR 3.05%・注文114件・6〜9時台が強い）' if d == '2026-11-08' else '（土曜・CVR 2.88%・注文94件・10〜13時台が強い）' if d == '2026-11-07' else '（金曜・CVR 3.56%・注文98件・朝と夜が強い）' if d == '2026-11-06' else '（木曜・CVR 2.78%・注文80件・10〜13時台が強い）' if d == '2026-11-05' else '（水曜・CVR 2.93%・注文70件・来訪は16日で最少だが来訪後は強い）' if d == '2026-11-04' else '（火曜・文化の日・CVR 2.62%・注文88件・来訪は多いがカゴ投入率が下端）' if d == '2026-11-03' else '（月曜・CVR 2.68%・注文75件・来訪が少ない＋13〜15時台の穴）' if d == '2026-11-02' else '（日曜・CVR 3.84%・注文112件・来訪後の割合が15日で最高）' if d == '2026-11-01' else '（土曜・CVR 2.63%・注文70件・来訪が少ない）' if d == '2026-10-31' else '（金曜・CVR 2.72%・注文72件だが客単価6,191円）' if d == '2026-10-30' else '（木曜・CVR 2.58%・ナノの購入率が08時から低下）' if d == '2026-10-29' else '（水曜・CVR 2.24%・表示が15日最低）' if d == '2026-10-28' else '（火曜・CVR 2.94%・朝の配信不足）' if d == '2026-10-27' else '（月曜・CVR 2.42%・20時以降に急落）' if d == '2026-10-26' else '（土曜・CVR 2.95%・ナノBC約7.5時間停止）' if d == '2026-10-24' else '（金曜・CVR 3.34%・洗車ブラシ新規）' if d == '2026-10-23' else '（木曜・CVR 3.23%・ドアポケット新規）' if d == '2026-10-22' else '（水曜・CVR 3.23%・前日から全面回復）' if d == '2026-10-21' else '（火曜・CVR 2.39%・81日で実売最低）' if d == '2026-10-20' else '（月曜・CVR 3.01%・プライム感謝祭最終日）' if d == '2026-10-19' else '（日曜・CVR 2.80%・プライム感謝祭本番3日目）' if d == '2026-10-18' else '（土曜・CVR 3.23%・プライム感謝祭本番2日目）' if d == '2026-10-17' else '（金曜・CVR 2.92%・プライム感謝祭本番1日目）' if d == '2026-10-16' else '（木曜・CVR 3.09%・プライム先行最終日）' if d == '2026-10-15' else '（水曜・CVR 2.60%・プライム先行2日目）' if d == '2026-10-14' else '（火曜・CVR 3.18%・セッション−20%）' if d == '2026-10-13' else '（月曜・CVR 3.00%・ヒートシーラー出稿）' if d == '2026-10-12' else '（日曜・CVR 3.54%・セッション−30%）' if d == '2026-10-11' else '（土曜・CVR 3.45%・減額テスト初日）' if d == '2026-10-10' else '（金曜・CVR 2.64%・VIP7,000円化）' if d == '2026-10-09' else '（木曜・CVR 2.61%・まとめ買い切替日）' if d == '2026-10-08' else '（水曜・CVR 2.71%）' if d == '2026-10-07' else '（火曜・CVR 3.18%）' if d == '2026-10-06' else '（月曜・CVR 3.01%）' if d == '2026-10-05' else '（日曜・CVR 2.86%）' if d == '2026-10-04' else '（土曜・CVR 3.10%）' if d == '2026-10-03' else '（金曜・CVR 3.12%）' if d == '2026-10-02' else '（木曜・CVR 3.42%）' if d == '2026-10-01' else '（水曜・CVR 3.36%）' if d == '2026-09-30' else '（火曜・注文96件）' if d == '2026-09-29' else '（月曜・CVR 3.05%）' if d == '2026-09-28' else '（9月最高益・CVR 3.07%）' if d == '2026-09-27' else '（土曜・CVR 3.15%）' if d == '2026-09-26' else '（平日2日目・CVR 3.18%＝答え合わせ確定）' if d == '2026-09-25' else '（平日初日・CVR 3.16%）' if d == '2026-09-24' else '（秋分の日・CVR 3.17%）' if d == '2026-09-23' else '（国民の休日・CVR 3.02%）' if d == '2026-09-22' else '（敬老の日・CVR 3.28%・9月最高利益日）' if d == '2026-09-21' else '（日曜・CVR 3.13%）' if d == '2026-09-20' else '（マラソン初日・CVR 2.98%）' if d == '2026-09-19' else '' if d in ('2026-09-14','2026-09-15','2026-09-16','2026-09-17','2026-09-18') else '（セッション4,246・注文140＝9月最多）' if d == '2026-09-13' else '（CVR 3.74%・9月最高）' if d == '2026-09-12'
        else '（−2σトリガー発動日）' if d == '2026-09-04' else '')] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★11/17は セッション2,534・注文60件 = **CVR 2.37%**（前週火3.32%・ふだんの範囲 2.55〜3.26%の下の外）。時間別（6日平均=11/11-11/16）: 0〜5時台 注文9（6日平均8.3）・6〜9時台 10（14.2）・10〜13時台 14（14.3）・14〜17時台 12（12.5）・18〜23時台 15（19.8・前週火29）。広告費は 18〜23時台+22%で注文は少なかった',
  '★段ごと: カゴ投入率 **4.66%**（過去30日 4.86〜6.58%の下の外・最低）／決済画面÷カート 90.7%（中央値90.8%）／決済完了 56.1%（中央値54.7%）＝下がったのは「商品ページ→カート」だけ。入口ページ別ではガラスクリーナーが最大（来訪523・カート22／期待30.2・購入9／期待16.5・少ない側3%）。ほかは1ページずつは偶然の範囲（ナノ カート9／13.7・W固定 16／19.7・ノーズ 13／16.0）',
  '★点数/注文 1.42（85/60・VIP特典10を含む）・客単価5,239円（前日5,672・前週火4,870）・値引8,756円（gross比2.7%）。7,000円以上の注文 12件（20%）・10,000円以上 1件。客単価は範囲内（中央値比+3%）',
  '★セッション2,700〜3,800/日 は日予算240,000〜253,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(10/19-11/17)・祝日除外（11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  '★11/17(火)は祝日でない火曜平均(461,518円)比−31.9%・前週火(11/10)比−13.9%。曜日指数（10/19〜11/17・祝日除外・週次更新）: 日127.8・木100.0・金99.4・月97.2・土96.2・水95.7・火84.4'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])


# ---------- 時間別（11/17 vs 前週火11/10 vs 11/11-11/16平均。Meta時間別 data_query / Shopify GROUP BY hour_of_day 実測）----------
import json as _json
_H = _json.load(open('scripts/daily/hourly1117.json'))
sh('時間別', ['時間帯別の比較: 11/17(火) vs 前週火(11/10) vs 直近6日(11/11-11/16)平均。広告=Meta時間別（11/17は00時台 fresh・CSVの暫定より+154円）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上。注文の時間別合計は60（日別と一致）',
  '読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/17は広告費が 0〜5時台+21%・6〜9時台−11%・10〜13時台+13%・14〜17時台+16%・18〜23時台+22%（6日平均比）、注文は 9・10・14・12・15（6日平均 8.3・14.2・14.3・12.5・19.8）。夜に広告費を使ったが注文は少なかった日',
  '⚠️ 日中の比率（gross÷広告）は参考。判断は終日と週で行う'],
 ['時間帯','広告 11/17','広告 11/10','広告 6日平均','表示 11/17','表示 11/10','表示 6日平均','LPV 11/17','LPV 11/10','LPV 6日平均','Meta購入 11/17','Meta購入 11/10','Meta購入 6日平均',
  'gross 11/17','gross 11/10','gross 6日平均','注文 11/17','注文 11/10','注文 6日平均','gross÷広告 11/17','gross÷広告 11/10','gross÷広告 6日平均','セッション 11/17','カート 11/17'],
 _H['rows'], [10,10,10,10,10,10,10,9,9,9,9,9,9,11,11,11,8,8,8,9,9,9,10,8],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'#,##0',8:'#,##0',9:'#,##0',10:'#,##0',14:'#,##0',15:'#,##0',16:'#,##0',20:'0.00',21:'0.00',22:'0.00'})
wb.save('data/reports/report-2026-11-18.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 10月確定(近似原価) {aup:,.0f}円")
