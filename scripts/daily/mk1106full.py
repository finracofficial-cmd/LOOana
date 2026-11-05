# -*- coding: utf-8 -*-
"""2026-11-06 定例レポート本体（昨日=11/05 木。11/04の広告費は確定値に上書き）。"""
import pickle, csv, datetime, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
R = pickle.load(open('/tmp/rep1105w.pkl', 'rb'))
FEE = 0.03325   # 2026-11-02 月次再計測（直近100注文 #30857〜#30956・553,322円）。次回 12/1
D1, D3, D7, D30, CUM = R['D1'], R['D3'], R['D7'], R['D30'], R['CUM']
SNAP = '2026-11-06'   # 11/06 00時台 Meta読み（adsetdaily_budget）の日予算が 2026-11-05f と一致（15セット・192,000）
rows = list(csv.reader(open('data/budget-snapshots.csv'))); body = [r for r in rows[1:] if r]
assert any(r[0] == SNAP for r in body), f'{SNAP} スナップショット未記録'
BUD = collections.defaultdict(int)
for r in body:
    if r[0] == SNAP: BUD[r[1]] += int(r[3])
assert sum(BUD.values()) == 192000, sum(BUD.values())
_BS = collections.defaultdict(dict)
for r in body:
    day = _BS[r[1]].setdefault(r[0][:10], {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))
for cp, byday in _BS.items():
    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]

MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
# --- 7日(10/30-11/05) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1105/ord7_raw.json から生成）---
ORD = {'伸縮ガラスクリーナー':121,'W固定スマホ車載ホルダー':103,'優先配送 (VIP特典)':116,'伸縮ワックス洗車ブラシ':76,'ナノガラス脱毛パッド':68,'マグネットドアクッション':54,
'ポータブルヒートシーラー':38,'4-in-1マルチクリーナー':30,'快適マジックインソール':29,'姿勢サポートチェア':19,'ワイド水切りワイパー':10,'高見えレザーヘッドレストフック':9,
'コードレスダブルミスト加湿器':7,'優先配送':4,'携帯電動シェーバー':3,'壁掛けディスペンサー':2,'2WAYシートボックス':2,'姿勢サポートベルト':1,
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':1,'高見えレザードアポケット':1,'ファスナー修理キット':1,'5WAY腰掛けファン':1,'健康サンダル':1,'1秒折り畳みチェア':1,
'コードレス毛玉クリーナー':1,'完全遮光・形状記憶':1,'ネックマッサージャー':1}
STORE_ORD7, STORE_SESS7 = 567, 19648   # 注文=ShopifyQL 7日直接・セッション=日次の合計
assert sum(ORD.values()) == 701, sum(ORD.values())   # 全店567より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）

# --- 30日(10/07-11/05) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1105/ord30_raw.json から生成）---
ORD30 = {'ナノガラス脱毛パッド':900,'伸縮ガラスクリーナー':499,'W固定スマホ車載ホルダー':457,'優先配送 (VIP特典)':480,'快適マジックインソール':285,'ポータブルヒートシーラー':139,
'伸縮ワックス洗車ブラシ':134,'4-in-1マルチクリーナー':121,'高見えレザーヘッドレストフック':100,'マグネットドアクッション':54,'姿勢サポートチェア':44,'ナノバブルシャワーヘッド':32,
'コードレスダブルミスト加湿器':25,'優先配送':23,'携帯電動シェーバー':17,'バランスケアスリッパ':15,'ネックマッサージャー':13,'壁掛けディスペンサー':13,
'むくみ取りかっさ':11,'ワイド水切りワイパー':10,'高見えレザードアポケット':9,'偏光・調光サングラス':6,'2WAYシートボックス':4,'完全遮光・形状記憶':4,
'姿勢サポートベルト':2,'形状記憶日傘':2,'UV歯ブラシ除菌器':2,'5WAY腰掛けファン':2,'健康サンダル':2,'スマートノーズEMS美顔器':1,
'ファスナー修理キット':1,'ヘアドライタオル':1,'4WAY 取り付けOK 小型瞬間冷却ハンディファン':1,'もちふわ肉球サンダル':1,'ロングニトリル家事手袋':1,'温感EMSフェイシャルワンド':1,
'1秒折り畳みチェア':1,'ムダ毛シェーバー':1,'コードレス毛玉クリーナー':1,'電動温熱カッサ':1,'オートソープディスペンサー':1}
assert sum(ORD30.values()) == 3417, sum(ORD30.values())

