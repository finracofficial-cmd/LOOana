# -*- coding: utf-8 -*-
"""mk1117full.py から mk1118full.py を生成（昨日=11/17 火。11/16広告費確定）。
注文数（7日・30日）と30日Metaファネルは scripts/daily/o1117/*.json|txt、時間別は hourly1117.json から生成する。
v2〜v4 キャンペーン: 予算の記録は元の商品名、広告費はフック（旧・v2・v3・v4）とインソール（旧・v2・v3）を足す（w1117.py の MULTI と同じ）。"""
import json, re
exec(open('scripts/daily/txt1117.py').read()); T0 = T
exec(open('scripts/daily/txt1118.py').read())
src = open('scripts/daily/mk1117full.py').read()
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
O7, s7 = ordd('scripts/daily/o1117/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-11-11 UNTIL 2026-11-17 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1117/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-19 UNTIL 2026-11-17 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1117/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-11-11 UNTIL 2026-11-17'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (572, 3120, 474), (s7, s30, ORD7_STORE)
MF = {}
for ln in open('scripts/daily/o1117/mf30_raw.txt').read().split('\n')[1:]:
    if not ln.strip(): continue
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), 0 if o == 'null' else int(o))
assert len(MF) == 37, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses.update({'2026-11-17': 2534})
D7W = ['2026-11-11', '2026-11-12', '2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16', '2026-11-17']
SESS7 = sum(_ses[d] for d in D7W)
def fmt(d, per=6):
    it = [f"'{k}':{v}" for k, v in d.items()]
    return ',\n'.join(','.join(it[i:i + per]) for i in range(0, len(it), per))
ORD_NEW = ("ORD = {" + fmt(O7) + "}\n"
           f"STORE_ORD7, STORE_SESS7 = {ORD7_STORE}, {SESS7}   # 注文=ShopifyQL 7日直接・セッション=日次の合計\n"
           f"assert sum(ORD.values()) == {s7}, sum(ORD.values())   # 全店{ORD7_STORE}より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）")
ORD30_NEW = "ORD30 = {" + fmt(O30) + "}\n" + f"assert sum(ORD30.values()) == {s30}, sum(ORD30.values())"
MF_NEW = "MF_RAW = {" + ',\n'.join(','.join(f"'{k}':{str(v).replace(' ', '')}" for k, v in list(MF.items())[i:i + 2]) for i in range(0, len(MF), 2)) + "}"
lines = src.split('\n')
def rep_line(prefix, new):
    idx = [i for i, l in enumerate(lines) if l.lstrip().startswith(prefix)]
    assert len(idx) == 1, ('行が一意でない', prefix[:50], len(idx))
    i = idx[0]; ind = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = ind + new
