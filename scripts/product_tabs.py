# -*- coding: utf-8 -*-
"""商品別の日次タブを持つExcelを生成する。
使い方: python3 product_tabs.py <daily_sales.csv> <daily_ad.csv> <out.xlsx>
  daily_sales.csv: date,name,gross,disc   （Shopify実測・商品別日次）
  daily_ad.csv:    date,campaign,cost     （Meta実測・キャンペーン別日次）
タブ構成: 一覧（全商品サマリー）＋ 商品ごとに1タブ ＋ カタログ全部 ＋ 非広告商品
各商品タブ: 日付/曜日/曜日指数/売上(gross-値引)/値引/販売数/原価/広告費/利益/利益率/MER/曜日補正MER/日予算/消化率/メモ
"""
import csv, sys, collections, datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SALES, AD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
INTO = sys.argv[4] if len(sys.argv) > 4 else None   # 既存ブックに商品タブを追記する場合はそのパス
SNAP = '/home/user/LOOana/data/budget-snapshots.csv'

COST = {'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
 '接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
 '接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
 '携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
 '優先配送':0,'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'W固定スマホ車載ホルダー':1182,'ネックマッサージャー':3034,
 'リカバリーサンダル':1309,'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648,
 # 加重平均（バリエーション構成が日次で取れないため30日実測ミックスで加重）
 'ナノガラス脱毛パッド':751, '壁掛けディスペンサー':2358}
PRICE = {'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
 '接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
 '接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
 'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
 '完全遮光・接触冷感UVハット':5980,'ナノバブルシャワーヘッド':6980,'ネックマッサージャー':9980,
 'リカバリーサンダル':3980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,'優先配送':536,
 'ナノガラス脱毛パッド':3980, '壁掛けディスペンサー':6556, 'ムダ毛シェーバー':None,
 'W固定スマホ車載ホルダー':3980, '完全遮光・接触冷感UVハット':None}   # None=売価が窓内で変動
BLENDED = {'完全遮光・接触冷感UVハット':'2026-07-31に新規出稿開始。同日に売価5,980→4,980円へ値下げしたため、販売数は日付に応じた売価で算出',
           'W固定スマホ車載ホルダー':'2026-08-01に新規出稿開始（通年商品）。売価3,980円・原価1,182円・原価率29.7%・分岐CPA2,798円・分岐MER1.42・目標MER2.83',
           'ナノガラス脱毛パッド':'原価は白/緑757円・黒/桃740円の30日実測ミックスで加重平均（751円）。4期間サマリーはバリエーション別実数量の正確値',
           'ムダ毛シェーバー':'売価は7/27に5,980→6,980円へ値上げ。販売数は日付に応じた売価で算出（値上げ当日7/27のみ新旧混在を分解: 旧1個+新5個=6個）',
           '壁掛けディスペンサー':'日次の売価・原価は3本セット(6,980/2,528円)と2本セット(5,980/1,981円)の30日実測ミックスで加重平均。'
                            '販売数・原価は日次では概算になる（4期間サマリーはバリエーション別実数量の正確値）'}