# --- 30日(10/07-11/05) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1105/mf30_raw.txt から生成）---
MF_RAW = {'ナノガラス脱毛パッド':(2006363,1656346,24087),'伸縮ガラスクリーナー':(1106642,397944,13762),
'W固定スマホ車載ホルダー':(1019758,454259,14378),'快適マジックインソール':(901516,569791,10179),
'ポータブルヒートシーラー':(324294,77576,4253),'高見えレザーヘッドレストフック':(320555,63721,2340),
'カタログ全部（テスト）':(273001,84916,2970),'4-in-1マルチクリーナー':(257793,118121,3895),
'伸縮ワックス洗車ブラシ':(257123,63722,2899),'姿勢サポートチェア':(168025,76209,2075),
'コードレスダブルミスト加湿器':(107957,25677,931),'マグネットドアクッション':(99198,29403,1364),
'ナノバブルシャワーヘッド':(96844,53388,1340),'バランスケアスリッパ':(65966,35896,685),
'ディスペンサー':(56463,15426,405),'ネックマッサージャー2':(54083,22201,374),
'携帯電動シェーバー':(43996,18917,409),'高見えレザードアポケット':(32026,7234,227),
'むくみ取りかっさ':(25825,7243,249),'ワイド水切りワイパー':(15959,5153,220),
'ふわとろ高密度ブランケット':(10366,3684,60),'コードレス毛玉クリーナー':(7993,3061,55),
'もちふわ肉球サンダル':(5869,995,64),'2WAYシートボックス':(5687,2443,42),
'健康サンダル':(5033,1946,36),'ハイウエストシェイプパンツ':(4923,777,22),
'ファスナー修理キット':(4492,1269,44),'ロングニトリル家事手袋':(4366,824,19),
'クリアビューレインガードフィルム':(1091,256,11),'UV歯ブラシ除菌器':(80,32,1)}
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
# 10月確定（10/31広告費の上書き後の最終値）と11月の滑り出し
AUG = [d for d in ALLD if '2026-10-01' <= d <= '2026-10-31']
assert len(AUG) == 31
_au = [dayblk(d) for d in AUG]
aus = sum(x[0] for x in _au); auc = sum(x[1] for x in _au); aua = sum(x[2] for x in _au); aup = aus-auc-aua
_cum = [dayblk(d) for d in CUM]
cs = sum(x[0] for x in _cum); cc = sum(x[1] for x in _cum); ca = sum(x[2] for x in _cum); cp = cs-cc-ca
p3ma = (sum(R['N3'].values()) - sum(R['K3'].values()) - R['ACCT3']) / 3
sh('収益', [f'LOOTY 収益レポート 2026-11-06（昨日 = 11/05 木）',
  f'★昨日の利益 {round(_pl[-1][3]):,}円（利益率 {_pl[-1][3]/_pl[-1][0]:.1%}・MER {_pl[-1][0]/_pl[-1][2]:.2f}）／手数料控除後 {round(_pl[-1][3]-_pl[-1][0]*FEE):,}円',
  f'★11月累積（11/01〜・{len(CUM)}日）: 実売 {cs:,.0f} / 利益 {cp:,.0f}円（{cp/cs:.1%}）／1日あたり {cp/len(CUM):,.0f}円（10月確定は {aup:,.0f}円・{aup/31:,.0f}円/日）',
  '★11/5(木)は 実売 **442,891円**・利益 **+111,026円（25.1%）**・MER 2.18。前週木10/29(443,760円・利益70,630円)比 −0.2%（利益は+40,396円）、祝日でない木曜平均(9/10〜10/29・8回 530,775円)比 −16.6%。利益は15日中7位。注文80件（前週木84）・来訪2,874（前週木3,259・前日2,387）・来訪→購入2.78%（前週木2.58%）。広告費203,228円（暫定）・CPM 2,266（前日2,467）・1LPVあたり87.2円（前日93.4）。10〜13時台が強く（注文21・6日平均14.7・gross+52%）、朝と夜は少なめ',
  '★注文80件・セッション2,874（前週木10/29 3,259・前日2,387）・CVR **2.78%**（前週木2.58%・前日2.93%）・カゴ投入率5.50%（158/2,874・15日 4.94〜6.58%）・チェックアウト完了率54.2%（77/142・15日 43.9〜61.8%）。点数/注文1.51（VIP特典19を含む・除くと1.28）・客単価5,536円。返品0件。VIP特典19件・7,000円以上20件(25.0%)・1万円以上4件',
  '⚠️ 3日移動平均 **107,687円/日**（11/3 +117,461・11/4 +94,573・11/5 +111,026）<130,000 → **ブレーキ継続**（合計を増やさない。いま192,000でブレーキ時の190,000を2,000上回る）。直近7日(10/30-11/5)利益789,976円（25.4%・前7日773,315円）。11月5日間 +609,552円（121,910円/日）',
  '🔁 11/5（ユーザー）: 01:10確認 毛玉停止・加湿器13,000→16,000・クリーナー主力18,000→16,000・インソール13,000→10,000／01時台 ナノバブル再開8,000 → 11:1x 停止（4,100円・0個）／12:56 ワイパー8,000→12,000／22時台 新商品クリアビューレインガードフィルム8,000（審査通過後 1,091円）→ 最終 **15セット・192,000円**（11/5 00時 190,000）。消化203,228円（暫定）',
  '✅ 本日（11/6 金）の判定: 加湿器2日目（11/4-5）CTR 3.36%（2.5〜4.5%の間）→ **継続**（7日判定11/11）／ワイパー2日目 CTR 4.27%（同）→ **継続**（2日で13個・倍率2.31）／毛玉は11/5に停止済み。日単位の目安（2日続けて1.25未満で2割減）: **シーラー**（11/4 0.77・11/5 0.83）＝10,000→8,000が基準どおりで、合計も190,000に戻る。次: 11/7 ドア7日・レインガード2日目 → 11/8 11/4の変更の答え合わせ → 11/9(月) 週次',
  '✅ 11/4広告費を確定上書き: 186,751→**187,231円**（+480）→ 11/4利益 +95,053→**+94,573円**に確定。11/5分203,228円は暫定・次回確定',
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
CAL = {'伸縮ガラスクリーナー': ('2026-11-08', '11/5 01:10 主力18,000→16,000（ユーザー・sabu 12,000据え置き・合計28,000）。11/5 19個・倍率1.80・+23,791円（11/4 1.40）。7日(10/30-11/5)倍率1.77・+196,116円。11/8: 11/4夜〜11/5の2段階の減額をまとめて答え合わせ（11/5-7）'),
       'W固定スマホ車載ホルダー': ('2026-11-08', '11/4 A 10,000・B 19,000（ユーザー）。11/5 13個・倍率1.18・+5,534円（11/4 1.83＝1日目の1.25未満）。7日1.53・+115,001円。11/8 配分の答え合わせ'),
       '壁掛けディスペンサー': ('2026-10-24', '📌停止（10/24判定）｜再開後7日(10/17-23)倍率0.98<1.25 → 宣言どおり停止（14個・−1,102円・返品0）。ユーザーがMetaで停止'),
       '4-in-1マルチクリーナー': ('2026-11-09', '11/5 8個・倍率3.20・+18,977円（11/4 2.33）。7日倍率2.17・+71,955円。11/9 週次（7日1.86以上かつ消化95%以上で+20%の候補）'),
       'ポータブルヒートシーラー': ('2026-11-06', '11/4 20:29 13,000→10,000（ユーザー）。11/5 3個・倍率0.83・−1,775円（11/4 0.77・11/3 0.82＝3日続けて1.25未満）。7日1.34。11/6: 10,000→8,000（−20%）が基準どおり'),
       '高見えレザーヘッドレストフック': ('2026-11-10', '11/3 13:30頃 ユーザーがキャンペーン停止（両セットともCPMが店の2〜3倍・原因は未確認）。11/3 0個・6,801円。7日(10/28-11/3)倍率1.17・+10,728円。11/10 停止の答え合わせ。再出稿の目安CPM4,500以下'),
       'ナノバブルシャワーヘッド': ('2026-10-26', '10/26 00:19 ユーザーが停止（先週倍率1.45・+24,768円）。再開はいつでも可'),
       'コードレスダブルミスト加湿器': ('2026-11-11', '11/5 01:10 13,000→16,000（ユーザー）。11/5 4個・倍率0.68・−5,642円（11/4 1.82＝1日目の1.25未満）。11/6判定: 2日目CTR 3.36%（2.5〜4.5%）→ 継続。11/11 7日（11/4-10）利益≥0で継続'),
       '高見えレザードアポケット': ('2026-10-29', '10/24 2日目判定: CTR3.09%＝延長も停止もしない帯。ユーザーが11,000へ増額済み。10/22-24 12個・倍率1.47・+11,588円（10/24は着地75・カート0・0個。実ブラウザでカート追加は正常）。10/29: 7日(10/22-28)の利益≥0で継続'),
       '伸縮ワックス洗車ブラシ': ('2026-11-08', '11/4 11:2x 20,000→23,000（ユーザー）。11/5 10個・倍率1.32・+7,882円（11/4 2.48）。7日(10/30-11/5)倍率1.88・+141,086円。11/8 増額の答え合わせ（11/5-7の増えた粗利÷増えた広告費）'),
       'バランスケアスリッパ': ('2026-10-27', '10/27 00:07 ユーザーが停止（再開1日 9,681円・2個・0.76）。再開はいつでも可'),
       'ナノガラス脱毛パッド': ('2026-11-09', '11/4 17:28 A 20,000→15,000（ユーザー）。11/5 13個・倍率2.38・+22,982円（11/4 1.21）。7日(10/30-11/5)倍率1.40。11/9 週次'),
       '姿勢サポートチェア': ('2026-11-09', '11/5 2個・倍率0.80・−1,831円（11/4 1.76＝1日目）。7日(10/30-11/5)倍率1.42・+32,129円。小さい商品のルール（2週続けて赤字で停止）'),
       '2WAYシートボックス': ('2026-10-29', '10/29 08:55 再開 → 17:45 ユーザーが停止（5,669円・購入0）。再開はいつでも可'),
       'マグネットドアクッション': ('2026-11-07', '11/4 20:29 19,000→15,000（ユーザー）。11/5 7個・倍率1.39・+6,441円。10/31-11/5 +110,435円・倍率2.11。11/7 7日（10/31-11/6）利益≥0で継続'),
       'ふわとろ高密度ブランケット': ('2026-11-01', '11/1 21:20頃 ユーザーが停止。2日 10,366円・カート0・購入0'),
       'ファスナー修理キット': ('2026-11-03', '11/3 11:30出稿8,000 → 〜22:59 ユーザーが停止。初日確定 4,476円・表示1,265・CTR3.48%・1個（倍率0.78）'),
       'コードレス毛玉クリーナー': ('2026-11-05', '11/5 01:10 キャンペーン停止（ユーザー）。再開後 4,210円（11/4 3,979・11/5 231）・広告経由0個（11/5に停止中で1個売れた）'),
       'ワイド水切りワイパー': ('2026-11-11', '11/5 12:56 8,000→12,000（ユーザー）。11/5 11個・倍率2.73・+19,522円。2日で13個・倍率2.31。11/6判定: 2日目CTR 4.27%（2.5〜4.5%）→ 継続。11/11 7日（11/4-10）'),
       'クリアビューレインガードフィルム': ('2026-11-07', '11/5 22時台 新規出稿8,000（ユーザー）。売価3,980・原価798・分岐CPA3,182・事故停止は購入0のまま9,546円。11/5 1,091円・表示256・クリック11・0個。11/7朝 2日目（実質の配信開始は11/5夜のため11/6終日で判定）・11/12 7日'),
       'むくみ取りかっさ': ('2026-10-21', '10/21判定済み: 再開後7日(10/14-20)倍率1.18 <1.25 → 停止。Metaは10/16から配信なし＝再開しない（期間利益+4,520円）'),
       '快適マジックインソール': ('2026-11-11', '11/5 01:10 13,000→10,000（ユーザー）。11/5 4個・倍率1.07・+813円（11/4 1.33＝1日目の1.25未満）。7日1.13。11/11 新CR 7日（11/4-10）'),}
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
 ['📊 11/5(木)','実売 **442,891円**・利益 **+111,026円（25.1%）**・MER2.18',
  '前週木比−0.2%（利益は+40,396円）・祝日でない木曜平均比−16.6%。7日利益789,976円（前7日773,315）で横ばい〜微増。10〜13時台が強い（注文21・gross+52%）','—','監視'],
 ['⚠️ ブレーキ継続','3日移動平均 **107,687円/日**（11/3 +117,461・11/4 +94,573・11/5 +111,026）',
  '130,000未満 → 合計を増やさない。いま192,000でブレーキ時の190,000を2,000上回る','—','毎日'],
 ['✂️ シーラー 2割減','11/3 0.82・11/4 0.77・11/5 0.83（3日続けて1.25未満）',
  '10,000→8,000（−20%）がユーザー基準どおり。合計も190,000に戻る','ユーザー','今日'],
 ['👀 1日目の1.25未満','車載1.18・インソール1.07・チェア0.80・加湿器0.68',
  '明日（11/6終日）も1.25未満なら2割減の候補。加湿器は11/5に16,000へ増額した初日','—','11/7'],
 ['🧪 新商品・再開','ワイパー 2日で13個・倍率2.31（12,000へ増額済み）／加湿器 2日CTR3.36%／レインガード 11/5夜開始',
  'ワイパー・加湿器は継続して11/11に7日判定。レインガードは事故停止9,546円・2日目判定は11/6終日で','—','11/7'],
 ['🔁 11/4〜5の変更の答え合わせ','減: ドア・ナノA・クリーナー（2段階）・シーラー・4-in-1・インソール／増: ブラシ・加湿器（2段階）・ワイパー',
  '11/8に11/5-7の3日で（減は倍率と来訪数、増は増えた粗利÷増えた広告費）','—','11/8'],
 ['🧪 ドアクッション 7日','10/31-11/5 +110,435円・倍率2.11',
  '11/7に7日（10/31-11/6）利益≥0で継続','—','11/7'],
 ['💰 まとめ買い・既存客','7,000円以上25.0%・1万円以上4件',
  'メール（MAIL1000）は準備待ち。ブレーキ中は広告費なしで売上を足せる手','ユーザー','随時'],
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
for lbl, N, K, ACC in [('前日 11/05(木)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/03-11/05', R['N3'], R['K3'], R['ACCT3']),
        ('7日 10/30-11/05', R['N7'], R['K7'], R['ACCT7']), ('30日 10/07-11/05', R['N30'], R['K30'], R['ACCT30']),
        ('11月 11/01-', R['NC'], R['KC'], R['ACCTC'])]:
    s = sum(N.values()); c = sum(K.values()); p = s - c - ACC
    SUMR.append([lbl, s, c, round(ACC), round(c + ACC), round((c + ACC) / s, 4), round(p), round(p / s, 4),
                 round(s / ACC, 2), round(1 / (1 - c / s), 2), round(s * FEE), round(p - s * FEE), round((p - s * FEE) / s, 4)])
sh('全体サマリー', ['全体サマリー（売上=Shopify gross−値引・広告費=Meta実測。返品は売上からも利益からも控除しない=A案）',
 '総合原価＝原価＋広告費。恒等式 総合原価率＋利益率＝100% が全窓で成立していることを確認済み',
 '縦照合3本すべて通過（11/05）: Σ商品gross=全店461,960 ／ Σ値引=19,069 ／ Σ広告費=キャンペーン合算203,228円（11/04も gross 418,140・値引20,162 で一致）',
 '✅ 11/04の広告費は再取得で確定済み（186,751→**187,231円**。11/06に上書き）',
 '⚠️ 11/05の広告費は 11/06 00時台の取得【暫定】→ 次回に再取得して確認する',
 '★ガラスクリーナーの原価は保守側の最高値バリアント単価で計上。ヘッドレストフックは10/7以降のCJ原価732円で計上（11/3にproduct_tabsの1,344を訂正）',
 '★11/5の返品は0件。★5e-2突合: 広告なしで売れた商品＝5WAY腰掛けファン2・ネックマッサージャー1・壁掛けディスペンサー1（3本）・携帯電動シェーバー1・4WAY 1・完全遮光・形状記憶 1・毛玉1（停止中）。広告費ありで売上0＝ナノバブル4,100円（11:1x停止）・レインガード1,091円（22時台開始）',
 '決済ブレンド率 **3.325%**（2026-11-02再計測: 直近100注文・SP 91.2%×3.25%・KOMOJUスマホ決済7.8%・Paidy1.1%×4.1%。前回3.388%。次回12/1）',
 f'7日の全店CVR（Shopifyセッション基準）= {STORE_ORD7}注文 ÷ {STORE_SESS7:,}セッション = {STORE_ORD7/STORE_SESS7:.2%}'],
 ['窓','実売','原価','広告費','総合原価','総合原価率','利益','利益率','MER','分岐MER','決済手数料','手数料控除後利益','手数料後利益率'],
 SUMR, [20,14,13,13,13,11,13,10,8,9,12,15,12],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'0.0%',7:'#,##0',8:'0.0%',9:'0.00',10:'0.00',11:'#,##0',12:'#,##0',13:'0.0%'})
ws = wb['全体サマリー']; r = ws.max_row + 3
ws.cell(r, 1, '■ 昨日(11/05 木) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1
S1 = sum(R['N1'].values()); C1 = sum(R['K1'].values()); A1 = R['ACCT1']
per = [('実売', S1, sum(R['N3'].values())/3, sum(R['N7'].values())/7, sum(R['N30'].values())/30),
       ('原価', C1, sum(R['K3'].values())/3, sum(R['K7'].values())/7, sum(R['K30'].values())/30),
       ('広告費', A1, R['ACCT3']/3, R['ACCT7']/7, R['ACCT30']/30),
       ('利益', S1-C1-A1, (sum(R['N3'].values())-sum(R['K3'].values())-R['ACCT3'])/3,
        (sum(R['N7'].values())-sum(R['K7'].values())-R['ACCT7'])/7,
        (sum(R['N30'].values())-sum(R['K30'].values())-R['ACCT30'])/30)]
for c, v in enumerate(['指標','11/05(木)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)
for c in range(1, 7):
    x = ws.cell(r, c); x.font = TH; x.fill = HEAD; x.border = thin; x.alignment = Alignment(horizontal='center')
r += 1
for lbl, d1, m3, m7, m30 in per:
    for c, v in enumerate([lbl, round(d1), round(m3), round(m7), round(m30), round(d1/m7-1, 4)], 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = NEG if (isinstance(v, (int, float)) and v < 0) else TD
        if c in (2,3,4,5): x.number_format = '#,##0'
        if c == 6: x.number_format = '+0.0%;-0.0%'
    r += 1
ws.cell(r+1, 1, '11/5(木)は実売442,891円・利益+111,026円（25.1%）・MER2.18。前週木比−0.2%（利益は+40,396円）。4-in-1 8個（倍率3.20）・ワイパー11個（2.73）・ナノ13個（2.38）・クリーナー19個（1.80）・ドア7個（1.39）・洗車ブラシ10個（1.32）・車載13個（1.18）・インソール4個（1.07）が黒字、シーラー3個（0.83）・チェア2個（0.80）・加湿器4個（0.68）・ナノバブル0個（4,100円・停止）・レインガード0個（1,091円・初日）が赤字。広告なしで5WAY2・ネック・ディスペンサー・携帯シェーバー・4WAY・日傘・毛玉が各1').font = Font(name='Arial', size=10, color='CC0000')

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
sh('商品別', ['商品別（7日 10/30-11/05 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',
  '分岐CPA(注文) = 1個あたり粗利 × 点数/注文。まとめ買い商品（点数/注文>1.2）は必ず注文ベースで比較する',
  'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,459,035円（11/05分は暫定）',
  '当月累積利益は11月分（11/01〜・5日目）',
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
sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/07-11/05)」。他シートの7日窓と混ぜて読まないこと',
  'クリックは **アウトバウンドクリック**（data_query 実測・Asia/Tokyo）',
  '✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/07-11/05) が許容差以内で一致（コード内assert）',
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
  '非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（最新の判定は「収益」シートのブレーキ列）'],
 ['日付','曜','実売','原価','広告費','利益','利益率','MER','3日移動平均利益','警告'],
 DD, [12,5,13,12,12,12,9,8,16,16], {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'0.0%',8:'0.00',9:'#,##0'})

# ---------- 9 本日の判定 ----------
JUDGE = [
 ['11/6(金)','加湿器 2日目（11/4-5）','CTR>4.5%延長／<2.5%かつカート0停止','CTR 3.36%（3.48%・3.29%）・Metaカート30','**継続**（7日判定11/11）','11/11 7日'],
 ['11/6(金)','ワイパー 2日目（11/4-5）','同上','CTR 4.27%（4.85%・4.07%）・13個・倍率2.31','**継続**（12,000へ増額済み）','11/11 7日'],
 ['11/6(金)','日単位の目安','前日の終日で・2日続けて1.25未満で2割減・1回2割まで','シーラー 11/4 0.77・11/5 0.83','**シーラー 10,000→8,000**（ユーザー判断）','11/9 週次'],
 ['11/6(金)','ブレーキ','3日移動平均 <130,000 で合計予算を増やさない','107,687円','**継続**（いま192,000・+2,000）','毎日確認'],
 ['11/7(土)','ドアクッション 7日（10/31-11/6）','利益≥0で継続','10/31-11/5 +110,435円','待機','—'],
 ['11/7(土)','レインガード 2日目','CTR>4.5%延長／<2.5%かつカート0停止・事故停止9,546円','11/5 CTR 4.30%（11/256）','待機','11/12 7日'],
 ['11/8(日)','11/4〜5の変更の答え合わせ（11/5-7）','減: 倍率と来訪数／増: 増えた粗利÷増えた広告費','—','待機','—'],
 ['11/9(月)','週次（11/2-8）','倍率の帯（ブラシ・ドア・4-in-1の増額は先週1.86以上かつ消化95%以上で+20%）','—','待機','—'],
 ['11/11(水)','インソール新CR・加湿器・ワイパー 7日（11/4-10）','利益≥0で継続','—','待機','—'],
]
sh('本日の判定', ['宣言済みの基準に当てはめるだけ。基準は宣言時のまま動かさない',
  '★本日(11/6 金): 判定 = 加湿器・ワイパー2日目（どちらも継続）。⚠️ブレーキ継続（3日移動平均107,687）→ 合計は190,000まで（いま192,000）。日単位の目安で2日続けて1.25未満はシーラーのみ → 10,000→8,000（−20%）で基準どおり・合計も190,000に戻る。1日目の1.25未満: 車載1.18・インソール1.07・チェア0.80・加湿器0.68（明日も1.25未満なら2割減の候補）',
  '★次: 11/7(土) ドアクッション7日（10/31-11/6）・レインガード2日目 → 11/8(日) 11/4〜5の変更の答え合わせ（11/5-7）→ 11/9(月) 週次（11/2-8）→ 11/11(水) インソール新CR・加湿器・ワイパー7日 → 11/12(木) レインガード7日',
  '★倍率の定義: **MER ÷ 分岐MER**。1.0未満＝赤字',
  '★10月確定: 31日で+4,174,310円（26.0%・134,655円/日）。11月は5日で+609,552円（121,910円/日）'],
 ['判定日','対象','宣言済み基準','実測','結果','備考'], JUDGE, [10,26,34,34,16,46])

# ---------- 9a 予算見直しチェック（9/1 → 9/2 の差分）----------
PREVB = collections.defaultdict(int)
for r in body:
    if r[0] == '2026-11-05': PREVB[r[1]] += int(r[3])
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
sh('予算見直しチェック', ['前日(11/05 00時・2026-11-05)スナップショット → 本日(11/06 00時台・Meta読み)。11/05の変更: 01:10 毛玉停止・加湿器増額・クリーナー主力減・インソール減／01時台 ナノバブル再開→11時台停止／12:56 ワイパー増額／22時台 レインガード新規',
  '合計 190,000 → **192,000円/日**（+2,000＝レインガード+8,000・ワイパー+4,000・加湿器+3,000／毛玉−8,000・インソール−3,000・クリーナー−2,000）',
  '★体制: 15セット・192,000円/日（⚠️ブレーキ継続: 3日移動平均107,687円 <130,000 → 合計を増やさない。ブレーキ時の190,000を2,000上回る）',
  '★11/05の消化は 203,228円（暫定）。11/04は確定187,231円、11/03は確定212,735円',
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
'2026-08-28':3149,'2026-08-29':3537,'2026-08-30':3310,'2026-08-31':2761,'2026-09-01':2936,'2026-09-02':3142,'2026-09-03':3340,'2026-09-04':3293,'2026-09-05':3217,'2026-09-06':3752,'2026-09-07':2787,'2026-09-08':2739,'2026-09-09':2801,'2026-09-10':3514,'2026-09-11':3014,'2026-09-12':3132,'2026-09-13':4246,'2026-09-14':3592,'2026-09-15':3358,'2026-09-16':3348,'2026-09-17':3418,'2026-09-18':3583,'2026-09-19':4088,'2026-09-20':4310,'2026-09-21':4571,'2026-09-22':3877,'2026-09-23':4043,'2026-09-24':3257,'2026-09-25':3236,'2026-09-26':4416,'2026-09-27':5017,'2026-09-28':3841,'2026-09-29':3426,'2026-09-30':3276,'2026-10-01':4124,'2026-10-02':3619,'2026-10-03':3578,'2026-10-04':4506,'2026-10-05':3394,'2026-10-06':3904,'2026-10-07':3692,'2026-10-08':3530,'2026-10-09':3218,'2026-10-10':3685,'2026-10-11':3163,'2026-10-12':3794,'2026-10-13':3140,'2026-10-14':3501,'2026-10-15':3231,'2026-10-16':2914,'2026-10-17':3529,'2026-10-18':3863,'2026-10-19':3094,'2026-10-20':3176,'2026-10-21':3223,'2026-10-22':3470,'2026-10-23':3054,'2026-10-24':3560,'2026-10-25':4375,'2026-10-26':3923,'2026-10-27':3198,'2026-10-28':3703,'2026-10-29':3259,'2026-10-30':2651,'2026-10-31':2660,'2026-11-01':2916,'2026-11-02':2801,'2026-11-03':3359,'2026-11-04':2387,'2026-11-05':2874}
ORDD = {'2026-08-04':188,'2026-08-05':152,'2026-08-06':157,'2026-08-07':173,'2026-08-08':184,'2026-08-09':187,
'2026-08-10':141,'2026-08-11':176,'2026-08-12':124,'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,
'2026-08-16':143,'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,
'2026-08-22':98,'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,
'2026-08-28':85,'2026-08-29':115,'2026-08-30':114,'2026-08-31':84,'2026-09-01':88,'2026-09-02':92,'2026-09-03':103,'2026-09-04':74,'2026-09-05':106,'2026-09-06':122,'2026-09-07':96,'2026-09-08':95,'2026-09-09':98,'2026-09-10':116,'2026-09-11':96,'2026-09-12':117,'2026-09-13':140,'2026-09-14':102,'2026-09-15':103,'2026-09-16':99,'2026-09-17':100,'2026-09-18':96,'2026-09-19':122,'2026-09-20':135,'2026-09-21':150,'2026-09-22':117,'2026-09-23':128,'2026-09-24':107,'2026-09-25':102,'2026-09-26':142,'2026-09-27':156,'2026-09-28':117,'2026-09-29':96,'2026-09-30':110,'2026-10-01':141,'2026-10-02':113,'2026-10-03':111,'2026-10-04':129,'2026-10-05':102,'2026-10-06':124,'2026-10-07':100,'2026-10-08':92,'2026-10-09':85,'2026-10-10':127,'2026-10-11':112,'2026-10-12':114,'2026-10-13':100,'2026-10-14':91,'2026-10-15':100,'2026-10-16':85,'2026-10-17':114,'2026-10-18':108,'2026-10-19':93,'2026-10-20':76,'2026-10-21':104,'2026-10-22':112,'2026-10-23':102,'2026-10-24':105,'2026-10-25':125,'2026-10-26':95,'2026-10-27':94,'2026-10-28':83,'2026-10-29':84,'2026-10-30':72,'2026-10-31':70,'2026-11-01':112,'2026-11-02':75,'2026-11-03':88,'2026-11-04':70,'2026-11-05':80}
CV = [[d, WDJ[datetime.date.fromisoformat(d).weekday()], SES[d], ORDD[d], round(ORDD[d]/SES[d], 4),
       ('★昨日（木曜・CVR 2.78%・注文80件・10〜13時台が強い）' if d == '2026-11-05' else '（水曜・CVR 2.93%・注文70件・来訪は16日で最少だが来訪後は強い）' if d == '2026-11-04' else '（火曜・文化の日・CVR 2.62%・注文88件・来訪は多いがカゴ投入率が下端）' if d == '2026-11-03' else '（月曜・CVR 2.68%・注文75件・来訪が少ない＋13〜15時台の穴）' if d == '2026-11-02' else '（日曜・CVR 3.84%・注文112件・来訪後の割合が15日で最高）' if d == '2026-11-01' else '（土曜・CVR 2.63%・注文70件・来訪が少ない）' if d == '2026-10-31' else '（金曜・CVR 2.72%・注文72件だが客単価6,191円）' if d == '2026-10-30' else '（木曜・CVR 2.58%・ナノの購入率が08時から低下）' if d == '2026-10-29' else '（水曜・CVR 2.24%・表示が15日最低）' if d == '2026-10-28' else '（火曜・CVR 2.94%・朝の配信不足）' if d == '2026-10-27' else '（月曜・CVR 2.42%・20時以降に急落）' if d == '2026-10-26' else '（土曜・CVR 2.95%・ナノBC約7.5時間停止）' if d == '2026-10-24' else '（金曜・CVR 3.34%・洗車ブラシ新規）' if d == '2026-10-23' else '（木曜・CVR 3.23%・ドアポケット新規）' if d == '2026-10-22' else '（水曜・CVR 3.23%・前日から全面回復）' if d == '2026-10-21' else '（火曜・CVR 2.39%・81日で実売最低）' if d == '2026-10-20' else '（月曜・CVR 3.01%・プライム感謝祭最終日）' if d == '2026-10-19' else '（日曜・CVR 2.80%・プライム感謝祭本番3日目）' if d == '2026-10-18' else '（土曜・CVR 3.23%・プライム感謝祭本番2日目）' if d == '2026-10-17' else '（金曜・CVR 2.92%・プライム感謝祭本番1日目）' if d == '2026-10-16' else '（木曜・CVR 3.09%・プライム先行最終日）' if d == '2026-10-15' else '（水曜・CVR 2.60%・プライム先行2日目）' if d == '2026-10-14' else '（火曜・CVR 3.18%・セッション−20%）' if d == '2026-10-13' else '（月曜・CVR 3.00%・ヒートシーラー出稿）' if d == '2026-10-12' else '（日曜・CVR 3.54%・セッション−30%）' if d == '2026-10-11' else '（土曜・CVR 3.45%・減額テスト初日）' if d == '2026-10-10' else '（金曜・CVR 2.64%・VIP7,000円化）' if d == '2026-10-09' else '（木曜・CVR 2.61%・まとめ買い切替日）' if d == '2026-10-08' else '（水曜・CVR 2.71%）' if d == '2026-10-07' else '（火曜・CVR 3.18%）' if d == '2026-10-06' else '（月曜・CVR 3.01%）' if d == '2026-10-05' else '（日曜・CVR 2.86%）' if d == '2026-10-04' else '（土曜・CVR 3.10%）' if d == '2026-10-03' else '（金曜・CVR 3.12%）' if d == '2026-10-02' else '（木曜・CVR 3.42%）' if d == '2026-10-01' else '（水曜・CVR 3.36%）' if d == '2026-09-30' else '（火曜・注文96件）' if d == '2026-09-29' else '（月曜・CVR 3.05%）' if d == '2026-09-28' else '（9月最高益・CVR 3.07%）' if d == '2026-09-27' else '（土曜・CVR 3.15%）' if d == '2026-09-26' else '（平日2日目・CVR 3.18%＝答え合わせ確定）' if d == '2026-09-25' else '（平日初日・CVR 3.16%）' if d == '2026-09-24' else '（秋分の日・CVR 3.17%）' if d == '2026-09-23' else '（国民の休日・CVR 3.02%）' if d == '2026-09-22' else '（敬老の日・CVR 3.28%・9月最高利益日）' if d == '2026-09-21' else '（日曜・CVR 3.13%）' if d == '2026-09-20' else '（マラソン初日・CVR 2.98%）' if d == '2026-09-19' else '' if d in ('2026-09-14','2026-09-15','2026-09-16','2026-09-17','2026-09-18') else '（セッション4,246・注文140＝9月最多）' if d == '2026-09-13' else '（CVR 3.74%・9月最高）' if d == '2026-09-12'
        else '（−2σトリガー発動日）' if d == '2026-09-04' else '')] for d in sorted(SES)]
sh('CVR推移', ['全店CVR = Shopify注文 ÷ Shopifyセッション。商品別レポートのCVR（注文÷Metaクリック）とは分母が違うので混ぜないこと',
  '★11/5は セッション2,874・注文80件 = **CVR 2.78%**（前週木2.58%・10/21-11/4の15日は2.24〜3.84%＝範囲内）。時間別: 0〜5時台 注文9（6日平均9.0）・6〜9時台 15（18.3）・**10〜13時台 21（14.7・gross+52%）**・14〜17時台 16（15.7）・18〜23時台 19（23.5・gross−6%）。0〜5時台は広告費+36%（6日平均比）',
  '★チェックアウト完了率: 11/4 51.9%（69/133）→ 11/5 **54.2%**（77/142・15日 43.9〜61.8%＝範囲内）。カゴ投入率 **5.50%**（158/2,874・15日 4.94〜6.58%）。Meta計上のカート追加÷LPVは 11/4 11.83%（237/2,004）→ 11/5 **9.48%**（221/2,330・暫定）。CPM 2,467→2,266円・CTR 2.81→2.95%・1LPVあたり 93.4→87.2円＝来訪は前日より安く多く入った',
  '★点数/注文 1.51（121/80・VIP特典19を含む）・客単価5,536円（前週木5,283・前日5,685）・値引19,069円（gross比4.1%・前日4.8%）。7,000円以上の注文 20件（25.0%・前日18件 25.7%）・1万円以上4件（前日8件）',
  '★セッション2,700〜3,800/日 は日予算240,000〜253,000円体制の水準。日予算590,000だった8月上旬(5,000〜6,600)と比べない'],
 ['日付','曜','セッション','注文','全店CVR','備考'], CV, [12,5,12,10,10,20],
 {3:'#,##0',4:'#,##0',5:'0.00%'})

# ---------- 11 曜日指数 ----------
_ix = sorted(R['IDX'].items(), key=lambda x: -x[1])
_hi, _lo = _ix[0], _ix[-1]
sh('曜日指数', ['直近30日(10/07-11/05)・祝日除外（10/12スポーツの日・11/3文化の日を除外）。売上=gross−値引。次回定期更新11/9(月)',
  '★同曜日平均との比較は当面使わない（8月上旬の高予算期が窓に混ざるため）。「前週同曜日比」で読む',
  '★11/5(木)は祝日でない木曜平均(530,775円)比−16.6%・前週木(10/29)比−0.2%。曜日指数（10/7〜11/5・祝日除外）: 日121.0・土108.2・木100.0・水94.2・金93.9・月91.1・火87.7'],
 ['曜日','指数(全体=100)'], [[k, round(v, 1)] for k, v in _ix], [10, 16])


# ---------- 時間別（11/05 vs 前週木10/29 vs 10/30-11/04平均。Meta時間別 data_query / Shopify TIMESERIES hour 実測）----------
import json as _json
_H = _json.load(open('scripts/daily/hourly1105.json'))
sh('時間別', ['時間帯別の比較: 11/5(木) vs 前週木(10/29) vs 直近6日(10/30-11/4)平均。広告=Meta時間別（11/5は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',
  '読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/5は0〜5時台の広告費が6日平均より多く（+36%）、6〜13時台は少なめ（−8%・−12%）。注文は 0〜5時台 9（6日平均9.0）・6〜9時台 15（18.3）・10〜13時台 21（14.7・gross+52%）・14〜17時台 16（15.7）・18〜23時台 19（23.5）＝昼前後が強く、朝と夜は少なめ',
  '⚠️ 日中の比率（gross÷広告）は参考。判断は終日と週で行う'],
 ['時間帯','広告 11/05','広告 10/29','広告 6日平均','表示 11/05','表示 10/29','表示 6日平均','LPV 11/05','LPV 10/29','LPV 6日平均','Meta購入 11/05','Meta購入 10/29','Meta購入 6日平均',
  'gross 11/05','gross 10/29','gross 6日平均','注文 11/05','注文 10/29','注文 6日平均','gross÷広告 11/05','gross÷広告 10/29','gross÷広告 6日平均','セッション 11/05','カート 11/05'],
 _H['rows'], [10,10,10,10,10,10,10,9,9,9,9,9,9,11,11,11,8,8,8,9,9,9,10,8],
 {2:'#,##0',3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0',7:'#,##0',8:'#,##0',9:'#,##0',10:'#,##0',14:'#,##0',15:'#,##0',16:'#,##0',20:'0.00',21:'0.00',22:'0.00'})
wb.save('data/reports/report-2026-11-06.xlsx')
print('シート:', wb.sheetnames)
print(f"前日利益 {round(_pl[-1][3]):,} / 3日移動平均 {p3ma:,.0f}円 / 10月確定(近似原価) {aup:,.0f}円")
