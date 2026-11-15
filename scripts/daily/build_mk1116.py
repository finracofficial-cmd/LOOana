# -*- coding: utf-8 -*-
"""mk1113full.py から mk1116full.py を生成（昨日=11/15 日。11/14広告費確定）。11/14・11/15 の定例では Excel を作っていなかったので、11/13 版から3日分を一度に進める。
注文数（7日・30日）と30日Metaファネルは scripts/daily/o1115/*.json|txt、時間別は hourly1115.json から生成する。
v2 キャンペーン（ノーズ・シェーバー・フック・インソール）: 予算の記録は元の商品名、広告費はフックだけ旧＋v2 を足す（w1115.py の MULTI と同じ）。"""
import json, re
exec(open('scripts/daily/txt1113.py').read()); T0 = T
exec(open('scripts/daily/txt1116.py').read())
src = open('scripts/daily/mk1113full.py').read()

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
O7, s7 = ordd('scripts/daily/o1115/ord7_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-11-09 UNTIL 2026-11-15 ORDER BY orders DESC LIMIT 60')
O30, s30 = ordd('scripts/daily/o1115/ord30_raw.json', 'FROM sales SHOW orders GROUP BY product_title SINCE 2026-10-17 UNTIL 2026-11-15 ORDER BY orders DESC LIMIT 80')
_tot = json.load(open('scripts/daily/o1115/ord7_total_raw.json'))
assert _tot['query'] == 'FROM sales SHOW orders SINCE 2026-11-09 UNTIL 2026-11-15'; ORD7_STORE = int(_tot['rows'][0][0])
assert (s7, s30, ORD7_STORE) == (591, 3211, 492), (s7, s30, ORD7_STORE)
MF = {}
for ln in open('scripts/daily/o1115/mf30_raw.txt').read().split('\n')[1:]:
    if not ln.strip(): continue
    k, c, i, o = ln.strip().rsplit(',', 3); MF[k] = (int(c), int(i), 0 if o == 'null' else int(o))