# Shopify商品名 → Metaキャンペーン名
CAMP = {'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
        '3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
TAB = {'4WAY':'4WAY','害虫ブロッカー':'害虫ブロッカー','形状記憶日傘':'形状記憶日傘',
 'ナノガラス脱毛パッド':'ナノガラス脱毛パッド','完全遮光・形状記憶':'完全遮光UV日傘','接触冷感UVパーカー':'UVパーカー',
 '卓上冷感クーラー':'卓上冷感クーラー','5WAY腰掛けファン':'5WAY腰掛けファン','偏光・調光サングラス':'サングラス',
 '接触冷感UVアームカバー':'UVアームカバー','3WAYサーキュレーター':'3WAYサーキュレーター','瞬間冷感ポンチョ':'瞬間冷感ポンチョ',
 'ムダ毛シェーバー':'ムダ毛シェーバー','健康サンダル':'健康サンダル','UV歯ブラシ除菌器':'UV歯ブラシ除菌器',
 '携帯電動シェーバー':'携帯電動シェーバー','バランスケアスリッパ':'バランスケアスリッパ','壁掛けディスペンサー':'壁掛けディスペンサー',
 '湯上がりガーゼワンピース':'湯上がりワンピース',
 '完全遮光・接触冷感UVハット':'UVハット','W固定スマホ車載ホルダー':'車載ホルダー'}
EVENTS = {('害虫ブロッカー','2026-07-27'):'CRを1本→3本に追加',
          ('4WAY','2026-07-29'):'予備CR(広告B)を1本追加',
          ('ナノガラス脱毛パッド','2026-07-29'):'増額 68,000→76,000（メインセット55,000→63,000）',
          ('接触冷感UVアームカバー','2026-07-28'):'CRを1本追加',
          ('携帯電動シェーバー','2026-07-28'):'CRを1本追加',
          ('UV歯ブラシ除菌器','2026-07-23'):'複製リセット(A-コピー)投入',
          ('ムダ毛シェーバー','2026-07-27'):'値上げ 5,980→6,980円',
          ('卓上冷感クーラー','2026-07-27'):'LP改修（不安解消ブロック追加）',
          ('壁掛けディスペンサー','2026-07-28'):'LP全面改修＋価格メリット刷新',
          ('湯上がりガーゼワンピース','2026-07-26'):'キャンペーン停止',
          ('完全遮光・接触冷感UVハット','2026-07-31'):'新規出稿開始（日予算8,000）＋売価 5,980→4,980へ値下げ',
          ('W固定スマホ車載ホルダー','2026-08-01'):'新規出稿開始（日予算8,000・分岐CPA2,798円・通年商品）',
          ('害虫ブロッカー','2026-08-01'):'本体セット減額 60,000→43,000'}
HOLIDAYS = {'2026-07-20':'海の日'}
WD = ['月','火','水','木','金','土','日']

# ---- 読み込み ----
S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0,0]))   # [name][date] = [gross, disc]
for r in csv.DictReader(open(SALES, encoding='utf-8')):
    S[r['name']][r['date']][0] += int(r['gross']); S[r['name']][r['date']][1] += int(r['disc'])
A = collections.defaultdict(lambda: collections.defaultdict(float))            # [campaign][date] = cost
for r in csv.DictReader(open(AD, encoding='utf-8')):
    A[r['campaign']][r['date']] += float(r['cost'])
B = collections.defaultdict(lambda: collections.defaultdict(int))              # [campaign][date] = daily budget
for r in csv.DictReader(open(SNAP, encoding='utf-8')):
    B[r['campaign']][r['snapshot_date']] += int(r['daily_budget'])

DATES = sorted({d for v in S.values() for d in v})
def wd(d): return WD[datetime.date(*map(int, d.split('-'))).weekday()]
# 曜日指数（祝日を除外して算出）
store = {d: sum(v[d][0]-v[d][1] for v in S.values() if d in v) for d in DATES}
base = [d for d in DATES if d not in HOLIDAYS]
byw = collections.defaultdict(list)
for d in base: byw[wd(d)].append(store[d])
avg = sum(store[d] for d in base)/len(base)
IDX = {k: sum(v)/len(v)/avg*100 for k, v in byw.items()}

# ---- スタイル ----
wb = load_workbook(INTO) if INTO else Workbook()
TH = Font(name='Arial', bold=True, color='FFFFFF', size=10)
TD = Font(name='Arial', size=10)
NEG = Font(name='Arial', size=10, color='CC0000')
HEAD = PatternFill('solid', fgColor='305496')
ALT = PatternFill('solid', fgColor='F2F6FC')
GREEN = PatternFill('solid', fgColor='D6EFD8')
RED = PatternFill('solid', fgColor='FADBD8')
YEL = PatternFill('solid', fgColor='FFF2A8')
GRAY = PatternFill('solid', fgColor='EDEDED')
thin = Border(*[Side(style='thin', color='CCCCCC')]*4)

def header(ws, row, n):
    for c in range(1, n+1):
        x = ws.cell(row, c); x.font = TH; x.fill = HEAD; x.border = thin
        x.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

