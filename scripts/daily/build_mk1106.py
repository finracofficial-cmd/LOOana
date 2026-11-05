# -*- coding: utf-8 -*-
"""mk1105full.py から mk1106full.py を生成（昨日=11/05 木。11/04広告費確定・ブレーキ継続）。
注文数（7日・30日）と30日Metaファネルは、取得結果を保存した scripts/daily/o1105/*.json|txt から生成する（ord7/ord30は商品名を短縮名で保存・合計と行数をassert）。"""
import json, re
exec(open('scripts/daily/txt1105.py').read()); T0 = T
exec(open('scripts/daily/txt1106.py').read())
src = open('scripts/daily/mk1105full.py').read()

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
O7, s7 = ordd('scripts/daily/o1105/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-30 UNTIL 2026-11-05 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1105/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-07 UNTIL 2026-11-05 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1105/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-10-30 UNTIL 2026-11-05'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (701, 3417, 567), (s7, s30, ORD7_STORE)
_known = set(eval(re.search(r"ORD30 = (\{.*?\})\n", src, re.S).group(1))) | set(eval(re.search(r"ORD = (\{.*?\})\n", src, re.S).group(1))) | {'ワイド水切りワイパー', '4WAY 取り付けOK 小型瞬間冷却ハンディファン', 'クリアビューレインガードフィルム', 'コードレス毛玉クリーナー'}
assert set(O7) <= _known and set(O30) <= _known, (set(O7) - _known, set(O30) - _known)
MF = {}
for ln in open('scripts/daily/o1105/mf30_raw.txt').read().split('\n')[1:]:
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), int(o))
assert len(MF) == 30, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses['2026-11-05'] = 2874
D7W = ['2026-10-%02d' % d for d in range(30, 32)] + ['2026-11-01', '2026-11-02', '2026-11-03', '2026-11-04', '2026-11-05']
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
 ('"""2026-11-05 定例レポート本体', '"""2026-11-06 定例レポート本体（昨日=11/05 木。11/04の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1104w.pkl'", "R = pickle.load(open('/tmp/rep1105w.pkl', 'rb'))"),
 ("SNAP = '2026-11-05'", "SNAP = '2026-11-06'   # 11/06 00時台 Meta読み（adsetdaily_budget）の日予算が 2026-11-05f と一致（15セット・192,000）"),
 ("assert sum(BUD.values()) == 190000", "assert sum(BUD.values()) == 192000, sum(BUD.values())"),
 ("# --- 7日(10/29-11/04) Shopify注文数", "# --- 7日(10/30-11/05) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1105/ord7_raw.json から生成）---"),
 ("# --- 30日(10/06-11/04) Shopify注文数", "# --- 30日(10/07-11/05) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1105/ord30_raw.json から生成）---"),
 ("# --- 30日(10/06-11/04) Metaファネル", "# --- 30日(10/07-11/05) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1105/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-05", "sh('収益', [f'LOOTY 収益レポート 2026-11-06（昨日 = 11/05 木）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/04(水)'", "for lbl, N, K, ACC in [('前日 11/05(木)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/03-11/05', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 10/29-11/04'", "('7日 10/30-11/05', R['N7'], R['K7'], R['ACCT7']), ('30日 10/07-11/05', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/04）", "'縦照合3本すべて通過（11/05）: Σ商品gross=全店461,960 ／ Σ値引=19,069 ／ Σ広告費=キャンペーン合算203,228円（11/04も gross 418,140・値引20,162 で一致）',"),
 ("'✅ 11/03の広告費は再取得で確定済み", "'✅ 11/04の広告費は再取得で確定済み（186,751→**187,231円**。11/06に上書き）',"),
 ("'⚠️ 11/04の広告費は 11/05 00時台の取得【暫定】", "'⚠️ 11/05の広告費は 11/06 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/04 水)", "ws.cell(r, 1, '■ 昨日(11/05 木) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/04(水)'", "for c, v in enumerate(['指標','11/05(木)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 10/29-11/04", "sh('商品別', ['商品別（7日 10/30-11/05 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,509,044円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,459,035円（11/05分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・4日目）',", "'当月累積利益は11月分（11/01〜・5日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/06-11/04)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/07-11/05)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/06-11/04)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/07-11/05) が許容差以内で一致（コード内assert）',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/6(金) 加湿器・毛玉・ワイパー2日目", "'★次: 11/7(土) ドアクッション7日（10/31-11/6）・レインガード2日目 → 11/8(日) 11/4〜5の変更の答え合わせ（11/5-7）→ 11/9(月) 週次（11/2-8）→ 11/11(水) インソール新CR・加湿器・ワイパー7日 → 11/12(木) レインガード7日',"),
 ("if r[0] == '2026-11-04': PREVB[r[1]]", "if r[0] == '2026-11-05': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/04 00時", "sh('予算見直しチェック', ['前日(11/05 00時・2026-11-05)スナップショット → 本日(11/06 00時台・Meta読み)。11/05の変更: 01:10 毛玉停止・加湿器増額・クリーナー主力減・インソール減／01時台 ナノバブル再開→11時台停止／12:56 ワイパー増額／22時台 レインガード新規',"),
 ("'合計 189,000 → **190,000円/日**", "'合計 190,000 → **192,000円/日**（+2,000＝レインガード+8,000・ワイパー+4,000・加湿器+3,000／毛玉−8,000・インソール−3,000・クリーナー−2,000）',"),
 ("'★体制: 15セット・190,000円/日", "'★体制: 15セット・192,000円/日（⚠️ブレーキ継続: 3日移動平均107,687円 <130,000 → 合計を増やさない。ブレーキ時の190,000を2,000上回る）',"),
 ("'★11/04の消化は 186,751円", "'★11/05の消化は 203,228円（暫定）。11/04は確定187,231円、11/03は確定212,735円',"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/06-11/04)", "sh('曜日指数', ['直近30日(10/07-11/05)・祝日除外（10/12スポーツの日・11/3文化の日を除外）。売上=gross−値引。次回定期更新11/9(月)',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/04 vs", "# ---------- 時間別（11/05 vs 前週木10/29 vs 10/30-11/04平均。Meta時間別 data_query / Shopify TIMESERIES hour 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1104.json'))", "_H = _json.load(open('scripts/daily/hourly1105.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/4(水)", "sh('時間別', ['時間帯別の比較: 11/5(木) vs 前週木(10/29) vs 直近6日(10/30-11/4)平均。広告=Meta時間別（11/5は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/5は0〜5時台の広告費が6日平均より多く（+36%）、6〜13時台は少なめ（−8%・−12%）。注文は 0〜5時台 9（6日平均9.0）・6〜9時台 15（18.3）・10〜13時台 21（14.7・gross+52%）・14〜17時台 16（15.7）・18〜23時台 19（23.5）＝昼前後が強く、朝と夜は少なめ',"),
 ("['時間帯','広告 11/04','広告 10/28'", "['時間帯','広告 11/05','広告 10/29','広告 6日平均','表示 11/05','表示 10/29','表示 6日平均','LPV 11/05','LPV 10/29','LPV 6日平均','Meta購入 11/05','Meta購入 10/29','Meta購入 6日平均',"),
 ("'gross 11/04','gross 10/28'", "'gross 11/05','gross 10/29','gross 6日平均','注文 11/05','注文 10/29','注文 6日平均','gross÷広告 11/05','gross÷広告 10/29','gross÷広告 6日平均','セッション 11/05','カート 11/05'],"),
 ("wb.save('data/reports/report-2026-11-05.xlsx')", "wb.save('data/reports/report-2026-11-06.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は4日で+499,006円（124,752円/日）'],", "11月は5日で+609,552円（121,910円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（水曜・CVR 2.93%・注文70件・来訪は16日で最少だが来訪後は強い）' if d == '2026-11-04' else '（火曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（木曜・CVR 2.78%・注文80件・10〜13時台が強い）' if d == '2026-11-05' else '（水曜・CVR 2.93%・注文70件・来訪は16日で最少だが来訪後は強い）' if d == '2026-11-04' else '（火曜")
for a, b in [("'2026-11-03':3359,'2026-11-04':2387}", "'2026-11-03':3359,'2026-11-04':2387,'2026-11-05':2874}"),
             ("'2026-11-03':88,'2026-11-04':70}", "'2026-11-03':88,'2026-11-04':70,'2026-11-05':80}")]:
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
REP.append((block(src, "ORD30 = {'ナノガラス脱毛パッド':933,", "assert sum(ORD30.values()) == 3442, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'ナノガラス脱毛パッド':(2076525,1695569,24829),", "'ロングニトリル家事手袋':(4366,824,19)}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/4(水)'", "\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/4(水) 09:50〜20:29'", "\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ['11/04(水)', "'/tmp/rep1104w.pkl'", 'hourly1104.json', 'report-2026-11-05.xlsx']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1106full.py', 'w').write(src)
print('mk1106full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
