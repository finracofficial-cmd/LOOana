# -*- coding: utf-8 -*-
"""mk1110full.py から mk1111full.py を生成（昨日=11/10 火。11/09広告費確定）。
注文数（7日・30日）と30日Metaファネルは、取得結果を保存した scripts/daily/o1110/*.json|txt から生成する（ord7/ord30は商品名を短縮名で保存・合計と行数をassert）。"""
import json, re
exec(open('scripts/daily/txt1110.py').read()); T0 = T
exec(open('scripts/daily/txt1111.py').read())
src = open('scripts/daily/mk1110full.py').read()

# ---------- 実測ファイルから ORD / ORD30 / MF_RAW を作る ----------
def nm(t):
    if t.startswith('VIP特典'): return '優先配送 (VIP特典)'
    s = re.sub(r'【[^】]*】', '', t).strip()
    s = re.sub(r'^(LOOTY|LOTTY)\s*', '', s).strip()
    return {'完全遮光・形状記憶・晴雨兼用・UV日傘': '完全遮光・形状記憶', '高吸水・速乾ヘアドライタオル': 'ヘアドライタオル', 'コードレスパワーミスト加湿器': 'コードレスダブルミスト加湿器'}.get(s, s)   # 加湿器は11/6にShopify商品名が変わった（同じ商品ID）
def ordd(path, q):
    d = json.load(open(path)); assert d['query'] == q, d['query']
    out = {}
    for t, v in d['rows']:
        if not t: assert int(v) == 0; continue
        out[nm(t)] = out.get(nm(t), 0) + int(v)
    return out, sum(int(v) for _, v in d['rows'])
O7, s7 = ordd('scripts/daily/o1110/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-11-04 UNTIL 2026-11-10 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1110/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-12 UNTIL 2026-11-10 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1110/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-11-04 UNTIL 2026-11-10'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (752, 3402, 610), (s7, s30, ORD7_STORE)
_known = set(eval(re.search(r"ORD30 = (\{.*?\})\n", src, re.S).group(1))) | set(eval(re.search(r"ORD = (\{.*?\})\n", src, re.S).group(1))) | {'ワイド水切りワイパー', '4WAY 取り付けOK 小型瞬間冷却ハンディファン', 'クリアビューレインガードフィルム', 'コードレス毛玉クリーナー', 'シリコンホールド膝サポーター'}
assert set(O7) <= _known and set(O30) <= _known, (set(O7) - _known, set(O30) - _known)
MF = {}
for ln in open('scripts/daily/o1110/mf30_raw.txt').read().split('\n')[1:]:
    if not ln.strip(): continue
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), int(o))
assert len(MF) == 31, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses['2026-11-10'] = 2260
D7W = ['2026-11-04', '2026-11-05', '2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09', '2026-11-10']
SESS7 = sum(_ses[d] for d in D7W)
def fmt(d, per=6):
    it = [f"'{k}':{v}" for k, v in d.items()]
    return ',\n'.join(','.join(it[i:i + per]) for i in range(0, len(it), per))
ORD_NEW = ("ORD = {" + fmt(O7) + "}\n"
           f"STORE_ORD7, STORE_SESS7 = {ORD7_STORE}, {SESS7}   # 注文=ShopifyQL 7日直接・セッション=日次の合計\n"
           f"assert sum(ORD.values()) == {s7}, sum(ORD.values())   # 全店{ORD7_STORE}より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）")
ORD30_NEW = "ORD30 = {" + fmt(O30) + "}\n" + f"assert sum(ORD30.values()) == {s30}, sum(ORD30.values())"
MF_NEW = "MF_RAW = {" + ',\n'.join(','.join(f"'{k}':{v}".replace(' ', '') for k, v in list(MF.items())[i:i + 2]) for i in range(0, len(MF), 2)) + "}"

lines = src.split('\n')
def rep_line(prefix, new):
    idx = [i for i, l in enumerate(lines) if l.lstrip().startswith(prefix)]
    assert len(idx) == 1, ('行が一意でない', prefix[:50], len(idx))
    i = idx[0]; ind = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = ind + new
