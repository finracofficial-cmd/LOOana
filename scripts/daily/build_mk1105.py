# -*- coding: utf-8 -*-
"""mk1104full.py から mk1105full.py を生成（昨日=11/04 水。11/03広告費確定・ブレーキ再発動）。
注文数（7日・30日）と30日Metaファネルは、取得結果を保存した scripts/daily/o1104/*.json|txt から生成する（ord7/ord30は商品名を短縮名で保存・合計と行数をassert）。"""
import json, re
exec(open('scripts/daily/txt1104.py').read()); T0 = T
exec(open('scripts/daily/txt1105.py').read())
src = open('scripts/daily/mk1104full.py').read()

# ---------- 実測ファイルから ORD / ORD30 / MF_RAW を作る ----------
def nm(t):
    if t.startswith('VIP特典'): return '優先配送 (VIP特典)'
    s = re.sub(r'【[^】]*】', '', t).strip()
    s = re.sub(r'^(LOOTY|LOTTY)\s*', '', s).strip()
    return {'完全遮光・形状記憶・晴雨兼用・UV日傘': '完全遮光・形状記憶', '高吸水・速乾ヘアドライタオル': 'ヘアドライタオル'}.get(s, s)
def ordd(path, q):
    d = json.load(open(path)); assert d['query'] == q, d['query']
    out = {}
    for t, v in d['rows']:
        if not t: assert int(v) == 0; continue
        out[nm(t)] = out.get(nm(t), 0) + int(v)
    return out, sum(int(v) for _, v in d['rows'])
