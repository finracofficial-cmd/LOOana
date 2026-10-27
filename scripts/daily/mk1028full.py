# -*- coding: utf-8 -*-
"""2026-10-28 定例レポート本体（昨日=10/27 火）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep1027w.pkl', 'rb'))
FEE = 0.03388   # 2026-10-01 月次再計測（直近100注文 #27582〜#27681）。次回 11/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-10-28'   # 10/28 02時台（13セット・246,000）。10/27 00:07 スリッパ停止・予算変更なし
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 246000, sum(BUD.values())
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
# --- 7日(10/21-10/27) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD = {'ナノガラス脱毛パッド':269,'伸縮ガラスクリーナー':113,'W固定スマホ車載ホルダー':111,'優先配送 (VIP特典)':135,'快適マジックインソール':68,'ポータブルヒートシーラー':41,
'伸縮ワックス洗車ブラシ':35,'高見えレザーヘッドレストフック':24,'4-in-1マルチクリーナー':24,'コードレスダブルミスト加湿器':18,'ナノバブルシャワーヘッド':12,
'優先配送':8,'高見えレザードアポケット':8,'壁掛けディスペンサー':6,'偏光・調光サングラス':3,'バランスケアスリッパ':2,'ネックマッサージャー':1,
'スマートノーズEMS美顔器':1,'むくみ取りかっさ':1,'2WAYシートボックス':1,'形状記憶日傘':1,'携帯電動シェーバー':1,'オートソープディスペンサー':1,'ムダ毛シェーバー':1,'電動温熱カッサ':1,
'完全遮光・形状記憶':1}
STORE_ORD7, STORE_SESS7 = 737, 24807
assert sum(ORD.values()) == 887, sum(ORD.values())   # 全店737より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）

# --- 30日(9/28-10/27) Shopify注文数（ShopifyQL GROUP BY product_title 実測）---
ORD30 = {'ナノガラス脱毛パッド':1119,'伸縮ガラスクリーナー':530,'W固定スマホ車載ホルダー':496,'快適マジックインソール':369,'優先配送 (VIP特典)':352,
'高見えレザーヘッドレストフック':170,'4-in-1マルチクリーナー':95,'ポータブルヒートシーラー':91,'姿勢サポートチェア':44,'携帯電動シェーバー':44,'バランスケアスリッパ':43,
'伸縮ワックス洗車ブラシ':35,'ナノバブルシャワーヘッド':32,'優先配送':29,'ネックマッサージャー':19,'もちふわ肉球サンダル':19,'UV歯ブラシ除菌器':18,
'コードレスダブルミスト加湿器':18,'むくみ取りかっさ':13,'壁掛けディスペンサー':13,'高見えレザードアポケット':8,'偏光・調光サングラス':7,'電動眉シェーバー':5,'形状記憶日傘':3,
'2WAYシートボックス':3,'完全遮光・形状記憶':3,'姿勢サポートベルト':2,'ムダ毛シェーバー':2,'電動温熱カッサ':2,'スマートノーズEMS美顔器':1,'ビジュアル耳かき':1,
'健康サンダル':1,'温感EMSフェイシャルワンド':1,'リカバリーサンダル':1,'オートソープディスペンサー':1,'完全遮光・接触冷感UVハット':1}
assert sum(ORD30.values()) == 3591, sum(ORD30.values())

# --- 30日(9/28-10/27) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック）---
MF_RAW = {'ナノガラス脱毛パッド':(2393733,1831443,29057),'伸縮ガラスクリーナー':(1059904,385165,14644),
'W固定スマホ車載ホルダー':(1038341,428521,14986),'快適マジックインソール':(1030656,680283,13506),
'高見えレザーヘッドレストフック':(433981,93403,3843),'カタログ全部（テスト）':(267066,86179,3042),
'4-in-1マルチクリーナー':(203952,96501,3280),'ポータブルヒートシーラー':(198983,45053,2397),
'バランスケアスリッパ':(144650,83152,1681),'姿勢サポートチェア':(143325,69153,2054),
'携帯電動シェーバー':(113531,45951,1131),'ナノバブルシャワーヘッド':(92744,51430,1265),
'UV歯ブラシ除菌器':(87895,22061,423),'ネックマッサージャー2':(86582,35652,621),
'コードレスダブルミスト加湿器':(75662,18120,686),'もちふわ肉球サンダル':(74919,17656,924),
'伸縮ワックス洗車ブラシ':(59348,16137,793),'ディスペンサー':(56463,15426,405),
'高見えレザードアポケット':(32026,7234,227),'むくみ取りかっさ':(25825,7243,249),
'電動眉シェーバー':(24315,8228,143),'ハイウエストシェイプパンツ':(4923,777,22),'ロングニトリル家事手袋':(4366,824,19)}
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
def ucost(n, d):
    return 732 if (n == '高見えレザーヘッドレストフック' and d >= '2026-10-07') else COSTa[n]
ALLD = sorted({d for v in Sd.values() for d in v if d <= D1[0]})
D5 = ALLD[-5:]
def win(n, days):
    g = sum(Sd[n][d][0] for d in days if d in Sd[n]); dc = sum(Sd[n][d][1] for d in days if d in Sd[n])
    c = sum(Sd[n][d][0] / PRICEa[n] * ucost(n, d) for d in days if d in Sd[n]) if g and n in PRICEa and n in COSTa else 0
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
        if n in PRICEa and n in COSTa: c += g / PRICEa[n] * ucost(n, d)
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
# 9月確定（9/30広告費の上書き後の最終値）と10月の滑り出し
AUG = [d for d in ALLD if '2026-09-01' <= d <= '2026-09-30']
assert len(AUG) == 30
_au = [dayblk(d) for d in AUG]
aus = sum(x[0] for x in _au); auc = sum(x[1] for x in _au); aua = sum(x[2] for x in _au); aup = aus-auc-aua
_cum = [dayblk(d) for d in CUM]
cs = sum(x[0] for x in _cum); cc = sum(x[1] for x in _cum); ca = sum(x[2] for x in _cum); cp = cs-cc-ca
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
sh('収益', [f'LOOTY 収益レポート 2026-10-28（昨日 = 10/27 火）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★10月累積（10/01-27・{len(CUM)}日）: 実売 {cs:,.0f} / 利益 {cp:,.0f}円（{cp/cs:.1%}）／1日あたり {cp/len(CUM):,.0f}円（9月確定は {aup:,.0f}円・{aup/30:,.0f}円/日）',
  '★10/27(火)は 実売 **450,245円**・利益 **+102,601円（22.8%）**・MER 1.92。祝日でない火曜の平均(9/1〜10/20・7回 486,537円)比 **−7.5%**、前週火10/20(369,069円)比 +22.0%。**朝0〜9時台はMetaの配信が先週比−30%で売上が出遅れ**（6〜9時台 gross 61,720円・直近6日平均128,313円）、10時台以降は平常。前夜の20時以降の急落は再発せず（20〜23時台 gross 109,080円・直近6日平均94,653円）',
  '★注文94件・セッション3,198（前週火10/20 3,176）・CVR **2.94%**（前週火2.39%）・カゴ投入率5.91%（189/3,198）・チェックアウト完了率54.0%（94/174）。点数/注文1.33・客単価4,790円。返品0。VIP特典13件・7,000円以上15件(16.0%)',
  '🚨 3日移動平均 **122,210円/日**（10/25-27）<130,000 → **ブレーキ発動（合計予算を増やさない）**。直近7日利益939,844円（25.3%・前7日822,299円）',
  '🔁 10/27: 00:07 スリッパ停止 → 13セット・**246,000円**。予算変更なし。消化234,963円（暫定・日予算の96%）。インソール新素材は10/27時点で未投入（広告A 1本のみ）',
  '✅ 本日（10/28）の判定: ①ナノ新BCセット（Dのみ）: 10/27 消化31,360円（32,000の98%）・Meta計上14件・ACTIVE・エラー表示なし → **合格・11/2の週次へ** ②10/26夜の急落: 10/27の20〜22時台は購入16件（前夜4件）で**再発なし**。支払い試行の集計は10/26=17件・10/27=0件で未反映のまま ③車載B: ユーザー判断で16,000据え置き（10/27記録）→ 11/2にA/BのCPAを週で並べる',
  '✅ 10/26広告費を確定上書き: 257,498→**258,792円**（+1,294円）→ 10/26利益は+96,548円に確定。10/27分234,963円は暫定・次回確定',
  '原価は日次のバリアント構成が取れないナノガラス/壁掛けディスペンサーのみ30日実測ミックスの加重平均単価【近似】。'
  '期間別サマリー（次シート）はバリアント別実数量の正確値'],
 ['日付','曜','実売','原価','広告費','利益','利益率','手数料後利益','MER','3日移動平均利益','ブレーキ','備考'],
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
for r in body: _BK[r[0]][r[1]] += int(r[3])
def last_change(cp):
    """予算が最後に変わったスナップショットの日付（その日を変更後の初日とする＝実験P2の慣行と同じ）"""
    ch, prev = None, None
    for k in _keys:
        v = _BK[k].get(cp, 0)
        if prev is not None and v != prev and v: ch = k[:10]   # 再開（0→予算あり）も変更として扱う
        prev = v
    return ch
# 宣言済みの判定日（decisions.md の判定カレンダー）。判定日前は動かさない
CAL = {'伸縮ガラスクリーナー': ('2026-11-02', '10/26週次判定は倍率1.426で−20%の帯だったが、ユーザー判断で38,000据え置き。7日(10/21-27)倍率1.53・+141,306円。今週中に新素材（結露・大掃除）を投入。11/2(月)は10/26-11/1の倍率で通常の週次判定'),
       'W固定スマホ車載ホルダー': ('2026-11-02', 'A 22,000→14,000（10/26）。B は3日確認でCPAがAより高かったが、ユーザーの経営判断で16,000据え置き。10/26-27 倍率1.63・+38,764円（先週1.36）。11/2(月)に A の−8,000の答え合わせと A/B のCPAを週で比較'),
       '壁掛けディスペンサー': ('2026-10-24', '📌停止（10/24判定）｜再開後7日(10/17-23)倍率0.98<1.25 → 宣言どおり停止（14個・−1,102円・返品0）。ユーザーがMetaで停止'),
       '4-in-1マルチクリーナー': ('2026-11-02', '小さい商品ルールで8,000継続。7日(10/21-27)倍率1.82・+45,740円。11/2(月)も同ルール'),
       'ポータブルヒートシーラー': ('2026-11-02', '10/26 ユーザーが12,000→15,000。10/26-27 15個・倍率1.34・+10,668円（先週1.64）。11/2(月)に答え合わせ: 増えた粗利÷増えた広告費≥1.0で維持・<1.0で12,000へ'),
       '高見えレザーヘッドレストフック': ('2026-11-02', '8,000（10/26に戻した）。10/26-27 5個・倍率0.85・−2,362円（10/27は売上0）。小さい商品ルール: 10/26-11/1 が赤字なら赤字1週目、2週続けて赤字で停止'),
       'ナノバブルシャワーヘッド': ('2026-10-26', '10/26 00:19 ユーザーが停止（先週倍率1.45・+24,768円）。再開はいつでも可'),
       'コードレスダブルミスト加湿器': ('2026-11-02', '8,000継続（10/27 7日判定合格 +5,464円）。7日(10/21-27)倍率1.02・+1,215円（10/27は売上0）。小さい商品ルール: 2週続けて赤字で停止'),
       '高見えレザードアポケット': ('2026-10-29', '10/24 2日目判定: CTR3.09%＝延長も停止もしない帯。ユーザーが11,000へ増額済み。10/22-24 12個・倍率1.47・+11,588円（10/24は着地75・カート0・0個。実ブラウザでカート追加は正常）。10/29: 7日(10/22-28)の利益≥0で継続'),
       '伸縮ワックス洗車ブラシ': ('2026-10-30', '18,000（10/26〜）。10/23-27 44個・倍率2.35・+80,408円（10/27は11個・2.45）。10/30: 7日(10/23-29)の利益≥0で継続（以後は週次ルール）'),
       'バランスケアスリッパ': ('2026-10-27', '10/27 00:07 ユーザーが停止（再開1日 9,681円・2個・0.76）。再開はいつでも可'),
       'ナノガラス脱毛パッド': ('2026-11-02', '10/28 新BCセット（Dのみ）確認: 10/27 消化31,360（98%）・Meta計上14件・エラーなし → 合格。7日(10/21-27)倍率1.62。11/2(月)は週次判定（10/26-11/1）'),
       'むくみ取りかっさ': ('2026-10-21', '10/21判定済み: 再開後7日(10/14-20)倍率1.18 <1.25 → 停止。Metaは10/16から配信なし＝再開しない（期間利益+4,520円）'),
       '快適マジックインソール': ('2026-11-02', '10/26判定: 32,000据え置き。7日(10/21-27)倍率1.37・+82,287円（−20%の帯1.25-1.43）。新素材は10/27時点で未投入 → 10/28に投入し、11/2(月)に新広告と旧Aの同週CTR/CPA＋週倍率で判定（≥1.43維持・<1.25で−20%）'),}
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
        _cur = BUDL.get(MAP.get(n, n)); _a1 = R['A1'].get(n, 0); _a3 = R['A3'].get(n, 0)
        _act = '⛔停止中（販売0）' if not _cur else '🆕新商品・学習中（販売0）'
        _memo = CAL.get(n, ('', ''))[1] or ('売上0のまま停止' if not _cur else '購入0のまま分岐CPA×3を消化したら事故停止')
        ACT.append(_act)
        SIMPLE.append([n, _cur if _cur else '停止中', _act, 0, '7日', 0, 0 if _a3 else '', 0 if _a1 else '', _memo,
            0, 0 if _a3 else '', 0 if _a1 else '', '', '', round(p7), round(-_a3), round(-_a1), '', '', '', '🚨縮小・停止', ''])
        continue
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
    # --- 倍率（MER÷分岐）と予算アクション ---
    r7 = mer / be; r3 = (s3 / a3) / be if a3 else None; r1 = (s1 / a1) / be if a1 else None
    cur = BUDL.get(cp); small = bool(cur) and cur <= SMALL
    first_ad = min((d for d, v in ADd[cp].items() if v > 0), default=None)
    chg = last_change(cp)
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
    elif first_ad and first_ad > D7[0]:
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
        act, memo, rj, basis = weekly_rule(n, cp, small, chg)
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
_shown = {MAP.get(r[0], r[0]) for r in SIMPLE}
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
 ['📊 10/27(火)','実売 **450,245円**・利益 **+102,601円（22.8%）**・MER1.92',
  '火曜平均(486,537円)比−7.5%・前週火比+22.0%。朝0〜9時台の配信不足（Meta表示−30%）で出遅れ、10時以降は平常。来訪後の反応（カート率・購入率）は終日平常','—','監視'],
 ['🚨 ブレーキ発動','3日移動平均 **122,210円/日**（10/25 +167,480・10/26 +96,548・10/27 +102,601）',
  '130,000を下回った → 合計予算を増やさない。減額は週次ルールどおり11/2','—','10/29'],
 ['✅ 本日: ナノ新BCセット（Dのみ）','10/27 消化31,360円（98%）・Meta計上14件・ACTIVE・エラーなし','合格。以後は11/2の週次判定（ナノ全体の倍率）','—','11/2'],
 ['✅ 10/26夜の急落','10/27 20〜22時台: 購入16件・gross 68,280円（前夜 4件・29,860円）','再発なし。単発として扱う。支払い試行の集計（10/26=17件）は未反映のまま → 反映されたら10/26の失敗数だけ確認','—','10/29'],
 ['🔧 インソール新素材','7日(10/21-27)倍率1.37（帯1.25-1.43）・CTR 1.68%（5週前2.69%）。10/27は旧A 1本のみ','今日投入。予算32,000据え置き。11/2に新広告vs旧AのCTR/CPA＋週倍率で判定','ユーザー','11/2'],
 ['🔧 クリーナー新素材','7日倍率1.53だがCPA 1,397→2,479円（5週）・CTR 4.74→3.22%。損失額は最大','結露・大掃除訴求を今週投入。予算38,000据え置き','ユーザー','11/2'],
 ['👀 フック・加湿器','10/27 売上0（広告7,548・8,263円）。10/26-27 フック0.85／加湿器 7日1.02','小さい商品ルール（2週続けて赤字で停止）で11/2に判定。今日は動かさない','—','11/2'],
 ['👀 10/30(金)','洗車ブラシ 7日(10/23-29)','10/23-27で44個・倍率2.35・+80,408円。18,000に上げた後も2.45','—','10/30'],
]
sh('ネクストアクション', ['今日やること・判定カレンダー・持ち越しタスク（実施が確認できるまで毎日残す）'],
   ['区分','商品/対象','内容','効果','期限'], NA, [12, 26, 78, 16, 10])

# ---------- 2a 予算ルール（常設・2026-10-20ユーザーと合意）----------
BR_RULE = [
 ['物差し','倍率 ＝（売上 − 原価）÷ 広告費。1.0未満は赤字','Shopifyの実売・原価・Metaの広告費の実測だけで計算する'],
 ['物差し','利益が一番大きいのは「足した1万円が、ちょうど1万円の粗利を連れてくる所」。そこでも倍率は1.0ではなく1.4〜1.9くらいになる',
  '最初の方の1万円がたくさん稼ぐので、全部をならした倍率は高めに出る。倍率1.0まで増やすのは出しすぎ'],
 ['物差し','例: 日予算を1万円ずつ足すと → 4万円で倍率1.88（次の1万円は1.1万円の粗利＝まだ得）／6万円で1.60（次の1万円は1.0万円＝頂上）／8万円で1.39（次の1万円は0.7万円＝損）',
  '説明用の数字。頂上付近（5〜7万円）は利益がほぼ同じ＝平らなので、細かく合わせる必要はない'],
 ['物差し','1.86以上＝まだ増やせる ／ 1.43〜1.86＝頂上付近（そのまま） ／ 1.43未満＝出しすぎ',
  '足した分の効きは平均のおよそ0.7倍（8月に予算を動かして実測: 0.6〜0.8倍）。1.43×0.7≒1.0（トントン）、1.86×0.7≒1.3（3割の余裕）'],
 ['既存（日予算1万円超）','いつ: 毎週月曜に1回だけ。先週の月〜日（ちょうど1週間）の倍率で決める。火〜日は触らない',
  '曜日で倍率が±1割ぶれる（土1.10・金0.92）。月〜日なら土日が1回ずつ入って消える。4日で決めると好調な商品を何度も削った（8月中旬以降、主力の4日「下げる」11回すべて空振り）'],
 ['既存（日予算1万円超）','何をするか: 1.25未満→2〜3割減らす ／ 1.25〜1.43→2割減らす ／ 1.43〜1.86→そのまま ／ 1.86以上かつ予算をほぼ使い切っている（95%以上）→2割増やす',
  '予算を使い切れていない商品は、増やしてもMetaが配信できない'],
 ['既存（日予算1万円超）','どれだけ: 1回2割まで（1段ずつ）。動かしたら1週間待つ',
  '1割未満は効果がぶれに埋もれて分からない（8/4の全体−2.6%は判定不能だった）。一気に動かすと頂上を飛び越え、配信も不安定になる'],
 ['既存（日予算1万円超）','答え合わせ: 動かした翌週の月曜に「増えた粗利 ÷ 増えた広告費」。増やした→1.0以上で維持・未満で元に戻す ／ 減らした→1.0未満で正解・1.0以上は削りすぎで元に戻す',
  '平均の倍率が高くても、足した分が稼いでいないことがある（4-in-1: 8,000→10,000で足した分は1万円あたり約2,800円の粗利。倍率1.87でも足した分は赤字）'],
 ['小さい商品（日予算1万円以下）','予算は基本動かさない。毎週月曜に先週1週間を見て、赤字1週目＝注意 ／ 2週続けて赤字＝停止',
  '売れる数が少なくぶれが大きい。8/1〜10/19で1週赤字は211回中3回（姿勢サポートチェア）で、3回とも翌週は黒字（+7〜9万円）。待つ損（日1万円・倍率0.8で週約1.4万円）より、間違って止める損の方が大きい'],
 ['小さい商品（日予算1万円以下）','例外: 先週の倍率が1.86以上で予算をほぼ使い切っていれば、2割増やしてよい',
  '10/20 フック8,000→10,000で初適用（8,000にしてからの倍率3.52・前は日2万円で利益が出ていた）'],
 ['新商品（再開を含む）','いつでも: 購入ゼロのまま「分岐CPA（売価−原価）×3」を使ったら止める（3,980円の商品で約8,500〜10,000円＝売価の2.1〜2.5倍）',
  'トントンで売れる商品なら、分岐CPA1つ分の広告費で平均1個売れる。3つ分使って0個は、偶然では約5%しか起きない'],
 ['新商品（再開を含む）','2日目: クリック率4.5%超→伸ばす ／ 2.5%未満かつカート追加ゼロ→止める',
  '「売れる・売れない」は差が大きいので1〜2日で分かる（過去の新商品: 最初の月にCTR4.5%以上だった11件は外れ0件）'],
 ['新商品（再開を含む）','7日目: 黒字なら継続（以後は既存商品のルール） ／ 赤字なら停止',''],
 ['共通','事故（購入ゼロでお金だけ出ていく等）は、曜日に関係なくその日に止める',''],
 ['共通','判定日を宣言済みの商品は、宣言したときの基準で判定する','途中で基準を変えると判断がぶれる'],
 ['共通','このルールの判定結果は「シンプル判定」タブの「予算アクション」列に出る。月曜以外は「次の判定日」を表示',''],
]
_wr = sh('予算ルール', ['予算の判断ルール（2026-10-20 ユーザーと合意）。迷ったらこのタブだけ見ればよい',
  '★まとめ: ①毎週月曜に先週の月〜日の倍率を見る ②表に当てはめる（動かすなら2割） ③先週動かした商品は答え合わせ ④火〜日は触らない',
  '★日予算1万円以下は「2週続けて赤字で停止」だけ。新商品は「購入ゼロで分岐CPA×3」「2日目のクリック率」「7日目の黒字」の3段'],
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
for lbl, N, K, ACC in [('前日 10/27(火)', R['N1'], R['K1'], R['ACCT1']), ('3日 10/25-10/27', R['N3'], R['K3'], R['ACCT3']),
        ('7日 10/21-10/27', R['N7'], R['K7'], R['ACCT7']), ('30日 9/28-10/27', R['N30'], R['K30'], R['ACCT30']),
        ('10月累積 10/01-27', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過（10/27）: Σ商品gross=全店463,380 ／ Σ値引=13,135 ／ Σ広告費=キャンペーン合算234,963円',
 '✅ 10/26の広告費は再取得で確定済み（257,498円 → **258,792円**・+1,294円。10/28に上書き）',
 '⚠️ 10/27の広告費は 10/28 02時台の取得【暫定】→ 次回に再取得して確認する',
 '★ガラスクリーナー・ヘッドレストフックの原価は保守側の最高値バリアント単価で計上（フックは黒1,275だが1,344で計上＝利益は保守側）',
 '★10/27の返品は0件。★5e-2突合: 広告なしで売れた商品＝携帯電動シェーバー1（自然購入）。広告費ありで売上0＝フック（7,548円）・加湿器（8,263円）',
 '決済ブレンド率 **3.388%**（2026-10-01再計測: SP 83.7%×3.25%・KOMOJU 16.3%×4.1%。前回3.436%。次回11/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(10/27 火) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','10/27(火)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '10/27(火)は実売450,245円・利益+102,601円（22.8%）・MER1.92。火曜平均比−7.5%。洗車ブラシ11個（倍率2.45）・4-in-1 4個（2.27）・車載17個（1.68）・インソール17個（1.56）・シーラー8個（1.51）が平常以上、ナノ36個（1.43）・クリーナー16個（1.35）がやや弱く、フック0個（−7,548円）・加湿器0個（−8,263円）が売上ゼロ。朝の配信不足が日計を押し下げ').font = Font(name='Arial', size=10, color='CC0000')

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
sh('商品別', ['商品別（7日 10/21-10/27 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,845,209円（10/27分は暫定・w1027でassert）',
  '当月累積利益は10月分（10/01-27・27日）',
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
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(9/28-10/27)」。他シートの7日窓と混ぜて読まないこと',
  'クリックは **アウトバウンドクリック**（data_query 実測・Asia/Tokyo）',
  '✅ 検算: 全キャンペーンで data_query の消化 = CSV(9/28-10/27) が許容差以内で一致（コード内assert）',
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
  '非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（現況99,219円=🚨発動。中身が停止済み商品のままなので再定義が必要）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['10/26(月)','週次: ナノ 80,000','先週(10/19-25)の倍率: <1.25→−20〜30%／1.25-1.43→−20%／1.43-1.86→そのまま／≥1.86かつ消化≥95%→+20%','倍率1.64','**そのまま**','新BCは10/28合格'],
 ['10/26(月)','週次: クリーナー 38,000','同上','倍率1.426','**−20%の帯 → ユーザー判断で据え置き**','11/2に通常判定'],
 ['10/26(月)','週次: 車載 38,000','同上','倍率1.36','**−20% → A 14,000（実施）**','B は経営判断で16,000据え置き'],
 ['10/26(月)','週次: シーラー 12,000','同上','倍率1.64','**そのまま → ユーザーが15,000へ**','11/2に答え合わせ'],
 ['10/26(月)','インソール 32,000','帯−20%／答え合わせ「戻す」が逆','倍率1.31','**据え置き（新素材）**','10/28投入・11/2判定'],
 ['10/26(月)','フック 10,000の答え合わせ','増えた粗利÷増えた広告費≥1.0で維持','−3.86','**8,000へ戻す（実施）**','小さい商品ルールへ'],
 ['10/27','加湿器（新規・7日）','7日(10/20-26)の利益≥0 → 継続／<0 → 停止','+5,464円・倍率1.08','**継続（8,000）**','以後は小さい商品ルール'],
 ['10/27','車載B 16,000（変更+3日）','10/24-26のB CPA ≤ 主力A → 維持／> 主力A → 12,000','B 2,500・A 2,219','**12,000の帯 → 経営判断で据え置き**','11/2にA/Bを週で比較'],
 ['10/28','ナノ新BCセット（Dのみ）','配信が止まっていない・日予算を消化・エラーなし','10/27 98%消化・14件・エラーなし','**合格**','11/2の週次へ'],
 ['10/28','10/26夜の急落の再発確認','10/27 20〜22時台の購入が60日最低(6件)を下回らない','16件','**再発なし**','支払い試行集計は未反映'],
 ['10/30','洗車ブラシ（新規・7日）','7日(10/23-29)の利益≥0 → 継続／<0 → 停止','10/23-27 +80,408円・倍率2.35','待機',''],
 ['11/2(月)','2回目の週次判定（10/26-11/1）','週次表＋答え合わせ（車載A・シーラー）＋インソール新素材＋小さい商品（フック・加湿器・4-in-1）','—','待機','ブレーキ中は増額なし'],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日(10/28 水): ナノ新BCセット（D）合格（98%消化・14件）。10/26夜の急落は再発なし。ブレーキ発動（3日移動平均122,210）＝合計予算を増やさない。やること: ①インソール新素材の投入（10/27は未投入）②クリーナー新素材（結露・大掃除）の準備 ③10/30 洗車ブラシ7日判定 ④11/2 週次判定',
  '★次: 10/30 洗車ブラシ7日 → 11/2(月) 2回目の週次判定（10/26-11/1）。インソール新素材は投入7日後にCTR/CPA（新広告 vs 旧A）',
  '★倍率の定義: **MER ÷ 分岐MER**。1.0未満＝赤字',
  '★9月確定: 30日で+4,762,263円（28.9%・158,742円/日）。10月は12日で+1,926,117円（160,510円/日）'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-10-27b': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['前日(10/27 00時・2026-10-27b)スナップショット → 本日(10/28 02時)。10/27は予算変更なし（00:07 スリッパ停止のみ・10/27bで反映済み）',
  '合計 246,000 → **246,000円/日**（変更なし）',
  '★体制: 13セット・246,000円/日（🚨ブレーキ発動: 3日移動平均122,210円 <130,000 → 合計予算を増やさない）',
  '★10/27の消化は 234,963円（暫定・日予算の96%）。10/26は確定258,792円',
  '★眉シェーバーは停止中のため予算表から外れている'],
 ['商品/キャンペーン','変更前','変更後','差','変化率','7日MER','分岐','目標','7日余裕','3日MER','3日余裕',
  '倍率7日','倍率3日','消化率(7日)','1円あたり利益','頑健性','印'],
 BR, [26,10,10,9,9,8,7,7,9,8,9,9,9,12,13,14,7],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'+0.0%;-0.0%',14:'0.0%'})

# ---------- 10 CVR推移 ----------
SES = {'2026-08-04':6639,'2026-08-05':5425,'2026-08-06':5138,'2026-08-07':4827,'2026-08-08':5527,'2026-08-09':5886,
'2026-08-10':5245,'2026-08-11':6001,'2026-08-12':4900,'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,
'2026-08-16':5349,'2026-08-17':3438,'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,
'2026-08-22':3220,'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733,'2026-08-27':3145,
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936,'2026-09-02':3142,'2026-09-03':3340,'2026-09-04':3293,'2026-09-05':3217,'2026-09-06':3752,'2026-09-07':2787,'2026-09-08':2739,'2026-09-09':2801,'2026-09-10':3514,'2026-09-11':3014,'2026-09-12':3132,'2026-09-13':4246,'2026-09-14':3592,'2026-09-15':3358,'2026-09-16':3348,'2026-09-17':3418,'2026-09-18':3583,'2026-09-19':4088,'2026-09-20':4310,'2026-09-21':4571,'2026-09-22':3877,'2026-09-23':4043,'2026-09-24':3257,'2026-09-25':3236,'2026-09-26':4416,'2026-09-27':5017,'2026-09-28':3841,'2026-09-29':3426,'2026-09-30':3276,'2026-10-01':4124,'2026-10-02':3619,'2026-10-03':3578,'2026-10-04':4506,'2026-10-05':3394,'2026-10-06':3904,'2026-10-07':3692,'2026-10-08':3530,'2026-10-09':3218,'2026-10-10':3685,'2026-10-11':3163,'2026-10-12':3794,'2026-10-13':3140,'2026-10-14':3501,'2026-10-15':3231,'2026-10-16':2914,'2026-10-17':3529,'2026-10-18':3863,'2026-10-19':3094,'2026-10-20':3176,'2026-10-21':3223,'2026-10-22':3470,'2026-10-23':3054,'2026-10-24':3560,'2026-10-25':4375,'2026-10-26':3923,'2026-10-27':3198}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88,'2026-09-02':92,'2026-09-03':103,'2026-09-04':74,'2026-09-05':106,'2026-09-06':122,'2026-09-07':96,'2026-09-08':95,'2026-09-09':98,'2026-09-10':116,'2026-09-11':96,'2026-09-12':117,'2026-09-13':140,'2026-09-14':102,'2026-09-15':103,'2026-09-16':99,'2026-09-17':100,'2026-09-18':96,'2026-09-19':122,'2026-09-20':135,'2026-09-21':150,'2026-09-22':117,'2026-09-23':128,'2026-09-24':107,'2026-09-25':102,'2026-09-26':142,'2026-09-27':156,'2026-09-28':117,'2026-09-29':96,'2026-09-30':110,'2026-10-01':141,'2026-10-02':113,'2026-10-03':111,'2026-10-04':129,'2026-10-05':102,'2026-10-06':124,'2026-10-07':100,'2026-10-08':92,'2026-10-09':85,'2026-10-10':127,'2026-10-11':112,'2026-10-12':114,'2026-10-13':100,'2026-10-14':91,'2026-10-15':100,'2026-10-16':85,'2026-10-17':114,'2026-10-18':108,'2026-10-19':93,'2026-10-20':76,'2026-10-21':104,'2026-10-22':112,'2026-10-23':102,'2026-10-24':105,'2026-10-25':125,'2026-10-26':95,'2026-10-27':94}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       ('★昨日（火曜・CVR 2.94%・朝の配信不足）' if d == '2026-10-27' else '（月曜・CVR 2.42%・20時以降に急落）' if d == '2026-10-26' else '（土曜・CVR 2.95%・ナノBC約7.5時間停止）' if d == '2026-10-24' else '（金曜・CVR 3.34%・洗車ブラシ新規）' if d == '2026-10-23' else '（木曜・CVR 3.23%・ドアポケット新規）' if d == '2026-10-22' else '（水曜・CVR 3.23%・前日から全面回復）' if d == '2026-10-21' else '（火曜・CVR 2.39%・81日で実売最低）' if d == '2026-10-20' else '（月曜・CVR 3.01%・プライム感謝祭最終日）' if d == '2026-10-19' else '（日曜・CVR 2.80%・プライム感謝祭本番3日目）' if d == '2026-10-18' else '（土曜・CVR 3.23%・プライム感謝祭本番2日目）' if d == '2026-10-17' else '（金曜・CVR 2.92%・プライム感謝祭本番1日目）' if d == '2026-10-16' else '（木曜・CVR 3.09%・プライム先行最終日）' if d == '2026-10-15' else '（水曜・CVR 2.60%・プライム先行2日目）' if d == '2026-10-14' else '（火曜・CVR 3.18%・セッション−20%）' if d == '2026-10-13' else '（月曜・CVR 3.00%・ヒートシーラー出稿）' if d == '2026-10-12' else '（日曜・CVR 3.54%・セッション−30%）' if d == '2026-10-11' else '（土曜・CVR 3.45%・減額テスト初日）' if d == '2026-10-10' else '（金曜・CVR 2.64%・VIP7,000円化）' if d == '2026-10-09' else '（木曜・CVR 2.61%・まとめ買い切替日）' if d == '2026-10-08' else '（水曜・CVR 2.71%）' if d == '2026-10-07' else '（火曜・CVR 3.18%）' if d == '2026-10-06' else '（月曜・CVR 3.01%）' if d == '2026-10-05' else '（日曜・CVR 2.86%）' if d == '2026-10-04' else '（土曜・CVR 3.10%）' if d == '2026-10-03' else '（金曜・CVR 3.12%）' if d == '2026-10-02' else '（木曜・CVR 3.42%）' if d == '2026-10-01' else '（水曜・CVR 3.36%）' if d == '2026-09-30' else '（火曜・注文96件）' if d == '2026-09-29' else '（月曜・CVR 3.05%）' if d == '2026-09-28' else '（9月最高益・CVR 3.07%）' if d == '2026-09-27' else '（土曜・CVR 3.15%）' if d == '2026-09-26' else '（平日2日目・CVR 3.18%＝答え合わせ確定）' if d == '2026-09-25' else '（平日初日・CVR 3.16%）' if d == '2026-09-24' else '（秋分の日・CVR 3.17%）' if d == '2026-09-23' else '（国民の休日・CVR 3.02%）' if d == '2026-09-22' else '（敬老の日・CVR 3.28%・9月最高利益日）' if d == '2026-09-21' else '（日曜・CVR 3.13%）' if d == '2026-09-20' else '（マラソン初日・CVR 2.98%）' if d == '2026-09-19' else '' if d in ('2026-09-14','2026-09-15','2026-09-16','2026-09-17','2026-09-18') else '（セッション4,246・注文140＝9月最多）' if d == '2026-09-13' else '（CVR 3.74%・9月最高）' if d == '2026-09-12'
        else '（−2σトリガー発動日）' if d == '2026-09-04' else '')] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★10/27は セッション3,198・注文94件 = **CVR 2.94%**（前週火10/20 2.39%・前日10/26 2.42%）。時間帯別のカート率・購入率は終日平常。弱かったのは0〜9時台の来訪数（Metaの表示が先週比−30%）で、来た人の反応は落ちていない',
  '★チェックアウト完了率: 10/26 43.9% → 10/27 **54.0%**（94/174）。カゴ投入率 **5.91%**（189/3,198）。支払い試行の集計（payment_attempts）は10/26=17件・10/27=0件でまだ未反映（通常90件前後）。10/26夜の「失敗して注文にならなかった人」の数は引き続き確認不能',
  '★点数/注文 1.33（125/94・VIP特典13を含む）・客単価4,790円・値引13,135円',
  '★セッション2,700〜3,800/日 は日予算240,000〜253,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(9/28-10/27)・祝日除外（10/12スポーツの日も除外）。売上=gross−値引。次回定期更新11/2(月)',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  '★10/27(火)は祝日でない火曜平均(486,537円)比**−7.5%**・前週火(10/20)比+22.0%。火曜は曜日指数90.8で最弱。日・土が突出、火・金が最弱'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])


# ---------- 時間別（10/27 vs 前週火10/20 vs 10/21-26平均。Meta時間別 data_query / Shopify TIMESERIES hour 実測）----------
import json as _json
_H = _json.load(open('/tmp/claude-0/-home-user-LOOana/91ae6ee3-db77-5228-ad52-aeac6ce2aa54/scratchpad/hourly1027.json'))
sh('時間別', ['時間帯別の比較: 10/27(火) vs 前週火(10/20) vs 直近6日(10/21-26)平均。広告=Meta時間別（10/27は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',
  '読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。10/27は6〜9時台だけ表示が6日平均の−31%で売上が出遅れ、10時台以降は平常〜上',
  '⚠️ 日中の比率（gross÷広告）は参考。判断は終日と週で行う'],
 ['時間帯','広告 10/27','広告 10/20','広告 6日平均','表示 10/27','表示 10/20','表示 6日平均','LPV 10/27','LPV 10/20','LPV 6日平均','Meta購入 10/27','Meta購入 10/20','Meta購入 6日平均',
  'gross 10/27','gross 10/20','gross 6日平均','注文 10/27','注文 10/20','注文 6日平均','gross÷広告 10/27','gross÷広告 10/20','gross÷広告 6日平均','セッション 10/27','カート 10/27'],
 _H['rows'], [10,10,10,10,10,10,10,9,9,9,9,9,9,11,11,11,8,8,8,9,9,9,10,8],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'#,##0',8:'#,##0',9:'#,##0',10:'#,##0',14:'#,##0',15:'#,##0',16:'#,##0',20:'0.00',21:'0.00',22:'0.00'})
wb.save('data/reports/report-2026-10-28.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 9月確定(近似原価) {aup:,.0f}円")
