# -*- coding: utf-8 -*-
"""mk1116full.py から mk1117full.py を生成（昨日=11/16 月。11/15広告費確定）。
注文数（7日・30日）と30日Metaファネルは scripts/daily/o1116/*.json|txt、時間別は hourly1116.json から生成する。
v2〜v4 キャンペーン: 予算の記録は元の商品名、広告費はフック（旧・v2・v3・v4）とインソール（旧・v2・v3）を足す（w1116.py の MULTI と同じ）。"""
import json, re
exec(open('scripts/daily/txt1116.py').read()); T0 = T
exec(open('scripts/daily/txt1117.py').read())
src = open('scripts/daily/mk1116full.py').read()
def nm(t):
    if t.startswith('VIP特典'): return '優先配送 (VIP特典)'
    s = re.sub(r'【[^】]*】', '', t).strip()
    s = re.sub(r'^(LOOTY|LOTTY)\s*', '', s).strip()
    return {'完全遮光・形状記憶・晴雨兼用・UV日傘': '完全遮光・形状記憶', '高吸水・速乾ヘアドライタオル': 'ヘアドライタオル', 'コードレスパワーミスト加湿器': 'コードレスダブルミスト加湿器'}.get(s, s)
def ordd(path, q):
    d = json.load(open(path)); assert d['query'] == q, d['query']
    out = {}
    for t, v in d['rows']:
        if not t: assert int(v) == 0; continue
        out[nm(t)] = out.get(nm(t), 0) + int(v)
    return out, sum(int(v) for _, v in d['rows'])
O7, s7 = ordd('scripts/daily/o1116/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-11-10 UNTIL 2026-11-16 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1116/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-18 UNTIL 2026-11-16 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1116/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-11-10 UNTIL 2026-11-16'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (588, 3173, 489), (s7, s30, ORD7_STORE)
MF = {}
for ln in open('scripts/daily/o1116/mf30_raw.txt').read().split('\n')[1:]:
    if not ln.strip(): continue
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), 0 if o == 'null' else int(o))
assert len(MF) == 36, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses.update({'2026-11-16': 2418})
D7W = ['2026-11-10', '2026-11-11', '2026-11-12', '2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16']
SESS7 = sum(_ses[d] for d in D7W)
def fmt(d, per=6):
    it = [f"'{k}':{v}" for k, v in d.items()]
    return ',\n'.join(','.join(it[i:i + per]) for i in range(0, len(it), per))
ORD_NEW = ("ORD = {" + fmt(O7) + "}\n"
           f"STORE_ORD7, STORE_SESS7 = {ORD7_STORE}, {SESS7}   # 注文=ShopifyQL 7日直接・セッション=日次の合計\n"
           f"assert sum(ORD.values()) == {s7}, sum(ORD.values())   # 全店{ORD7_STORE}より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）")
ORD30_NEW = "ORD30 = {" + fmt(O30) + "}\n" + f"assert sum(ORD30.values()) == {s30}, sum(ORD30.values())"
MF_NEW = "MF_RAW = {" + ',\n'.join(','.join(f"'{k}':{str(v).replace(' ', '')}" for k, v in list(MF.items())[i:i + 2]) for i in range(0, len(MF), 2)) + "}"   # キー（キャンペーン名）の空白は残す（'快適マジックインソール v3'）
lines = src.split('\n')
def rep_line(prefix, new):
    idx = [i for i, l in enumerate(lines) if l.lstrip().startswith(prefix)]
    assert len(idx) == 1, ('行が一意でない', prefix[:50], len(idx))
    i = idx[0]; ind = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = ind + new
