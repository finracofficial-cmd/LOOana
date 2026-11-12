# -*- coding: utf-8 -*-
"""mk1112full.py から mk1113full.py を生成（昨日=11/12 木。11/11広告費確定）。
注文数（7日・30日）と30日Metaファネルは、取得結果を保存した scripts/daily/o1111/*.json|txt から生成する（ord7/ord30は商品名を短縮名で保存・合計と行数をassert）。"""
import json, re
exec(open('scripts/daily/txt1112.py').read()); T0 = T
exec(open('scripts/daily/txt1113.py').read())
src = open('scripts/daily/mk1112full.py').read()

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
O7, s7 = ordd('scripts/daily/o1112/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-11-06 UNTIL 2026-11-12 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1112/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-14 UNTIL 2026-11-12 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1112/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-11-06 UNTIL 2026-11-12'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (728, 3306, 600), (s7, s30, ORD7_STORE)
_known = set(eval(re.search(r"ORD30 = (\{.*?\})\n", src, re.S).group(1))) | set(eval(re.search(r"ORD = (\{.*?\})\n", src, re.S).group(1))) | {'ワイド水切りワイパー', '4WAY 取り付けOK 小型瞬間冷却ハンディファン', 'クリアビューレインガードフィルム', 'コードレス毛玉クリーナー', 'シリコンホールド膝サポーター', '防風あったか裏起毛パンツ', 'すき間収納シートポケット', 'ファスナー修理キット', 'UV歯ブラシ除菌器', 'バランスケアスリッパ'}
assert set(O7) <= _known and set(O30) <= _known, (set(O7) - _known, set(O30) - _known)
MF = {}
for ln in open('scripts/daily/o1112/mf30_raw.txt').read().split('\n')[1:]:
    if not ln.strip(): continue
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), 0 if o == 'null' else int(o))
assert len(MF) == 32, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses['2026-11-12'] = 2434
D7W = ['2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09', '2026-11-10', '2026-11-11', '2026-11-12']
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
 ('"""2026-11-12 定例レポート本体', '"""2026-11-13 定例レポート本体（昨日=11/12 木。11/11の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1111w.pkl'", "R = pickle.load(open('/tmp/rep1112w.pkl', 'rb'))"),
 ("SNAP = '2026-11-12'", "SNAP = '2026-11-13'   # 11/13 01時台 Meta直読（10キャンペーン・12セット）の日予算が 2026-11-12m と一致（145,000）"),
 ("assert sum(BUD.values()) == 176000", "assert sum(BUD.values()) == 145000, sum(BUD.values())"),
 ("# --- 7日(11/05-11/11) Shopify注文数", "# --- 7日(11/06-11/12) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1112/ord7_raw.json から生成）---"),
 ("# --- 30日(10/13-11/11) Shopify注文数", "# --- 30日(10/14-11/12) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1112/ord30_raw.json から生成）---"),
 ("# --- 30日(10/13-11/11) Metaファネル", "# --- 30日(10/14-11/12) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1112/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-12", "sh('収益', [f'LOOTY 収益レポート 2026-11-13（昨日 = 11/12 木）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/11(水)'", "for lbl, N, K, ACC in [('前日 11/12(木)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/10-11/12', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 11/05-11/11'", "('7日 11/06-11/12', R['N7'], R['K7'], R['ACCT7']), ('30日 10/14-11/12', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/11）", "'縦照合3本すべて通過（11/12）: Σ商品gross=全店336,940 ／ Σ値引=10,746 ／ Σ広告費=キャンペーン合算183,140円＝Meta時間別合計（11/11も gross 346,920・値引8,756 で一致・広告費は確定190,465円）',"),
 ("'✅ 11/10の広告費は再取得で確定済み", "'✅ 11/11の広告費は再取得で確定済み（189,643→**190,465円**。11/13に上書き）',"),
 ("'⚠️ 11/11の広告費は 11/12 00時台の取得【暫定】", "'⚠️ 11/12の広告費は 11/13 01時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/11 水)", "ws.cell(r, 1, '■ 昨日(11/12 木) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/11(水)'", "for c, v in enumerate(['指標','11/12(木)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 11/05-11/11", "sh('商品別', ['商品別（7日 11/06-11/12 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,387,595円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,367,680円（11/12分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・11日目）',", "'当月累積利益は11月分（11/01〜・12日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/13-11/11)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/14-11/12)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/13-11/11)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/14-11/12) が許容差以内で一致（コード内assert）',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/13(金)", "'★次: 11/14(土) クリーナー・ワイパー・ナノ・ドアの上げ（7日1.5以上・消化95%以上）／ブラシ・4-in-1の下げ（11/12-13が続けて1.25未満）→ 11/15(日) ワイパー・ブラシ・4-in-1・ドアの3日（11/12-14）→ 11/16(月) 週次（インソール・カタログ）・車載の次の判定 → 11/19(木) 裏起毛パンツの7日 → 11/26(木) 新しい運用の答え合わせ',"),
 ("if r[0] == '2026-11-11': PREVB[r[1]]", "if r[0] == '2026-11-12': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/11 00時台", "sh('予算見直しチェック', ['前日(11/12 00時台・2026-11-12)スナップショット → 本日(11/13 01時台・Meta直読)。11/12の変更は11回（12d〜12m）: レインガード12,000→10,000→コピー5,000→停止／UV歯ブラシ再開10,000→停止／すき間ポケット停止／スリッパ再開8,000→停止／フック再開8,000→停止',"),
 ("'合計 182,000 → **176,000円/日**", "'合計 176,000 → **145,000円/日**（−31,000＝レインガード−12,000・すき間ポケット−8,000・加湿器−8,000・ドア−3,000〔11/12 00時台〕。UV歯ブラシ・スリッパ・フックは再開して同じ日に停止＝±0）',"),
 ("'★体制: 15セット・176,000円/日", "'★体制: 12セット・145,000円/日（本日 -sab +2,600 で 147,600）。合計19万円のブレーキは廃止',"),
 ("'★11/11の消化は 189,643円", "'★11/12の消化は 183,140円（暫定。日中に予算が11回動いたため、終日予算に対する消化率は出さない）。11/11は確定190,465円、11/10は確定165,869円',"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/13-11/11)", "sh('曜日指数', ['直近30日(10/14-11/12)・祝日除外（11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/11 vs", "# ---------- 時間別（11/12 vs 前週木11/05 vs 11/06-11/11平均。Meta時間別 data_query / Shopify GROUP BY hour_of_day 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1111.json'))", "_H = _json.load(open('scripts/daily/hourly1112.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/11(水)", "sh('時間別', ['時間帯別の比較: 11/12(木) vs 前週木(11/5) vs 直近6日(11/6-11/11)平均。広告=Meta時間別（11/12は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/12は広告費が 0〜5時台+7%・6〜9時台−9%・10〜13時台−7%・14〜17時台−10%・18〜23時台−10%（6日平均比）、注文は 13・14・12・8・21件（6日平均 10.3・19.0・20.2・14.0・25.2）',"),
 ("['時間帯','広告 11/11','広告 11/04'", "['時間帯','広告 11/12','広告 11/05','広告 6日平均','表示 11/12','表示 11/05','表示 6日平均','LPV 11/12','LPV 11/05','LPV 6日平均','Meta購入 11/12','Meta購入 11/05','Meta購入 6日平均',"),
 ("'gross 11/11','gross 11/04'", "'gross 11/12','gross 11/05','gross 6日平均','注文 11/12','注文 11/05','注文 6日平均','gross÷広告 11/12','gross÷広告 11/05','gross÷広告 6日平均','セッション 11/12','カート 11/12'],"),
 ("wb.save('data/reports/report-2026-11-12.xlsx')", "wb.save('data/reports/report-2026-11-13.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は11日で+1,389,783円（126,344円/日）'],", "11月は12日で+1,450,433円（120,869円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（水曜・CVR 3.12%・注文72件・客単価4,697円は16日で最低・18〜23時台が弱い）' if d == '2026-11-11' else '（火曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（木曜・CVR 2.79%・注文68件・6〜17時台が弱く18〜23時台は−14%）' if d == '2026-11-12' else '（水曜・CVR 3.12%・注文72件・客単価4,697円は16日で最低・18〜23時台が弱い）' if d == '2026-11-11' else '（火曜")
for a, b in [("'2026-11-10':2260,'2026-11-11':2307}", "'2026-11-10':2260,'2026-11-11':2307,'2026-11-12':2434}"),
             ("'2026-11-10':75,'2026-11-11':72}", "'2026-11-10':75,'2026-11-11':72,'2026-11-12':68}")]:
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
REP.append((block(src, "ORD = {'", "（VIP特典は商品名2種を合算）"), ORD_NEW))
REP.append((block(src, "ORD30 = {'", "assert sum(ORD30.values()) == 3340, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'", ")}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/11(水)'", "\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/12(木)'", "\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ["'/tmp/rep1111w.pkl'", 'hourly1111.json', 'report-2026-11-12.xlsx', 'ブレーキ継続']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1113full.py', 'w').write(src)
print('mk1113full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