assert len(MF) == 33, len(MF)
_ses = eval(re.search(r"SES = (\{.*?\})\n", src, re.S).group(1)); _ses.update({'2026-11-13': 2323, '2026-11-14': 2570, '2026-11-15': 2607})
D7W = ['2026-11-09', '2026-11-10', '2026-11-11', '2026-11-12', '2026-11-13', '2026-11-14', '2026-11-15']
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
 ('"""2026-11-13 定例レポート本体', '"""2026-11-16 定例レポート本体（昨日=11/15 日。11/14の広告費は確定値に上書き）。"""'),
 ("R = pickle.load(open('/tmp/rep1112w.pkl'", "R = pickle.load(open('/tmp/rep1115w.pkl', 'rb'))"),
 ("SNAP = '2026-11-13'", "SNAP = '2026-11-16c'   # 11/16 00:5x 時点（ユーザーの 00:3x・00:5x の変更後）の全セット＝Meta直読（16a・16b）を積んだ状態と一致（182,600）"),
 ("assert sum(BUD.values()) == 145000", "assert sum(BUD.values()) == 182600, sum(BUD.values())"),
 ("# --- 7日(11/06-11/12) Shopify注文数", "# --- 7日(11/09-11/15) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1115/ord7_raw.json から生成）---"),
 ("# --- 30日(10/14-11/12) Shopify注文数", "# --- 30日(10/17-11/15) Shopify注文数（ShopifyQL GROUP BY product_title 実測・scripts/daily/o1115/ord30_raw.json から生成）---"),
 ("# --- 30日(10/14-11/12) Metaファネル", "# --- 30日(10/17-11/15) Metaファネル（data_query 実測・Asia/Tokyo・アウトバウンドクリック・scripts/daily/o1115/mf30_raw.txt から生成）---"),
 ("sh('収益', [f'LOOTY 収益レポート 2026-11-13", "sh('収益', [f'LOOTY 収益レポート 2026-11-16（昨日 = 11/15 日）',"),
 (p0('head'), q(T['head']) + ','),
 (p0('ord'), q(T['ord']) + ','),
 (p0('ma'), q(T['ma']) + ','),
 (p0('chg'), q(T['chg']) + ','),
 (p0('judge'), q(T['judge']) + ','),
 (p0('fix'), q(T['fix']) + ','),
 ("for lbl, N, K, ACC in [('前日 11/12(木)'", "for lbl, N, K, ACC in [('前日 11/15(日)', R['N1'], R['K1'], R['ACCT1']), ('3日 11/13-11/15', R['N3'], R['K3'], R['ACCT3']),"),
 ("('7日 11/06-11/12'", "('7日 11/09-11/15', R['N7'], R['K7'], R['ACCT7']), ('30日 10/17-11/15', R['N30'], R['K30'], R['ACCT30']),"),
 ("'縦照合3本すべて通過（11/12）", "'縦照合3本すべて通過（11/15）: Σ商品gross=全店442,620 ／ Σ値引=20,010 ／ Σ広告費=キャンペーン合算180,535円（00時台の暫定・時間別 fresh は181,134円）。11/14も gross 328,270・値引8,759 で一致・広告費は確定163,714円',"),
 ("'✅ 11/11の広告費は再取得で確定済み", "'✅ 11/14の広告費は再取得で確定済み（163,528→**163,714円**。11/16に上書き）',"),
 ("'⚠️ 11/12の広告費は 11/13 01時台の取得【暫定】", "'⚠️ 11/15の広告費は 11/16 00時台の取得【暫定】→ 次回に再取得して確認する',"),
 (p0('returns'), q(T['returns']) + ','),
 ("ws.cell(r, 1, '■ 昨日(11/12 木)", "ws.cell(r, 1, '■ 昨日(11/15 日) × 期間比較').font = Font(name='Arial', bold=True, size=11); r += 1"),
 ("for c, v in enumerate(['指標','11/12(木)'", "for c, v in enumerate(['指標','11/15(日)','3日平均/日','7日平均/日','30日平均/日','vs7日平均'], 1): ws.cell(r, c, v)"),
 ("ws.cell(r+1, 1, " + p0('sumnote', 25), "ws.cell(r+1, 1, " + q(T['sumnote']) + ").font = Font(name='Arial', size=10, color='CC0000')"),
 ("sh('商品別', ['商品別（7日 11/06-11/12", "sh('商品別', ['商品別（7日 11/09-11/15 = 判定単位）。カタログ行の広告費は「7日合計」（前日ではない）',"),
 ("'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,367,680円", "'Σ商品広告費 + カタログ = Metaアカウント7日消化 1,230,140円（11/15分は暫定）',"),
 ("'当月累積利益は11月分（11/01〜・12日目）',", "'当月累積利益は11月分（11/01〜・15日目）',"),
 ("sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/14-11/12)", "sh('ファネル30日', ['⚠️ このシートだけ窓が「30日(10/17-11/15)」。他シートの7日窓と混ぜて読まないこと',"),
 ("'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/14-11/12)", "'✅ 検算: 全キャンペーンで data_query の消化 = CSV(10/17-11/15) が許容差以内で一致（コード内assert。11/15はCSVが00時台の暫定なので許容差を広げた）。フックは旧キャンペーン＋v2 を足して1行',"),
 (p0('today'), q(T['today']) + ','),
 ("'★次: 11/14(土)", "'★次: 11/17(火) クリーナー・ナノの上げ（3-B）／ブラシの下げ（11/15-16が続けて1.25未満）／ノーズ・シェーバーの4-2／フック v2 2日目 → 11/18(水) ワイパー・W固定・ドア／インソール v2 2日目 → 11/21(土) ノーズ・シェーバー7日 → 11/22(日) フック7日 → 11/26(木) 答え合わせ',"),
 ("if r[0] == '2026-11-12': PREVB[r[1]]", "if r[0] == '2026-11-15': PREVB[r[1]] += int(r[3])"),
 ("sh('予算見直しチェック', ['前日(11/12 00時台", "sh('予算見直しチェック', ['前日(11/15 00時台・2026-11-15)スナップショット → 本日(11/16 00:5x・Meta直読の積み上げ 2026-11-16c)。変更: 11/15 00:3x -sab 15,600→13,000・ドア 8,000→9,600・パンツ停止・ブランケット 8,000→10,000／00:4x ワイパー 25,000→20,000／15時台 フック v2 8,000／11/16 00:3x ノーズ 8,000→12,000・シェーバー 8,000→11,000・インソール停止／00:5x インソール v2 8,000',"),
 ("'合計 176,000 → **145,000円/日**", "'合計 182,600 → **182,600円/日**（±0。増: ノーズ+4,000・シェーバー+3,000・ブランケット+2,000・ドア+1,600・フック+8,000／減: パンツ−8,000・ワイパー−5,000・-sab−2,600・インソール−3,000〔11,000→v2 8,000〕）',"),
 ("'★体制: 12セット・145,000円/日", "'★体制: 15セット・182,600円/日。合計19万円のブレーキは廃止',"),
 ("'★11/12の消化は 183,140円", "'★11/15の消化は 180,535円（暫定）。11/14は確定163,714円、11/13は確定145,978円。W固定 -sab は11/15 01時台から配信0（理由は未確認・11/16に再公開）',"),
 ("'★眉シェーバーは停止中", "'★インソールは旧キャンペーン停止→ v2（新規キャンペーン）で8,000。予算の記録は元の商品名で持つ（ノーズ・シェーバー・フックも同じ）'],"),
 (p0('cvr1'), q(T['cvr1']) + ','),
 (p0('cvr2'), q(T['cvr2']) + ','),
 (p0('cvr3'), q(T['cvr3']) + ','),
 ("sh('曜日指数', ['直近30日(10/14-11/12)", "sh('曜日指数', ['直近30日(10/17-11/15)・祝日除外（11/3文化の日を除外）。売上=gross−値引。週次更新は月曜',"),
 (p0('dow'), q(T['dow']) + '],'),
 ("# ---------- 時間別（11/12 vs", "# ---------- 時間別（11/15 vs 前週日11/08 vs 11/09-11/14平均。Meta時間別 data_query / Shopify GROUP BY hour_of_day 実測）----------"),
 ("_H = _json.load(open('scripts/daily/hourly1112.json'))", "_H = _json.load(open('scripts/daily/hourly1115.json'))"),
 ("sh('時間別', ['時間帯別の比較: 11/12(木)", "sh('時間別', ['時間帯別の比較: 11/15(日) vs 前週日(11/8) vs 直近6日(11/9-11/14)平均。広告=Meta時間別（11/15は01時台 fresh・CSVの暫定より+599円）、売上=Shopify gross（値引前）、Meta購入=ピクセル計上',"),
 ("'読み方: 「表示」と「LPV」は配信量", "'読み方: 「表示」と「LPV」は配信量、「セッション・カート」は来訪後の反応。11/15は広告費が 0〜5時台−8%・6〜9時台+6%・10〜13時台+3%・14〜17時台+17%・18〜23時台−1%（6日平均比）、注文は 5・13・18・15・25（6日平均 9.2・15.0・14.8・10.2・20.2）。日中以降の注文が多い日',"),
 ("['時間帯','広告 11/12','広告 11/05'", "['時間帯','広告 11/15','広告 11/08','広告 6日平均','表示 11/15','表示 11/08','表示 6日平均','LPV 11/15','LPV 11/08','LPV 6日平均','Meta購入 11/15','Meta購入 11/08','Meta購入 6日平均',"),
 ("'gross 11/12','gross 11/05'", "'gross 11/15','gross 11/08','gross 6日平均','注文 11/15','注文 11/08','注文 6日平均','gross÷広告 11/15','gross÷広告 11/08','gross÷広告 6日平均','セッション 11/15','カート 11/15'],"),
 ("wb.save('data/reports/report-2026-11-13.xlsx')", "wb.save('data/reports/report-2026-11-16.xlsx')"),
 ("['4. 間隔','同じ商品は2日あける", "['4. 間隔','同じ商品は2日あける（上げも下げも。3-Aの増額だけ例外）','11/4〜11/12の9日で90回動かし、22商品中16商品を2日続けて・または1日2回動かしていた'],\n ['4-2. 上げたら確かめる','上げてから最初の終日の倍率が1.25以下なら、上げる前の予算に戻す。基準4の2日を待たない。戻したあと次に動かすのは2日あけてから','2026-11-15 ユーザー「予算を上げて1.25以下になったら戻す。効果が現れてないから」（最初の例: ワイパー 11/14 1.09 → 20,000）'],"),
]
for p, n in LR: rep_line(p, n)
src = '\n'.join(lines)
for a, b in [("11月は12日で+1,450,433円（120,869円/日）'],", "11月は15日で+1,702,564円（113,504円/日）'],")]:
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
_o = "('★昨日（木曜・CVR 2.79%・注文68件・6〜17時台が弱く18〜23時台は−14%）' if d == '2026-11-12' else '（水曜"
assert src.count(_o) == 1
src = src.replace(_o, "('★昨日（日曜・CVR 2.92%・注文76件・客単価5,561円・7,000円以上26%）' if d == '2026-11-15' else '（土曜・CVR 2.49%・注文64件・決済完了45.7%は15日で最低）' if d == '2026-11-14' else '（金曜・CVR 2.50%・注文58件）' if d == '2026-11-13' else '（木曜・CVR 2.79%・注文68件・6〜17時台が弱く18〜23時台は−14%）' if d == '2026-11-12' else '（水曜")
for a, b in [("'2026-11-11':2307,'2026-11-12':2434}", "'2026-11-11':2307,'2026-11-12':2434,'2026-11-13':2323,'2026-11-14':2570,'2026-11-15':2607}"),
             ("'2026-11-11':72,'2026-11-12':68}", "'2026-11-11':72,'2026-11-12':68,'2026-11-13':58,'2026-11-14':64,'2026-11-15':76}")]:
    assert src.count(a) == 1, a; src = src.replace(a, b)