q = lambda s: repr(s)
p0 = lambda k, n=40: repr(T0[k])[:n]
LR = [
 ('"""2026-11-17 定例レポート本体', '"""2026-11-18 定例レポート本体（昨日=11/17 火。11/16の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1116w.pkl'", "R = pickle.load(open('/tmp/rep1117w.pkl', 'rb'))"),
 ("SNAP = '2026-11-17'", "SNAP = '2026-11-18'   # 11/18 00時台の全セット（data_query。マルチクリップ 10,000 は Meta 直読でも確認）＝197,600"),
 ("# --- 7日(11/10-11/16) Shopify注文数", "# --- 7日(11/11-11/17) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1117/ord7_raw.json から生成）---"),
 ("# --- 30日(10/18-11/16) Shopify注文数", "# --- 30日(10/19-11/17) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1117/ord30_raw.json から生成）---"),
 ("# --- 30日(10/18-11/16) Metaファネル", "# --- 30日(10/19-11/17) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1117/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-17", "sh('収益', [f'LOOTY 収益レポート 2026-11-18（昨日 = 11/17 火）',"),
 (p0('head'), q(T['head']) + ','), (p0('ord'), q(T['ord']) + ','), (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','), (p0('judge'), q(T['judge']) + ','), (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/16(月)'", "for lbl, N, K, ACC in [('前日 11/17(火)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/15-11/17', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 11/10-11/16'", "('7日 11/11-11/17', R['N7'], R['K7'], R['ACCT7']), ('30日 10/19-11/17', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/16）", "'縦照合3本すべて通過（11/17）: Σ商品gross=全店323,120 ／ Σ値引=8,756 ／ Σ広告費=キャンペーン合算195,748円（00時台の暫定・時間別では195,902円）。11/16も gross 446,830・値引15,724 で一致・広告費は確定185,255円',"),
 ("'✅ 11/15の広告費は再取得で確定済み", "'✅ 11/16の広告費は再取得で確定済み（184,018→**185,255円**。11/18に上書き）',"),
 ("'⚠️ 11/16の広告費は 11/17 00時台の取得【暫定】", "'⚠️ 11/17の広告費は 11/18 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/16 月)", "ws.cell(r, 1, '■ 昨日(11/17 火) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/16(月)'", "for c, v in enumerate(['指標','11/17(火)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 11/10-11/16", "sh('商品別', ['商品別（7日 11/11-11/17 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,215,031円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,246,147円（11/17分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・16日目）',", "'当月累積利益は11月分（11/01〜・17日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/18-11/16)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/19-11/17)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/18-11/16)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/19-11/17) が許容差以内で一致（コード内assert。11/17はCSVが00時台の暫定）。フックは旧・v2・v3・v4、インソールは旧・v2・v3 を足して1行',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/18(水)", "'★次: 11/19(木) グローブ2日目／マルチクリップ・ナノ・ドア・4-in-1 の4-2 → 11/20(金) ブランケット7日・ショップ オフ判定／ブラシ・シェーバー・W固定・ガラス → 11/21(土) ノーズ・シェーバー7日 → 11/23(月) インソール v3・マルチクリップ7日 → 11/26(木) 答え合わせ',"),
 ("if r[0] == '2026-11-16': PREVB[r[1]]", "if r[0] == '2026-11-17': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/16 00時台", "sh('予算見直しチェック', ['前日(11/17 00時台・2026-11-17)スナップショット → 本日(11/18 00時台・2026-11-18)。変更（11/17・ユーザー）: ノーズ 12,000→16,000・インソール v3 8,000→12,000・シェーバー 11,000→8,000・ブラシ 12,000→9,000・ガラス sabu 19,000→22,000・マルチクリップ 8,000→10,000・グローブ 8,000（新商品）',"),
 ("'合計 178,600 → **182,600円/日**", "'合計 182,600 → **197,600円/日**（+15,000。増: ノーズ+4,000・インソール+4,000・ガラス sabu+3,000・マルチクリップ+2,000・グローブ+8,000／減: シェーバー−3,000・ブラシ−3,000）。今日動かすものを実施すると 199,120円',"),
 ("'★体制: 15セット・182,600円/日", "'★体制: 16セット・197,600円/日（→ 今日の8件で199,120円）。合計19万円のブレーキは廃止',"),
 ("'★11/16の消化は 184,018円", "'★11/17の消化は 195,748円（暫定）。11/16は確定185,255円、11/15は確定181,491円。グローブは夜からの配信で2,682円（予算8,000の34%）',"),
 ("'★インソールは旧・v2 を止めて v3", "'★インソールは v3（新規キャンペーン）で12,000。フックは11/16に停止。ノーズ・シェーバーは v2。予算の記録は元の商品名で持つ'],"),
 (p0('cvr1'), q(T['cvr1']) + ','), (p0('cvr2'), q(T['cvr2']) + ','), (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/18-11/16)", "sh('曜日指数', ['直近30日(10/19-11/17)・祝日除外（11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/16 vs", "# ---------- 時間別（11/17 vs 前週火11/10 vs 11/11-11/16平均。Meta時間別 data_query / Shopify GROUP BY hour_of_day 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1116.json'))", "_H = _json.load(open('scripts/daily/hourly1117.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/16(月)", "sh('時間別', ['時間帯別の比較: 11/17(火) vs 前週火(11/10) vs 直近6日(11/11-11/16)平均。広告=Meta時間別（11/17は00時台 fresh・CSVの暫定より+154円）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上。注文の時間別合計は60（日別と一致）',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/17は広告費が 0〜5時台+21%・6〜9時台−11%・10〜13時台+13%・14〜17時台+16%・18〜23時台+22%（6日平均比）、注文は 9・10・14・12・15（6日平均 8.3・14.2・14.3・12.5・19.8）。夜に広告費を使ったが注文は少なかった日',"),
 ("['時間帯','広告 11/16','広告 11/09'", "['時間帯','広告 11/17','広告 11/10','広告 6日平均','表示 11/17','表示 11/10','表示 6日平均','LPV 11/17','LPV 11/10','LPV 6日平均','Meta購入 11/17','Meta購入 11/10','Meta購入 6日平均',"),
 ("'gross 11/16','gross 11/09'", "'gross 11/17','gross 11/10','gross 6日平均','注文 11/17','注文 11/10','注文 6日平均','gross÷広告 11/17','gross÷広告 11/10','gross÷広告 6日平均','セッション 11/17','カート 11/17'],"),
 ("wb.save('data/reports/report-2026-11-17.xlsx')", "wb.save('data/reports/report-2026-11-18.xlsx')"),
 ("assert sum(BUD.values()) == 182600", "assert sum(BUD.values()) == 197600, sum(BUD.values())"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は16日で+1,828,226円（114,264円/日）'],", "11月は17日で+1,862,360円（109,551円/日）'],"),
             ("('★昨日（月曜・CVR 3.14%・注文76件・客単価5,672円・7,000円以上25%）' if d == '2026-11-16' else '（日曜",
              "('★昨日（火曜・CVR 2.37%・注文60件・客単価5,239円・7,000円以上20%）' if d == '2026-11-17' else '（月曜・CVR 3.14%・注文76件・客単価5,672円・7,000円以上25%）' if d == '2026-11-16' else '（日曜"),
             ("'2026-11-16':2418}", "'2026-11-16':2418,'2026-11-17':2534}"),
             ("'2026-11-16':76}", "'2026-11-16':76,'2026-11-17':60}"),
             ("   # 11/16 は CSV・ファネルとも 00時台の取得", "   # 11/17 は CSV・ファネルとも 00時台の取得")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
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
       (block(src, "ORD30 = {'", "assert sum(ORD30.values()) == 3173, sum(ORD30.values())"), ORD30_NEW),
       (block(src, "MF_RAW = {'", ")}"), MF_NEW),
       (block(src, "NA = [\n ['📊 11/16(月)'", "\n]"), T['NA']),
       (block(src, "JUDGE = [\n ['11/17(火)'", "\n]"), T['JUDGE'])]
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ["'/tmp/rep1116w.pkl'", 'hourly1116.json', 'report-2026-11-17.xlsx', "SNAP = '2026-11-17'"]:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1118full.py', 'w').write(src)
print('mk1118full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
