# -*- coding: utf-8 -*-
"""mk1103full.py から mk1104full.py を生成（昨日=11/03 火・文化の日。11/02広告費確定・ブレーキ解除・チェア7日判定）。
注文数（7日・30日）と30日Metaファネルは、取得結果をそのまま保存した scripts/daily/o1103/*.json|txt から生成する（手で転記しない）。"""
import json, re
exec(open('scripts/daily/txt1103.py').read()); T0 = T
exec(open('scripts/daily/txt1104.py').read())
src = open('scripts/daily/mk1103full.py').read()

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
O7, s7 = ordd('scripts/daily/o1103/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-28 UNTIL 2026-11-03 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1103/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-05 UNTIL 2026-11-03 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1103/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-10-28 UNTIL 2026-11-03'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (709, 3461, 584), (s7, s30, ORD7_STORE)
_known = set(eval(re.search(r"ORD30 = (\{.*?\})\n", src, re.S).group(1))) | set(eval(re.search(r"ORD = (\{.*?\})\n", src, re.S).group(1))) | {'ファスナー修理キット'}
assert set(O7) <= _known and set(O30) <= _known, (set(O7) - _known, set(O30) - _known)
MF = {}
for ln in open('scripts/daily/o1103/mf30_raw.txt').read().split('\n')[1:]:
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), int(o))
assert len(MF) == 28, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses['2026-11-03'] = 3359
D7W = ['2026-10-%02d' % d for d in range(28, 32)] + ['2026-11-01', '2026-11-02', '2026-11-03']
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
 ('"""2026-11-03 定例レポート本体', '"""2026-11-04 定例レポート本体（昨日=11/03 火・文化の日。11/02の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1102w.pkl'", "R = pickle.load(open('/tmp/rep1103w.pkl', 'rb'))"),
 ("SNAP = '2026-11-03'", "SNAP = '2026-11-04'   # 11/04 06時 Meta直読の日予算が 2026-11-03h と一致（13セット・189,000）"),
 ("assert sum(BUD.values()) == 208000", "assert sum(BUD.values()) == 189000, sum(BUD.values())"),
 ("# --- 7日(10/27-11/02) Shopify注文数", "# --- 7日(10/28-11/03) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1103/ord7_raw.json から生成）---"),
 ("# --- 30日(10/04-11/02) Shopify注文数", "# --- 30日(10/05-11/03) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1103/ord30_raw.json から生成）---"),
 ("# --- 30日(10/04-11/02) Metaファネル", "# --- 30日(10/05-11/03) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1103/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-03", "sh('収益', [f'LOOTY 収益レポート 2026-11-04（昨日 = 11/03 火・文化の日）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/02(月)'", "for lbl, N, K, ACC in [('前日 11/03(火・祝)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/01-11/03', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 10/27-11/02'", "('7日 10/28-11/03', R['N7'], R['K7'], R['ACCT7']), ('30日 10/05-11/03', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/02）", "'縦照合3本すべて通過（11/03）: Σ商品gross=全店450,670 ／ Σ値引=13,140 ／ Σ広告費=キャンペーン合算212,514円（11/02も gross 378,030・値引9,154 で一致）',"),
 ("'✅ 11/01の広告費は再取得で確定済み", "'✅ 11/02の広告費は再取得で確定済み（216,088→**216,365円**。11/04に上書き）',"),
 ("'⚠️ 11/02の広告費は 11/03 00時台の取得【暫定】", "'⚠️ 11/03の広告費は 11/04 朝の取得【暫定】→ 次回に再取得して確認する',"),
 ("'★ガラスクリーナー・ヘッドレストフックの原価", "'★ガラスクリーナーの原価は保守側の最高値バリアント単価で計上。ヘッドレストフックは10/7以降のCJ原価732円で計上（11/3にproduct_tabsの1,344を訂正）',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/02 月)", "ws.cell(r, 1, '■ 昨日(11/03 火・祝) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/02(月)'", "for c, v in enumerate(['指標','11/03(火・祝)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 10/27-11/02", "sh('商品別', ['商品別（7日 10/28-11/03 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,577,164円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,554,749円（11/03分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・2日目）',", "'当月累積利益は11月分（11/01〜・3日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/04-11/02)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/05-11/03)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/04-11/02)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/05-11/03) が許容差以内で一致（コード内assert）',"),
 ("'非常ブレーキ: 3日移動平均利益 < 130,000円 で発動", "'非常ブレーキ: 3日移動平均利益 < 130,000円 で発動（最新の判定は「収益」シートのブレーキ列）'],"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/4(水) インソール4・フック２の3日比較", "'★次: 11/6(金) 加湿器2日目（11/4-5）→ 11/7(土) ドアクッション7日（10/31-11/6）→ 11/9(月) 週次（11/2-8）＋11/3の変更の答え合わせ → 11/10 フック停止の答え合わせ → 11/11 加湿器7日',"),
 ("if r[0] == '2026-11-02': PREVB[r[1]]", "if r[0] == '2026-11-03': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/02 04時", "sh('予算見直しチェック', ['前日(11/03 00時・2026-11-03)スナップショット → 本日(11/04 06時・Meta直読)。11/03の変更: 01:18 一括変更／フック停止／ファスナー・毛玉 出稿→停止／ドアクッション+4,000／かかと冬停止・ナノA+4,000／加湿器再開',"),
 ("'合計 204,000 → **208,000円/日**", "'合計 208,000 → **189,000円/日**（−19,000＝フック−12,000・インソール4 −8,000・ナノ−4,000（かかと冬停止−8,000・A+4,000）・クリーナー−4,000・ブラシ−3,000・シーラー−2,000／ドア+4,000・4-in-1 +2,000・加湿器+8,000。ファスナー・毛玉は11/3中に出稿→停止で差0）',"),
 ("'★体制: 16セット・208,000円/日", "'★体制: 13セット・189,000円/日（✅ブレーキ解除: 3日移動平均134,725円 ≥130,000。基準246,000まで57,000）',"),
 ("'★11/02の消化は 216,088円", "'★11/03の消化は 212,514円（暫定）。11/02は確定216,365円、11/01は確定230,113円',"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/04-11/02)", "sh('曜日指数', ['直近30日(10/05-11/03)・祝日除外（10/12スポーツの日・11/3文化の日を除外）。売上=gross−値引。次回定期更新11/9(月)',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/02 vs", "# ---------- 時間別（11/03 vs 前週火10/27 vs 10/28-11/02平均。Meta時間別 data_query / Shopify GROUP BY hour_of_day 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1102.json'))", "_H = _json.load(open('scripts/daily/hourly1103.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/2(月)", "sh('時間別', ['時間帯別の比較: 11/3(火・祝) vs 前週火(10/27) vs 直近6日(10/28-11/2)平均。広告=Meta時間別（11/3は暫定）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/3は広告費が6日平均と同程度（−29〜+19%）でLPVは多い（−1〜+62%）。注文は 0〜5時台 8（6日平均8.0）・6〜9時台 17（21.0）・10〜13時台 14（16.2）、14〜17時台 23（15.7・gross+57%）、18〜23時台 26（21.8）',"),
 ("['時間帯','広告 11/02','広告 10/26'", "['時間帯','広告 11/03','広告 10/27','広告 6日平均','表示 11/03','表示 10/27','表示 6日平均','LPV 11/03','LPV 10/27','LPV 6日平均','Meta購入 11/03','Meta購入 10/27','Meta購入 6日平均',"),
 ("'gross 11/02','gross 10/26'", "'gross 11/03','gross 10/27','gross 6日平均','注文 11/03','注文 10/27','注文 6日平均','gross÷広告 11/03','gross÷広告 10/27','gross÷広告 6日平均','セッション 11/03','カート 11/03'],"),
 ("wb.save('data/reports/report-2026-11-03.xlsx')", "wb.save('data/reports/report-2026-11-04.xlsx')"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("'★10月確定: 31日で+4,174,310円（26.0%・134,655円/日）。11月は2日で+286,769円（143,384円/日）'],",
              "'★10月確定: 31日で+4,174,310円（26.0%・134,655円/日）。11月は3日で+404,174円（134,725円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（月曜・CVR 2.68%・注文75件・来訪が少ない＋13〜15時台の穴）' if d == '2026-11-02' else '（日曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（火曜・文化の日・CVR 2.62%・注文88件・来訪は多いがカゴ投入率が下端）' if d == '2026-11-03' else '（月曜・CVR 2.68%・注文75件・来訪が少ない＋13〜15時台の穴）' if d == '2026-11-02' else '（日曜")
for a, b in [("'2026-11-01':2916,'2026-11-02':2801}", "'2026-11-01':2916,'2026-11-02':2801,'2026-11-03':3359}"),
             ("'2026-11-01':112,'2026-11-02':75}", "'2026-11-01':112,'2026-11-02':75,'2026-11-03':88}")]:
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
REP.append((block(src, "ORD = {'ナノガラス脱毛パッド':124,", "assert sum(ORD.values()) == 714, sum(ORD.values())   # 全店590より多いのは複数商品を含む注文が両方で数えられるため（VIP特典は商品名2種を合算）"), ORD_NEW))
REP.append((block(src, "ORD30 = {'ナノガラス脱毛パッド':993,", "assert sum(ORD30.values()) == 3496, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'ナノガラス脱毛パッド':(2191063,1763320,26225),", "'ロングニトリル家事手袋':(4366,824,19)}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/2(月)'", "'ユーザー','随時'],\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/2(月)','週次: 4-in-1 8,000'", "'待機','—'],\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ['11/02(月)', "'/tmp/rep1102w.pkl'", 'hourly1102.json', 'report-2026-11-03.xlsx']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1104full.py', 'w').write(src)
print('mk1104full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