# ---- v2 キャンペーン: 予算の記録（元の商品名）と広告費（フックは旧＋v2）----
PATCH = [
 ("MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}",
  "MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}\n"
  "MULTI = {'高見えレザーヘッドレストフック': ('高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv2'), '快適マジックインソール': ('快適マジックインソール', '快適マジックインソールv2')}   # w1115.py と同じ（広告費は旧＋v2）\n"
  "BNAME = {n: n for n, c in MAP.items() if c.endswith('v2')}   # 予算の記録は元の商品名（ノーズ・シェーバー）\n"
  "INV.update({'高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '快適マジックインソールv2': '快適マジックインソール'})"),
 ("MF = {INV.get(k, k): v for k, v in MF_RAW.items()}",
  "MF = {}\nfor _k, _v in MF_RAW.items():\n    _n = INV.get(_k, _k); _o = MF.get(_n, (0, 0, 0)); MF[_n] = tuple(a + b for a, b in zip(_o, _v))   # フックは旧＋v2 を足して1行"),
 ("    a = sum(ADd[MAP.get(n, n)].get(d, 0) for d in days)\n    return g - dc, c, a",
  "    a = sum(ADd[_c].get(d, 0) for _c in MULTI.get(n, (MAP.get(n, n),)) for d in days)\n    return g - dc, c, a"),
 ("        _cur = BUDL.get(MAP.get(n, n)); _a1",
  "        _cur = BUDL.get(BNAME.get(n, MAP.get(n, n))); _a1"),
 ("    cp = MAP.get(n, n); days = [d for d in D7 if d in BSNAP[cp]]\n    wu = (a7 / sum(BSNAP[cp][d] for d in days)) if len(days) == 7 and sum(BSNAP[cp][d] for d in days) else None",
  "    cp = MAP.get(n, n); bcp = BNAME.get(n, cp); days = [d for d in D7 if d in BSNAP[bcp]]\n    wu = (a7 / sum(BSNAP[bcp][d] for d in days)) if len(days) == 7 and sum(BSNAP[bcp][d] for d in days) else None"),
 ("    cur = BUDL.get(cp); small = bool(cur) and cur <= SMALL", "    cur = BUDL.get(bcp); small = bool(cur) and cur <= SMALL"),
 ("    chg = last_change(cp)\n", "    chg = last_change(bcp)\n"),
 ("    elif first_ad and first_ad > D7[0]:", "    elif first_ad and first_ad > D7[0] and not (n in CAL and CAL[n][0] == TODAY and CAL[n][1].startswith('📌')):"),
 ("        act, memo, rj, basis = weekly_rule(n, cp, small, chg)", "        act, memo, rj, basis = weekly_rule(n, bcp, small, chg)"),
 ("_shown = {MAP.get(r[0], r[0]) for r in SIMPLE}", "_shown = {BNAME.get(r[0], MAP.get(r[0], r[0])) for r in SIMPLE}"),
 ("def ucost(n, d):\n", "def pricea(n, d):\n    return 6980 if (n == 'スマートノーズEMS美顔器' and d >= '2026-11-14') else PRICEa[n]   # 11/14 16:51 値上げ（w1115.py の PRICEBYDATE と同じ）\ndef ucost(n, d):\n"),
 ("Sd[n][d][0] / PRICEa[n] * ucost(n, d)) for d in days", "Sd[n][d][0] / pricea(n, d) * ucost(n, d)) for d in days"),
 ("        elif n in PRICEa and n in COSTa: c += g / PRICEa[n] * ucost(n, d)", "        elif n in PRICEa and n in COSTa: c += g / pricea(n, d) * ucost(n, d)"),
 ("        if g and n in PRICEa and n in COSTa: c += g/PRICEa[n]*COSTa[n]", "        if g and n in PRICEa and n in COSTa: c += g/pricea(n, d)*COSTa[n]"),
 ("for cp, byday in _BS.items():\n    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]",
  "for cp, byday in _BS.items():\n    for d, snaps in byday.items(): BSNAP[cp][d] = snaps[max(snaps)]\n"
  "# 8行未満のスナップショットは変わった行だけ＝広告セット単位で前の状態に上書きして積む（moves1116.py と同じ）。その日の最後の状態をその日の予算にする\n"
  "_ROWS = collections.defaultdict(dict)\nfor r in body: _ROWS[r[0]][(r[1], r[2])] = int(r[3])\n_ST = {}; _STK = {}\n"
  "for _k in sorted(_ROWS):\n    _ST = dict(_ROWS[_k]) if len(_ROWS[_k]) >= 8 else {**_ST, **_ROWS[_k]}\n    _STK[_k] = dict(_ST)\n"
  "BSNAP = collections.defaultdict(lambda: collections.defaultdict(int))\n"
  "for _k in sorted(_STK):\n    _sum = collections.defaultdict(int)\n    for (_c, _a), _v in _STK[_k].items(): _sum[_c] += _v\n    for _c in set(_sum) | set(BSNAP):\n        BSNAP[_c][_k[:10]] = _sum.get(_c, 0)"),
 ("for r in body: _BK[r[0]][r[1]] += int(r[3])\n", "for _k in _STK:\n    for (_c, _a), _v in _STK[_k].items(): _BK[_k][_c] += _v   # 積み上げた状態（キャンペーン合計）\n"),
 ("    assert abs(_c - _v[0]) <= max(50, _v[0] * 0.0005), (_k, _c, _v[0])",
  "    assert abs(_c - _v[0]) <= max(500, _v[0] * 0.002), (_k, _c, _v[0])   # 11/15 は CSV が 00時台の暫定・ファネルは01時台の取得"),
]
for a, b in PATCH:
    assert src.count(a) == 1, ('PATCH 対象が一意でない/見つからない', a[:70], src.count(a))
    src = src.replace(a, b)
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
REP.append((block(src, "ORD30 = {'", "assert sum(ORD30.values()) == 3306, sum(ORD30.values())"), ORD30_NEW))
REP.append((block(src, "MF_RAW = {'", ")}"), MF_NEW))
REP.append((block(src, "NA = [\n ['📊 11/12(木)'", "\n]"), T['NA']))
REP.append((block(src, "JUDGE = [\n ['11/13(金)'", "\n]"), T['JUDGE']))
for old, new in REP:
    assert src.count(old) == 1, ('置換対象が一意でない/見つからない', old[:70], src.count(old))
    src = src.replace(old, new)
for bad in ["'/tmp/rep1112w.pkl'", 'hourly1112.json', 'report-2026-11-13.xlsx', '11/12(木)は 実売']:
    assert bad not in src, ('置き換え漏れ', bad)
open('scripts/daily/mk1116full.py', 'w').write(src)
print('mk1116full.py written,', len(src.splitlines()), 'lines; SESS7', SESS7)
