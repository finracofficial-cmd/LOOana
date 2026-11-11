# -*- coding: utf-8 -*-
"""mk1111full.py から mk1112full.py を生成（昨日=11/11 水。11/10広告費確定）。
注文数（7日・30日）と30日Metaファネルは、取得結果を保存した scripts/daily/o1111/*.json|txt から生成する（ord7/ord30は商品名を短縮名で保存・合計と行数をassert）。"""
import json, re
exec(open('scripts/daily/txt1111.py').read()); T0 = T
exec(open('scripts/daily/txt1112.py').read())
src = open('scripts/daily/mk1111full.py').read()

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
O7, s7 = ordd('scripts/daily/o1111/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-11-05 UNTIL 2026-11-11 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1111/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-13 UNTIL 2026-11-11 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1111/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-11-05 UNTIL 2026-11-11'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (748, 3340, 612), (s7, s30, ORD7_STORE)
_known = set(eval(re.search(r"ORD30 = (\{.*?\})\n", src, re.S).group(1))) | set(eval(re.search(r"ORD = (\{.*?\})\n", src, re.S).group(1))) | {'ワイド水切りワイパー', '4WAY 取り付けOK 小型瞬間冷却ハンディファン', 'クリアビューレインガードフィルム', 'コードレス毛玉クリーナー', 'シリコンホールド膝サポーター', '防風あったか裏起毛パンツ', 'すき間収納シートポケット'}
assert set(O7) <= _known and set(O30) <= _known, (set(O7) - _known, set(O30) - _known)
MF = {}
for ln in open('scripts/daily/o1111/mf30_raw.txt').read().split('\n')[1:]:
    if not ln.strip(): continue
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), 0 if o == 'null' else int(o))
assert len(MF) == 32, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses['2026-11-11'] = 2307
D7W = ['2026-11-05', '2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09', '2026-11-10', '2026-11-11']
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
 ('"""2026-11-11 定例レポート本体', '"""2026-11-12 定例レポート本体（昨日=11/11 水。11/10の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1110w.pkl'", "R = pickle.load(open('/tmp/rep1111w.pkl', 'rb'))"),
 ("SNAP = '2026-11-11'", "SNAP = '2026-11-12'   # 11/12 00時台 Meta直読（13キャンペーン）の日予算が 2026-11-11i と一致（15セット・176,000）"),
 ("assert sum(BUD.values()) == 182000", "assert sum(BUD.values()) == 176000, sum(BUD.values())"),
 ("# --- 7日(11/04-11/10) Shopify注文数", "# --- 7日(11/05-11/11) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1111/ord7_raw.json から生成）---"),
 ("# --- 30日(10/12-11/10) Shopify注文数", "# --- 30日(10/13-11/11) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1111/ord30_raw.json から生成）---"),
 ("# --- 30日(10/12-11/10) Metaファネル", "# --- 30日(10/13-11/11) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1111/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-11", "sh('収益', [f'LOOTY 収益レポート 2026-11-12（昨日 = 11/11 水）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/10(火)'", "for lbl, N, K, ACC in [('前日 11/11(水)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/09-11/11', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 11/04-11/10'", "('7日 11/05-11/11', R['N7'], R['K7'], R['ACCT7']), ('30日 10/13-11/11', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/10）", "'縦照合3本すべて通過（11/11）: Σ商品gross=全店346,920 ／ Σ値引=8,756 ／ Σ広告費=キャンペーン合算189,643円＝Meta時間別合計（11/10も gross 375,780・値引10,547 で一致）',"),
 ("'✅ 11/09の広告費は再取得で確定済み", "'✅ 11/10の広告費は再取得で確定済み（165,063→**165,869円**。11/12に上書き）',"),
 ("'⚠️ 11/10の広告費は 11/11 00時台の取得【暫定】", "'⚠️ 11/11の広告費は 11/12 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/10 火)", "ws.cell(r, 1, '■ 昨日(11/11 水) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/10(火)'", "for c, v in enumerate(['指標','11/11(水)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 11/04-11/10", "sh('商品別', ['商品別（7日 11/05-11/11 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,384,377円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,387,595円（11/11分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・10日目）',", "'当月累積利益は11月分（11/01〜・11日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/12-11/10)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/13-11/11)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/12-11/10)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/13-11/11) が許容差以内で一致（コード内assert）',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/12(木)", "'★次: 11/13(金) 裏起毛パンツ・すき間ポケットの2日目／車載の答え合わせ／ドア（2日続けて1.25未満なら8,800）→ 11/14(土) クリーナー主力・ナノの増額の答え合わせ → 11/15(日) レインガード・ワイパー・ブラシ・4-in-1（新しい予算での3日）→ 11/16(月) 週次 → 11/19(木) 加湿器・新商品2本の7日',"),
 ("if r[0] == '2026-11-10': PREVB[r[1]]", "if r[0] == '2026-11-11': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/10 00時台", "sh('予算見直しチェック', ['前日(11/11 00時台・2026-11-11)スナップショット → 本日(11/12 00時台・Meta直読)。11/11の変更は8回（11b〜11i）: 00:15 ワイパー・レインガード・ブラシ減／ドア増／アーチフィット停止 → 00:24 フック・シートボックス再開 → 09:48 同2本停止・ワイパー/クリーナー主力/ナノ増 → 12:08 レインガード減 → 16:11 裏起毛パンツ新規 → 17:24 加湿器再開 → 20:28 レインガード・ワイパー・ブラシ・4-in-1減／チェア停止 → 22:30 すき間ポケット新規',"),
 ("'合計 198,000 → **182,000円/日**", "'合計 182,000 → **176,000円/日**（−6,000＝ワイパー−4,000・レインガード−9,000・ブラシ−6,000・4-in-1 −3,000・チェア停止−9,000・アーチフィット停止−8,000・ドア+3,000・クリーナー主力+3,000・ナノ+3,000・裏起毛パンツ+8,000・加湿器+8,000・すき間ポケット+8,000）',"),
 ("'★体制: 14セット・182,000円/日", "'★体制: 15セット・176,000円/日（3日移動平均87,395円＝合計を190,000円より増やさない）',"),
 ("'★11/10の消化は 165,063円", "'★11/11の消化は 189,643円（暫定。日中に予算が8回動いたため、終日予算に対する消化率は出さない）。11/10は確定165,869円、11/09は確定200,083円',"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/12-11/10)", "sh('曜日指数', ['直近30日(10/13-11/11)・祝日除外（11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/10 vs", "# ---------- 時間別（11/11 vs 前週水11/04 vs 11/05-11/10平均。Meta時間別 data_query / Shopify TIMESERIES hour 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1110.json'))", "_H = _json.load(open('scripts/daily/hourly1111.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/10(火)", "sh('時間別', ['時間帯別の比較: 11/11(水) vs 前週水(11/4) vs 直近6日(11/5-11/10)平均。広告=Meta時間別（11/11は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/11は広告費が 0〜5時台+13%・6〜9時台−8%・10〜13時台−11%・14〜17時台−17%・18〜23時台+3%（6日平均比）なのに対し、LPVは全時間帯で−21〜−33%。注文は 0〜5時台 15（6日平均9.3）・6〜9時台 16（18.8）・10〜13時台 15（21.2）・14〜17時台 9（15.2・gross−45%）・18〜23時台 17（25.5・gross−41%・前週水24）。23時台のLPVは着地途中',"),
 ("['時間帯','広告 11/10','広告 11/03'", "['時間帯','広告 11/11','広告 11/04','広告 6日平均','表示 11/11','表示 11/04','表示 6日平均','LPV 11/11','LPV 11/04','LPV 6日平均','Meta購入 11/11','Meta購入 11/04','Meta購入 6日平均',"),
 ("'gross 11/10','gross 11/03'", "'gross 11/11','gross 11/04','gross 6日平均','注文 11/11','注文 11/04','注文 6日平均','gross÷広告 11/11','gross÷広告 11/04','gross÷広告 6日平均','セッション 11/11','カート 11/11'],"),
 ("wb.save('data/reports/report-2026-11-11.xlsx')", "wb.save('data/reports/report-2026-11-12.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は10日で+1,328,167円（132,817円/日）'],", "11月は11日で+1,389,783円（126,344円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（火曜・CVR 3.32%・注文75件・来訪は16日で最少・18〜23時台は平常）' if d == '2026-11-10' else '（月曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（水曜・CVR 3.12%・注文72件・客単価4,697円は16日で最低・18〜23時台が弱い）' if d == '2026-11-11' else '（火曜・CVR 3.32%・注文75件・来訪は16日で最少・18〜23時台は平常）' if d == '2026-11-10' else '（月曜")
for a, b in [("'2026-11-09':2936,'2026-11-10':2260}", "'2026-11-09':2936,'2026-11-10':2260,'2026-11-11':2307}"),
             ("'2026-11-09':79,'2026-11-10':75}", "'2026-11-09':79,'2026-11-10':75,'2026-11-11':72}")]:
    assert src.count(a) == 1, a; src = src.replace(a, b)
# 収益タブの日次利益: 新商品2本（裏起毛パンツ・すき間ポケット）は色・サイズで原価が違うため、
# 代表原価×個数ではなく daily_variant.csv の実測構成で原価を積む（代表原価のままだと 11/11 で原価が481円多く出る）
_a = "def ucost(n, d):"
assert src.count(_a) == 1
src = src.replace(_a, """VEXG = {'防風あったか裏起毛パンツ': ({'S':3980,'M':3980,'L':3980,'XL':3980,'XL灰':3980,'XXL':3980}, {'S':1140,'M':1148,'L':1219,'XL':1233,'XL灰':1338,'XXL':1251}),
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
def ucost(n, d):""")
_a = "    c = sum(Sd[n][d][0] / PRICEa[n] * ucost(n, d) for d in days if d in Sd[n]) if g and n in PRICEa and n in COSTa else 0"
assert src.count(_a) == 1
src = src.replace(_a, "    c = sum((VEXC[(n, d)] if n in VEXG else Sd[n][d][0] / PRICEa[n] * ucost(n, d)) for d in days if d in Sd[n]) if g and n in PRICEa and n in COSTa else 0")
_a = "        if n in PRICEa and n in COSTa: c += g / PRICEa[n] * ucost(n, d)"
assert src.count(_a) == 1
src = src.replace(_a, "        if n in VEXG: c += VEXC[(n, d)]\n        elif n in PRICEa and n in COSTa: c += g / PRICEa[n] * ucost(n, d)")
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
REP.append((block(src, "ORD30 = {'", "assert sum(ORD30.values()) == 3402, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'", ")}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/10(火)'", "\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/11(水)'", "\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ['11/10(火)', "'/tmp/rep1110w.pkl'", 'hourly1110.json', 'report-2026-11-11.xlsx']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1112full.py', 'w').write(src)
print('mk1112full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