def _mixed_qty(g, p_old, p_new):
    """新旧売価が混在する日の販売数を解く（a×旧 + b×新 = gross）"""
    for b in range(0, g // p_new + 1):
        rem = g - b * p_new
        if rem % p_old == 0:
            return rem // p_old + b
    return None

def series(name):
    """その商品の日次系列を返す"""
    camp = CAMP.get(name, name)
    out = []
    for d in DATES:
        g, dc = S[name].get(d, [0, 0])
        sales = g - dc
        cost_ad = A[camp].get(d, 0.0)
        p = PRICE.get(name)
        if name == 'ムダ毛シェーバー' and g:      # 7/27に5,980→6,980へ値上げ（日付対応の売価で算出）
            if d < '2026-07-27': q = round(g / 5980)
            elif g % 6980 == 0:  q = g // 6980
            else:                q = _mixed_qty(g, 5980, 6980)   # 値上げ当日の新旧混在
        elif name == '完全遮光・接触冷感UVハット' and g:   # 7/31に5,980→4,980へ値下げ
            if d < '2026-07-31': q = round(g / 5980)
            elif g % 4980 == 0:  q = g // 4980
            else:                q = _mixed_qty(g, 5980, 4980)
        elif p:
            q = round(g / p)
        else:                       # 窓内で売価が変動し構成が解けない商品は数量を出さない
            q = None
        cost = q * COST.get(name, 0) if q is not None else None
        profit = sales - (cost or 0) - cost_ad
        bud = B.get(camp, {}).get(d)
        out.append(dict(date=d, wd=wd(d), idx=IDX[wd(d)], sales=sales, disc=dc, qty=q,
                        cost=cost, ad=cost_ad, profit=profit, bud=bud))
    return out

def block(rows, days):
    s = sum(r['sales'] for r in rows[-days:]); c = sum((r['cost'] or 0) for r in rows[-days:])
    a = sum(r['ad'] for r in rows[-days:])
    return s, c, round(a), round(s-c-a)

ADV = [n for n in TAB if any(A[CAMP.get(n, n)].values())]
ADV.sort(key=lambda n: -sum(v[0]-v[1] for v in S[n].values()))

# ---- Sheet: 一覧 ----
if INTO:
    ws = wb.create_sheet('一覧')
else:
    ws = wb.active; ws.title = '一覧'
ws['A1'] = f'LOOTY 商品別 日次パフォーマンス（{DATES[0]}〜{DATES[-1]}・全てShopify/Metaの実測）'
ws['A1'].font = Font(name='Arial', bold=True, size=13)
ws['A2'] = '各商品タブに日次の 売上／値引／販売数／原価／広告費／利益／利益率／MER／曜日補正MER／日予算／消化率 を載せています。'
ws['A3'] = '曜日指数（祝日7/20を除外した実測）: ' + '・'.join(f'{k}{v:.1f}' for k, v in sorted(IDX.items(), key=lambda x: -x[1]))
r = 5
hh = ['商品', '売価', '単価原価', '原価率(30日)', '分岐MER', '目標MER',
      '30日売上', '30日原価', '30日広告費', '30日利益', '30日利益率', '30日MER',
      '7日売上', '7日広告費', '7日利益', '7日MER', '前日利益', '現日予算']
for c, v in enumerate(hh, 1): ws.cell(r, c, v)
header(ws, r, len(hh)); r += 1
for n in ADV:
    rows = series(n)
    s30, c30, a30, p30 = block(rows, 30); s7, c7, a7, p7 = block(rows, 7)
    p1 = rows[-1]['profit']
    cr = c30/s30 if s30 else 0
    br = round(1/(1-cr), 2) if cr < 1 else ''
    tg = round(1/(1-cr-0.35), 2) if 1-cr-0.35 > 0 else ''
    bud = B.get(CAMP.get(n, n), {}).get(DATES[-1])
    vals = [n, PRICE.get(n) or '変動', COST.get(n, 0), round(cr, 4), br, tg,
            s30, c30, a30, p30, round(p30/s30, 4) if s30 else '', round(s30/a30, 2) if a30 else '',
            s7, a7, p7, round(s7/a7, 2) if a7 else '', round(p1), bud or '']
    for c, v in enumerate(vals, 1):
        x = ws.cell(r, c, v); x.border = thin; x.font = TD
        if isinstance(v, (int, float)) and v < 0 and c in (10, 11, 15, 17): x.font = NEG
        if c in (7, 8, 9, 10, 13, 14, 15, 17, 2, 3, 18): x.number_format = '#,##0'
        if c in (4, 11): x.number_format = '0.0%'
        if c in (5, 6, 12, 16): x.number_format = '0.00'
    if isinstance(br, float) and a30:
        ws.cell(r, 12).fill = GREEN if s30/a30 >= (tg or 99) else (RED if s30/a30 < br else YEL)
    r += 1
for col, w in zip('ABCDEFGHIJKLMNOPQR', [26,9,9,11,9,9, 12,11,12,12,11,9, 11,11,11,9, 11,11]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = 'B6'

# ---- 商品ごとのタブ ----
PH = ['日付','曜日','曜日指数','売上(gross−値引)','値引','販売数','売価(実測)','単価原価','原価','原価率',
      '広告費','利益','利益率','MER','曜日補正MER','日予算','消化率','メモ']
for n in ADV:
    rows = series(n)
    w = wb.create_sheet(TAB[n][:31])
    w['A1'] = n; w['A1'].font = Font(name='Arial', bold=True, size=13)
    s30, c30, a30, p30 = block(rows, 30)
    cr = c30/s30 if s30 else 0
    br = 1/(1-cr) if cr < 1 else 0
    tg = 1/(1-cr-0.35) if 1-cr-0.35 > 0 else 0
    if s30 > 0:
        w['A2'] = (f'売価 {PRICE.get(n) or "窓内で変動"}円 ／ 単価原価 {COST.get(n,0):,}円 ／ '
                   f'原価率(30日) {cr*100:.1f}% ／ 分岐MER {br:.2f} ／ 目標MER {tg:.2f}')
    else:   # 30日窓に売上がない新商品は実測から比率を出せない（0%と誤表示しない）
        _cr = COST.get(n,0)/PRICE[n] if PRICE.get(n) else None
        w['A2'] = (f'売価 {PRICE.get(n) or "窓内で変動"}円 ／ 単価原価 {COST.get(n,0):,}円 ／ '
                   + (f'原価率(定価ベース) {_cr*100:.1f}% ／ 分岐MER {1/(1-_cr):.2f} ／ 目標MER {1/(1-_cr-0.35):.2f}'
                      if _cr else '原価率・分岐・目標 = 30日窓に売上なしのため算出不可')
                   + ' ※30日窓に売上がないため実測比率ではなく定価から算出')
    if n in BLENDED:
        w['A3'] = '※ ' + BLENDED[n]; w['A3'].font = Font(name='Arial', size=9, color='CC0000')
    rr = 5
    w.cell(rr, 1, '■ 期間サマリー').font = Font(name='Arial', bold=True, size=11); rr += 1
    sh = ['期間', '売上', '原価', '広告費', '利益', '利益率', 'MER', '余裕(MER−分岐)']
    for c, v in enumerate(sh, 1): w.cell(rr, c, v)
    header(w, rr, len(sh)); rr += 1
    for lbl, dd in [(f'前日({DATES[-1][5:]})', 1), (f'3日({DATES[-3][5:]}-{DATES[-1][5:]})', 3), (f'7日({DATES[-7][5:]}-{DATES[-1][5:]})', 7), (f'30日({DATES[-30][5:]}-{DATES[-1][5:]})', 30)]:
        s, c_, a, p = block(rows, dd)
        vals = [lbl, s, c_, a, p, round(p/s, 4) if s else '', round(s/a, 2) if a else '',
                round(s/a - br, 2) if a and br else '']
        for c, v in enumerate(vals, 1):
            x = w.cell(rr, c, v); x.border = thin; x.font = NEG if (isinstance(v,(int,float)) and v < 0 and c in (5,6,8)) else TD
            if c in (2,3,4,5): x.number_format = '#,##0'
            if c == 6: x.number_format = '0.0%'
            if c in (7,8): x.number_format = '0.00'
        rr += 1
    rr += 1
    w.cell(rr, 1, '■ 日次').font = Font(name='Arial', bold=True, size=11); rr += 1
    for c, v in enumerate(PH, 1): w.cell(rr, c, v)
    header(w, rr, len(PH)); w.row_dimensions[rr].height = 28; rr += 1
    top = rr
    for i, x in enumerate(rows):
        memo = []
        if x['date'] in HOLIDAYS: memo.append(f'祝日({HOLIDAYS[x["date"]]})')
        prev = rows[i-1]['bud'] if i else None
        if x['bud'] is not None and prev is not None and x['bud'] != prev:
            memo.append(f'日予算 {prev:,}→{x["bud"]:,}円')
        if x['bud'] and (x['ad']/x['bud'] > 1.8 or x['ad']/x['bud'] < 0.4):
            memo.append('⚠️消化率が異常（当日中の予算変更 or 開始初日 or スナップショット欠落を確認）')
        if (n, x['date']) in EVENTS: memo.append(EVENTS[(n, x['date'])])
        mer = x['sales']/x['ad'] if x['ad'] else None
        gross = x['sales'] + x['disc']
        unit_price = round(gross / x['qty']) if x['qty'] else ''          # その日の実測売価（値引前）
        unit_cost  = round(x['cost'] / x['qty']) if x['qty'] else ''      # その日の実測単価原価（バリアント加重後）
        cost_rate  = round(x['cost'] / x['sales'], 4) if x['sales'] and x['cost'] else ''
        vals = [x['date'], x['wd'], round(x['idx'], 1), x['sales'], x['disc'], x['qty'],
                unit_price, unit_cost, x['cost'], cost_rate,
                round(x['ad']), round(x['profit']),
                round(x['profit']/x['sales'], 4) if x['sales'] else '',
                round(mer, 2) if mer else '', round(mer/(x['idx']/100), 2) if mer else '',
                x['bud'] or '', round(x['ad']/x['bud'], 3) if x['bud'] else '', ' ／ '.join(memo)]
        for c, v in enumerate(vals, 1):
            cell = w.cell(rr, c, v); cell.border = thin
            cell.font = NEG if (isinstance(v, (int, float)) and v < 0 and c in (12, 13)) else TD
            if i % 2 == 1: cell.fill = ALT
            if c in (4,5,7,8,9,11,12,16): cell.number_format = '#,##0'
            if c in (10,13,17): cell.number_format = '0.0%'
            if c in (3,14,15): cell.number_format = '0.00'
            if c == 18: cell.alignment = Alignment(wrap_text=True, vertical='top')
        if mer:
            w.cell(rr, 14).fill = GREEN if mer >= tg else (RED if mer < br else YEL)
        if memo: w.cell(rr, 18).fill = YEL
        if x['date'] in HOLIDAYS:
            for c in range(1, 4): w.cell(rr, c).fill = GRAY
        rr += 1
    for col, wid in zip('ABCDEFGHIJKLMNOPQR', [12,6,9,16,10,8,11,10,11,9,11,11,9,8,11,10,9,40]):
        w.column_dimensions[col].width = wid
    w.freeze_panes = f'A{top}'
    w.auto_filter.ref = f'A{top-1}:R{rr-1}'

# ---- カタログ全部（テスト） ----
w = wb.create_sheet('カタログ全部')
w['A1'] = 'カタログ全部（テスト）※全商品横断のカタログ広告'
w['A1'].font = Font(name='Arial', bold=True, size=13)
w['A2'] = 'Shopify側でどの商品にも紐づかないため売上・利益は分解できない。広告費のみを日次で管理する。'
w['A3'] = 'この行を含めると、商品タブの広告費の合計＝Metaアカウントの実消化額と一致する。'
rr = 5
for c, v in enumerate(['日付', '曜日', '広告費', '日予算', '消化率'], 1): w.cell(rr, c, v)
header(w, rr, 5); rr += 1
for d in DATES:
    a = A['カタログ全部（テスト）'].get(d, 0); b = B.get('カタログ全部（テスト）', {}).get(d)
    for c, v in enumerate([d, wd(d), round(a), b or '', round(a/b, 3) if b else ''], 1):
        x = w.cell(rr, c, v); x.border = thin; x.font = TD
        if c in (3, 4): x.number_format = '#,##0'
        if c == 5: x.number_format = '0.0%'
    rr += 1
for col, wid in zip('ABCDE', [12, 6, 12, 11, 9]): w.column_dimensions[col].width = wid

# ---- 非広告商品 ----
w = wb.create_sheet('非広告商品')
w['A1'] = '広告を出していない商品（広告費0円。利益＝売上−原価）'
w['A1'].font = Font(name='Arial', bold=True, size=13)
rr = 3
noad = [n for n in S if n not in ADV and n != '']
for c, v in enumerate(['商品', '売価', '単価原価', '30日売上', '30日販売数', '30日原価', '30日利益', '30日利益率'], 1):
    w.cell(rr, c, v)
header(w, rr, 8); rr += 1
for n in sorted(noad, key=lambda k: -sum(v[0]-v[1] for v in S[k].values())):
    s = sum(v[0]-v[1] for v in S[n].values()); g = sum(v[0] for v in S[n].values())
    p = PRICE.get(n); q = round(g/p) if p else None
    c_ = q*COST.get(n, 0) if q is not None else 0
    for c, v in enumerate([n, p or '変動', COST.get(n, 0), s, q, c_, s-c_, round((s-c_)/s, 4) if s else ''], 1):
        x = w.cell(rr, c, v); x.border = thin; x.font = TD
        if c in (2, 3, 4, 6, 7): x.number_format = '#,##0'
        if c == 8: x.number_format = '0.0%'
    rr += 1
for col, wid in zip('ABCDEFGH', [26, 9, 10, 12, 11, 11, 12, 11]): w.column_dimensions[col].width = wid

wb.save(OUT)
print('saved', OUT, '/ タブ数', len(wb.sheetnames))