O7, s7 = ordd('scripts/daily/o1104/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-29 UNTIL 2026-11-04 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1104/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-06 UNTIL 2026-11-04 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1104/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-10-29 UNTIL 2026-11-04'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (702, 3442, 571), (s7, s30, ORD7_STORE)
_known = set(eval(re.search(r"ORD30 = (\{.*?\})\n", src, re.S).group(1))) | set(eval(re.search(r"ORD = (\{.*?\})\n", src, re.S).group(1))) | {'ワイド水切りワイパー'}
assert set(O7) <= _known and set(O30) <= _known, (set(O7) - _known, set(O30) - _known)
MF = {}
for ln in open('scripts/daily/o1104/mf30_raw.txt').read().split('\n')[1:]:
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), int(o))
assert len(MF) == 29, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses['2026-11-04'] = 2387
D7W = ['2026-10-%02d' % d for d in range(29, 32)] + ['2026-11-01', '2026-11-02', '2026-11-03', '2026-11-04']
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
 ('"""2026-11-04 定例レポート本体', '"""2026-11-05 定例レポート本体（昨日=11/04 水。11/03の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1103w.pkl'", "R = pickle.load(open('/tmp/rep1104w.pkl', 'rb'))"),
 ("SNAP = '2026-11-04'", "SNAP = '2026-11-05'   # 11/05 01時台 Meta読み（adsetdaily_budget）の日予算が 2026-11-04i と一致（15セット・190,000）"),
 ("assert sum(BUD.values()) == 189000", "assert sum(BUD.values()) == 190000, sum(BUD.values())"),
 ("# --- 7日(10/28-11/03) Shopify注文数", "# --- 7日(10/29-11/04) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1104/ord7_raw.json から生成）---"),
 ("# --- 30日(10/05-11/03) Shopify注文数", "# --- 30日(10/06-11/04) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1104/ord30_raw.json から生成）---"),
 ("# --- 30日(10/05-11/03) Metaファネル", "# --- 30日(10/06-11/04) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1104/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-04", "sh('収益', [f'LOOTY 収益レポート 2026-11-05（昨日 = 11/04 水）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/03(火・祝)'", "for lbl, N, K, ACC in [('前日 11/04(水)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/02-11/04', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 10/28-11/03'", "('7日 10/29-11/04', R['N7'], R['K7'], R['ACCT7']), ('30日 10/06-11/04', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/03）", "'縦照合3本すべて通過（11/04）: Σ商品gross=全店418,140 ／ Σ値引=20,162 ／ Σ広告費=キャンペーン合算186,751円（11/03も gross 450,670・値引13,140 で一致）',"),
 ("'✅ 11/02の広告費は再取得で確定済み", "'✅ 11/03の広告費は再取得で確定済み（212,514→**212,735円**。11/05に上書き）',"),
 ("'⚠️ 11/03の広告費は 11/04 朝の取得【暫定】", "'⚠️ 11/04の広告費は 11/05 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/03 火・祝)", "ws.cell(r, 1, '■ 昨日(11/04 水) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/03(火・祝)'", "for c, v in enumerate(['指標','11/04(水)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 10/28-11/03", "sh('商品別', ['商品別（7日 10/29-11/04 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,554,749円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,509,044円（11/04分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・3日目）',", "'当月累積利益は11月分（11/01〜・4日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/05-11/03)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/06-11/04)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/05-11/03)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/06-11/04) が許容差以内で一致（コード内assert）',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/6(金) 加湿器2日目", "'★次: 11/6(金) 加湿器・毛玉・ワイパー2日目（11/4-5）→ 11/7(土) ドアクッション7日（10/31-11/6）→ 11/8(日) 11/4の変更の答え合わせ（11/5-7）→ 11/9(月) 週次（11/2-8）→ 11/11(水) インソール新CR・加湿器・毛玉・ワイパー7日',"),
 ("if r[0] == '2026-11-03': PREVB[r[1]]", "if r[0] == '2026-11-04': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/03 00時", "sh('予算見直しチェック', ['前日(11/04 00時・2026-11-04)スナップショット → 本日(11/05 01時・Meta読み)。11/04の変更: 09:50 ドア／11:2x ブラシ・4-in-1・車載／13時台 毛玉再開・加湿器増額／14時台 ワイパー出稿／17:28 ナノA／19:48 クリーナー／20:29 ドア・シーラー',"),
 ("'合計 208,000 → **189,000円/日**", "'合計 189,000 → **190,000円/日**（+1,000＝毛玉+8,000・ワイパー+8,000・加湿器+5,000・ブラシ+3,000／ドア−8,000・ナノ−5,000・クリーナー−4,000・シーラー−3,000・4-in-1 −2,000・車載−1,000（A−4,000・B+3,000））',"),
 ("'★体制: 13セット・189,000円/日", "'★体制: 15セット・190,000円/日（⚠️ブレーキ再発動: 3日移動平均90,200円 <130,000 → 合計を増やさない）',"),
 ("'★11/03の消化は 212,514円", "'★11/04の消化は 186,751円（暫定）。11/03は確定212,735円、11/02は確定216,365円',"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/05-11/03)", "sh('曜日指数', ['直近30日(10/06-11/04)・祝日除外（10/12スポーツの日・11/3文化の日を除外）。売上=gross−値引。次回定期更新11/9(月)',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/03 vs", "# ---------- 時間別（11/04 vs 前週水10/28 vs 10/29-11/03平均。Meta時間別 data_query / Shopify TIMESERIES hour 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1103.json'))", "_H = _json.load(open('scripts/daily/hourly1104.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/3(火・祝)", "sh('時間別', ['時間帯別の比較: 11/4(水) vs 前週水(10/28) vs 直近6日(10/29-11/3)平均。広告=Meta時間別（11/4は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/4は朝〜夕方の広告費が6日平均より少なく（6〜9時台−38%・10〜13時台−21%）、LPVも少ない（−47%・−27%）。注文は 0〜5時台 11（6日平均8.3）・6〜9時台 11（20.8）・10〜13時台 12（15.7）・14〜17時台 12（16.3）・18〜23時台 24（22.3・gross+31%）＝弱かったのは朝〜夕方、夜は平常以上',"),
 ("['時間帯','広告 11/03','広告 10/27'", "['時間帯','広告 11/04','広告 10/28','広告 6日平均','表示 11/04','表示 10/28','表示 6日平均','LPV 11/04','LPV 10/28','LPV 6日平均','Meta購入 11/04','Meta購入 10/28','Meta購入 6日平均',"),
 ("'gross 11/03','gross 10/27'", "'gross 11/04','gross 10/28','gross 6日平均','注文 11/04','注文 10/28','注文 6日平均','gross÷広告 11/04','gross÷広告 10/28','gross÷広告 6日平均','セッション 11/04','カート 11/04'],"),
 ("wb.save('data/reports/report-2026-11-04.xlsx')", "wb.save('data/reports/report-2026-11-05.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は3日で+404,174円（134,725円/日）'],", "11月は4日で+499,006円（124,752円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（火曜・文化の日・CVR 2.62%・注文88件・来訪は多いがカゴ投入率が下端）' if d == '2026-11-03' else '（月曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（水曜・CVR 2.93%・注文70件・来訪は16日で最少だが来訪後は強い）' if d == '2026-11-04' else '（火曜・文化の日・CVR 2.62%・注文88件・来訪は多いがカゴ投入率が下端）' if d == '2026-11-03' else '（月曜")
for a, b in [("'2026-11-02':2801,'2026-11-03':3359}", "'2026-11-02':2801,'2026-11-03':3359,'2026-11-04':2387}"),
             ("'2026-11-02':75,'2026-11-03':88}", "'2026-11-02':75,'2026-11-03':88,'2026-11-04':70}")]:
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
REP.append((block(src, "ORD = {'伸縮ガラスクリーナー':125,", "（VIP特典は商品名2種を合算）"), ORD_NEW))
REP.append((block(src, "ORD30 = {'ナノガラス脱毛パッド':960,", "assert sum(ORD30.values()) == 3461, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'ナノガラス脱毛パッド':(2122148,1721491,25320),", "'コードレス毛玉クリーナー':(3783,1147,27)}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/3(火・祝)'", "\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/3(火) 01:18'", "\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ['11/03(火・祝)', "'/tmp/rep1103w.pkl'", 'hourly1103.json', 'report-2026-11-04.xlsx']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1105full.py', 'w').write(src)
print('mk1105full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