q = lambda s: repr(s)
p0 = lambda k, n=40: repr(T0[k])[:n]
LR = [
 ('"""2026-11-16 定例レポート本体', '"""2026-11-17 定例レポート本体（昨日=11/16 月。11/15の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1115w.pkl'", "R = pickle.load(open('/tmp/rep1116w.pkl', 'rb'))"),
 ("SNAP = '2026-11-16c'", "SNAP = '2026-11-17'   # 11/17 00時台の全セット（ノーズ12,000・シェーバー11,000はMeta直読で確認。data_query は8,000と遅れて出る）＝182,600"),
 ("# --- 7日(11/09-11/15) Shopify注文数", "# --- 7日(11/10-11/16) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1116/ord7_raw.json から生成）---"),
 ("# --- 30日(10/17-11/15) Shopify注文数", "# --- 30日(10/18-11/16) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1116/ord30_raw.json から生成）---"),
 ("# --- 30日(10/17-11/15) Metaファネル", "# --- 30日(10/18-11/16) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1116/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-16", "sh('収益', [f'LOOTY 収益レポート 2026-11-17（昨日 = 11/16 月）',"),
 (p0('head'), q(T['head']) + ','), (p0('ord'), q(T['ord']) + ','), (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','), (p0('judge'), q(T['judge']) + ','), (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/15(日)'", "for lbl, N, K, ACC in [('前日 11/16(月)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/14-11/16', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 11/09-11/15'", "('7日 11/10-11/16', R['N7'], R['K7'], R['ACCT7']), ('30日 10/18-11/16', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/15）", "'縦照合3本すべて通過（11/16）: Σ商品gross=全店446,830 ／ Σ値引=15,724 ／ Σ広告費=キャンペーン合算184,018円（00時台の暫定・時間別 fresh は184,428円）。11/15も gross 442,620・値引20,010 で一致・広告費は確定181,491円',"),
 ("'✅ 11/14の広告費は再取得で確定済み", "'✅ 11/15の広告費は再取得で確定済み（180,535→**181,491円**。11/17に上書き）',"),
 ("'⚠️ 11/15の広告費は 11/16 00時台の取得【暫定】", "'⚠️ 11/16の広告費は 11/17 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/15 日)", "ws.cell(r, 1, '■ 昨日(11/16 月) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/15(日)'", "for c, v in enumerate(['指標','11/16(月)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 11/09-11/15", "sh('商品別', ['商品別（7日 11/10-11/16 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,230,140円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,215,031円（11/16分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・15日目）',", "'当月累積利益は11月分（11/01〜・16日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/17-11/15)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/18-11/16)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/17-11/15)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/18-11/16) が許容差以内で一致（コード内assert。11/16はCSVが00時台の暫定）。フックは旧・v2・v3・v4、インソールは旧・v2・v3 を足して1行',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/17(火)", "'★次: 11/18(水) マルチクリップ・インソール v3 の2日目／ノーズ・インソール・ガラス sabu の4-2／ワイパー・W固定・ナノ・ドア・4-in-1 → 11/21(土) ノーズ・シェーバー7日 → 11/23(月) インソール v3・マルチクリップ7日 → 11/26(木) 答え合わせ',"),
 ("if r[0] == '2026-11-15': PREVB[r[1]]", "if r[0] == '2026-11-16': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/15 00時台", "sh('予算見直しチェック', ['前日(11/16 00時台・2026-11-16)スナップショット → 本日(11/17 00時台・Meta直読 2026-11-17)。変更（11/16・ユーザー）: ノーズ 8,000→12,000・シェーバー 8,000→11,000・インソール旧 11,000→停止→v3 8,000・フック v2 8,000→v3→v4→停止・マルチクリップ 8,000（新商品）',"),
 ("'合計 182,600 → **182,600円/日**", "'合計 178,600 → **182,600円/日**（+4,000。増: ノーズ+4,000・シェーバー+3,000・マルチクリップ+8,000／減: インソール−3,000・フック−8,000）。今日動かすものを実施すると 189,000円',"),
 ("'★体制: 15セット・182,600円/日", "'★体制: 15セット・182,600円/日（→ 今日の5件で189,000円）。合計19万円のブレーキは廃止',"),
 ("'★11/15の消化は 180,535円", "'★11/16の消化は 184,018円（暫定）。11/15は確定181,491円、11/14は確定163,714円。W固定 -sab は11/16 に配信が戻った（17,726円・予算13,000の136%）',"),
 ("'★インソールは旧キャンペーン停止", "'★インソールは旧・v2 を止めて v3（新規キャンペーン）で8,000。フックは v2→v3（配信0）→v4→22時台に停止。予算の記録は元の商品名で持つ'],"),
 (p0('cvr1'), q(T['cvr1']) + ','), (p0('cvr2'), q(T['cvr2']) + ','), (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/17-11/15)", "sh('曜日指数', ['直近30日(10/18-11/16)・祝日除外（11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/15 vs", "# ---------- 時間別（11/16 vs 前週月11/09 vs 11/10-11/15平均。Meta時間別 data_query / Shopify GROUP BY hour_of_day 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1115.json'))", "_H = _json.load(open('scripts/daily/hourly1116.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/15(日)", "sh('時間別', ['時間帯別の比較: 11/16(月) vs 前週月(11/9) vs 直近6日(11/10-11/15)平均。広告=Meta時間別（11/16は00時台 fresh・CSVの暫定より+410円）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上。注文の時間別合計は77（日別76・1件が2つの時間帯に数えられている・理由は未確認）',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/16は広告費が 0〜5時台−10%・6〜9時台−21%・10〜13時台+8%・14〜17時台+22%・18〜23時台+27%（6日平均比）、注文は 6・12・11・19・29（6日平均 8.7・14.5・15.2・10.7・19.8）。夕方から夜に強かった日',"),
 ("['時間帯','広告 11/15','広告 11/08'", "['時間帯','広告 11/16','広告 11/09','広告 6日平均','表示 11/16','表示 11/09','表示 6日平均','LPV 11/16','LPV 11/09','LPV 6日平均','Meta購入 11/16','Meta購入 11/09','Meta購入 6日平均',"),
 ("'gross 11/15','gross 11/08'", "'gross 11/16','gross 11/09','gross 6日平均','注文 11/16','注文 11/09','注文 6日平均','gross÷広告 11/16','gross÷広告 11/09','gross÷広告 6日平均','セッション 11/16','カート 11/16'],"),
 ("wb.save('data/reports/report-2026-11-16.xlsx')", "wb.save('data/reports/report-2026-11-17.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は15日で+1,702,564円（113,504円/日）'],", "11月は16日で+1,828,226円（114,264円/日）'],"),
             ("('★昨日（日曜・CVR 2.92%・注文76件・客単価5,561円・7,000円以上26%）' if d == '2026-11-15' else '（土曜",
              "('★昨日（月曜・CVR 3.14%・注文76件・客単価5,672円・7,000円以上25%）' if d == '2026-11-16' else '（日曜・CVR 2.92%・注文76件・客単価5,561円・7,000円以上26%）' if d == '2026-11-15' else '（土曜"),
             ("'2026-11-13':2323,'2026-11-14':2570,'2026-11-15':2607}", "'2026-11-13':2323,'2026-11-14':2570,'2026-11-15':2607,'2026-11-16':2418}"),
             ("'2026-11-13':58,'2026-11-14':64,'2026-11-15':76}", "'2026-11-13':58,'2026-11-14':64,'2026-11-15':76,'2026-11-16':76}"),
             ("   # 11/15 は CSV が 00時台の暫定・ファネルは01時台の取得", "   # 11/16 は CSV・ファネルとも 00時台の取得")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
# ---- v2〜v4 キャンペーン ----
_m = [l for l in src.split('\n') if l.startswith('MULTI = {')]; assert len(_m) == 1
src = src.replace(_m[0], "MULTI = {'高見えレザーヘッドレストフック': ('高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv2', '高見えレザーヘッドレストフックv3', '高見えレザーヘッドレストフックv4'), '快適マジックインソール': ('快適マジックインソール', '快適マジックインソールv2', '快適マジックインソール v3')}   # w1116.py と同じ")
_u = "INV.update({'高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '快適マジックインソールv2': '快適マジックインソール'})"
assert src.count(_u) == 1
src = src.replace(_u, "INV.update({'高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv3': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック', '快適マジックインソールv2': '快適マジックインソール', '快適マジックインソール v3': '快適マジックインソール'})")
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
REP = [(block(src, "ORD = {'", "（VIP特典は商品名2種を合算）"), ORD_NEW),
       (block(src, "ORD30 = {'", "assert sum(ORD30.values()) == 3211, sum(ORD30.values())"), ORD30_NEW),
       (block(src, "MF_RAW = {'", ")}"), MF_NEW),
       (block(src, "NA = [\n ['📊 11/15(日)'", "\n]"), T['NA']),
       (block(src, "JUDGE = [\n ['11/16(月)'", "\n]"), T['JUDGE'])]
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ["'/tmp/rep1115w.pkl'", 'hourly1115.json', 'report-2026-11-16.xlsx', "SNAP = '2026-11-16c'"]:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1117full.py', 'w').write(src)
print('mk1117full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