q = lambda s: repr(s)
p0 = lambda k, n=40: repr(T0[k])[:n]
LR = [
 ('"""2026-11-10 定例レポート本体', '"""2026-11-11 定例レポート本体（昨日=11/10 火。11/09の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1109w.pkl'", "R = pickle.load(open('/tmp/rep1110w.pkl', 'rb'))"),
 ("SNAP = '2026-11-10'", "SNAP = '2026-11-11'   # 11/11 00時台 Meta直読（12キャンペーン）の日予算が 2026-11-10c と一致（14セット・182,000）"),
 ("assert sum(BUD.values()) == 198000", "assert sum(BUD.values()) == 182000, sum(BUD.values())"),
 ("# --- 7日(11/03-11/09) Shopify注文数", "# --- 7日(11/04-11/10) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1110/ord7_raw.json から生成）---"),
 ("# --- 30日(10/11-11/09) Shopify注文数", "# --- 30日(10/12-11/10) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1110/ord30_raw.json から生成）---"),
 ("# --- 30日(10/11-11/09) Metaファネル", "# --- 30日(10/12-11/10) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1110/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-10", "sh('収益', [f'LOOTY 収益レポート 2026-11-11（昨日 = 11/10 火）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/09(月)'", "for lbl, N, K, ACC in [('前日 11/10(火)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/08-11/10', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 11/03-11/09'", "('7日 11/04-11/10', R['N7'], R['K7'], R['ACCT7']), ('30日 10/12-11/10', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/09）", "'縦照合3本すべて通過（11/10）: Σ商品gross=全店375,780 ／ Σ値引=10,547 ／ Σ広告費=キャンペーン合算165,063円＝Meta時間別合計（11/09も gross 405,870・値引11,743 で一致）',"),
 ("'✅ 11/08の広告費は再取得で確定済み", "'✅ 11/09の広告費は再取得で確定済み（198,846→**200,083円**。11/11に上書き）',"),
 ("'⚠️ 11/09の広告費は 11/10 00時台の取得【暫定】", "'⚠️ 11/10の広告費は 11/11 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/09 月)", "ws.cell(r, 1, '■ 昨日(11/10 火) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/09(月)'", "for c, v in enumerate(['指標','11/10(火)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 11/03-11/09", "sh('商品別', ['商品別（7日 11/04-11/10 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,430,812円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,384,377円（11/10分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・9日目）',", "'当月累積利益は11月分（11/01〜・10日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/11-11/09)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/12-11/10)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/11-11/09)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/12-11/10) が許容差以内で一致（コード内assert）',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/11(水)", "'★次: 11/12(木) レインガード7日（11/5-11）・アーチフィット2日目・4-in-1（3日続けて1.25未満なら8,800）→ 11/13(金) 11/10の変更の答え合わせ（11/10-12）→ 11/16(月) 週次',"),
 ("if r[0] == '2026-11-09': PREVB[r[1]]", "if r[0] == '2026-11-10': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/09 03時台", "sh('予算見直しチェック', ['前日(11/10 00時台・2026-11-10)スナップショット → 本日(11/11 00時台・Meta直読)。11/10の変更: 00:29確認 ワイパー増・クリーナー/ナノ/車載/4-in-1減・シーラー停止（10b）／15:20確認 アーチフィット新規8,000（10c）',"),
 ("'合計 212,000 → **198,000円/日**", "'合計 198,000 → **182,000円/日**（−16,000＝クリーナー主力−3,000/sabu−5,000・ナノ−5,000・車載−2,000/−2,000・4-in-1 −2,000・シーラー停止−8,000・ワイパー+3,000・アーチフィット新規+8,000）',"),
 ("'★体制: 14セット・198,000円/日", "'★体制: 14セット・182,000円/日（3日移動平均128,270円＝合計を190,000円より増やさない）',"),
 ("'★11/09の消化は 198,846円", "'★11/10の消化は 165,063円（暫定・終日の最終予算182,000の91%）。11/09は確定200,083円、11/08は確定241,135円',"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/11-11/09)", "sh('曜日指数', ['直近30日(10/12-11/10)・祝日除外（10/12スポーツの日・11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/09 vs", "# ---------- 時間別（11/10 vs 前週火11/03(祝) vs 11/04-11/09平均。Meta時間別 data_query / Shopify TIMESERIES hour 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1109.json'))", "_H = _json.load(open('scripts/daily/hourly1110.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/9(月)", "sh('時間別', ['時間帯別の比較: 11/10(火) vs 前週火(11/3・祝日) vs 直近6日(11/4-11/9)平均。広告=Meta時間別（11/10は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/10は広告費が 6〜17時台で6日平均の−22〜−31%（合計予算は−12%）、0〜5時台−6%・18〜23時台−7%。注文は 0〜5時台 8（6日平均9.8）・6〜9時台 14（18.3）・10〜13時台 16（20.5）・14〜17時台 8（15.8・gross−60%）・18〜23時台 29（24.7・gross−2%）。22〜23時台のLPVは着地途中',"),
 ("['時間帯','広告 11/09','広告 11/02'", "['時間帯','広告 11/10','広告 11/03','広告 6日平均','表示 11/10','表示 11/03','表示 6日平均','LPV 11/10','LPV 11/03','LPV 6日平均','Meta購入 11/10','Meta購入 11/03','Meta購入 6日平均',"),
 ("'gross 11/09','gross 11/02'", "'gross 11/10','gross 11/03','gross 6日平均','注文 11/10','注文 11/03','注文 6日平均','gross÷広告 11/10','gross÷広告 11/03','gross÷広告 6日平均','セッション 11/10','カート 11/10'],"),
 ("wb.save('data/reports/report-2026-11-10.xlsx')", "wb.save('data/reports/report-2026-11-11.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は9日で+1,220,392円（135,599円/日）'],", "11月は10日で+1,328,167円（132,817円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（月曜・CVR 2.69%・注文79件・14〜17時台が弱く18〜23時台は平常）' if d == '2026-11-09' else '（日曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（火曜・CVR 3.32%・注文75件・来訪は16日で最少・18〜23時台は平常）' if d == '2026-11-10' else '（月曜・CVR 2.69%・注文79件・14〜17時台が弱く18〜23時台は平常）' if d == '2026-11-09' else '（日曜")
for a, b in [("'2026-11-08':3741,'2026-11-09':2936}", "'2026-11-08':3741,'2026-11-09':2936,'2026-11-10':2260}"),
             ("'2026-11-08':114,'2026-11-09':79}", "'2026-11-08':114,'2026-11-09':79,'2026-11-10':75}")]:
    assert src.count(a) == 1, a; src = src.replace(a, b)
def cal_set(name, body):
    global src
    h = [l for l in src.split('\n') if l.lstrip().startswith(f"'{name}': ('2026-") or l.startswith(f"CAL = {{'{name}'")]
    if not h:
        _k = "       'むくみ取りかっさ': ('2026-"; assert src.count(_k) == 1
        src = src.replace(_k, f"       '{name}': {body},\n" + _k); return
    assert len(h) == 1, (name, len(h)); old = h[0]; new = f"       '{name}': {body},"
    if old.startswith('CAL = {'): new = 'CAL = {' + new.strip()
    if old.rstrip().endswith('),}'): new = new.rstrip().rstrip(',') + ',}'
    src = src.replace(old, new)
for _n, _b in T['CAL'].items(): cal_set(_n, _b)
def block(src, start, endtok):
    i = src.index(start); j = src.index(endtok, i) + len(endtok)
    return src[i:j]
REP = []
REP.append((block(src, "ORD = {'伸縮ガラスクリーナー':123,", "（VIP特典は商品名2種を合算）"), ORD_NEW))
REP.append((block(src, "ORD30 = {'ナノガラス脱毛パッド':787,", "assert sum(ORD30.values()) == 3446, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'ナノガラス脱毛パッド':(1774445,1500565,21732),", "'ロングニトリル家事手袋':(4366,824,19)}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/9(月)'", "\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/10(火)'", "\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ['11/09(月)', "'/tmp/rep1109w.pkl'", 'hourly1109.json', 'report-2026-11-10.xlsx']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1111full.py', 'w').write(src)
print('mk1111full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
