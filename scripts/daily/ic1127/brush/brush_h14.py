# -*- coding: utf-8 -*-
"""11/27 14:0x「ぶらしやっぱだめ？」（再開は 11/26 17:21・旧キャンペーン・広告A だけ・8,000円）
入力: brush_meta_1126_1127_1402_raw.json（Meta・日別。11/27 は 14:02 の取得＝取り込みは1時間ほど遅れる）／brush_sales_1126_1127_1403_raw.json（Shopify・注文）／
      brush_sess_1126_1127_1403_raw.json（Shopify・ブラシのページに着いた来訪）／../../ic1126/brush/*_raw.json（過去の 注文÷クリック・粗利）／w1126.py の原価・売価
見るもの: 再開からの通算（広告費・クリック・注文・倍率）と、注文数が偶然の範囲か。日中の数字なので判定・予算の提案には使わない"""
import json, csv, io, math, os, datetime, contextlib
D = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D + '../../../..')
out = []
def P(s=''): print(s); out.append(s)
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1126.py').read(), g)
NM = '伸縮ワックス洗車ブラシ'; COST, PRICE = g['COST'][NM], g['PRICE'][NM]
def meta(f):
    raw = json.load(open(f, encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
    return [{k: (v if k in ('date', 'adcampaign_name', 'ad_name') else (0.0 if v in ('null', '') else float(v))) for k, v in zip(cols, r)} for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]
T = {r['date']: r for r in meta(D + 'brush_meta_1126_1127_1402_raw.json')}; assert set(T) == {'2026-11-26', '2026-11-27'} and all(r['ad_name'] == 'A' for r in T.values())
S = {r[0][:10]: (int(r[1]), float(r[2]) + float(r[3]) - round(float(r[2]) / PRICE) * COST, round(float(r[2]) / PRICE)) for r in json.load(open(D + 'brush_sales_1126_1127_1403_raw.json', encoding='utf-8'))['rows']}
SS = {}
for d, src, s, c, ck, dn in json.load(open(D + 'brush_sess_1126_1127_1403_raw.json', encoding='utf-8'))['rows']:
    x = SS.setdefault(d[:10], [0, 0, 0, 0, 0]); x[0] += int(s); x[1] += int(c); x[2] += int(ck); x[3] += int(dn); x[4] += int(s) if src == 'social' else 0
P('■ ① 再開からの数字（Meta は 14:02 の取得・Shopify は 14:03）')
tc = ti = tk = to = tg = 0
for d in sorted(T):
    t = T[d]; o, gp, q = S.get(d, (0, 0.0, 0)); s = SS.get(d, [0] * 5)
    c, i, k = t['cost'], t['impressions'], t['link_clicks']; tc += c; ti += i; tk += k; to += o; tg += gp
    P(f"  {d[5:]}{'（17:21〜）' if d.endswith('26') else '（0〜13時台）'}: 広告費 {c:,.0f}・表示 {i:,.0f}・クリック {k:.0f}（クリック率 {k/i:.2%}）・クリック1回 {c/k:.0f}円・CPM {c/i*1000:,.0f}・来訪（Meta）{t['landing_page_views']:.0f}・カート（Meta）{t['offsite_conversions_fb_pixel_add_to_cart']:.0f}｜Shopify: ページの来訪 {s[0]}（social {s[4]}）・カート {s[1]}・決済画面 {s[2]}・注文 {o}件・{q}個・倍率 {gp/c:.2f}")
P(f"  通算: 広告費 {tc:,.0f}・クリック {tk:.0f}（クリック率 {tk/ti:.2%}）・クリック1回 {tc/tk:.0f}円・注文 {to}件・粗利 {tg:,.0f} → 倍率 {tg/tc:.2f}・利益 {tg-tc:+,.0f}")
# ---- 過去 ----
M = {}
for r in meta('scripts/daily/ic1126/brush/brush_daily_1023_1126_raw.json'):
    x = M.setdefault(r['date'], dict(c=0, i=0, k=0, a=0)); x['c'] += r['cost']; x['i'] += r['impressions']; x['k'] += r['link_clicks']; x['a'] += r['offsite_conversions_fb_pixel_add_to_cart']
PO = {r[0][:10]: (int(r[1]), float(r[2]) + float(r[3]) - round(float(r[2]) / PRICE) * COST) for r in json.load(open('scripts/daily/ic1126/brush/brush_sales_daily_1023_1126_raw.json', encoding='utf-8'))['rows']}
def rng(a, b):
    a, b = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b); return [(a + datetime.timedelta(n)).isoformat() for n in range((b - a).days + 1)]
ple = lambda k, l: sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
P('■ ② 注文 1件 は偶然の範囲か（クリック × 過去の 注文÷クリック ＝ 見込み）')
gpo = []; rate = []; ta = sum(T[d]['offsite_conversions_fb_pixel_add_to_cart'] for d in T)
for nm, ds in (('最初の2週（10/23〜11/5）', rng('2026-10-23', '2026-11-05')), ('止める前の12日（11/6〜17）', rng('2026-11-06', '2026-11-17'))):
    kk = sum(M[d]['k'] for d in ds); cc = sum(M[d]['c'] for d in ds); ii = sum(M[d]['i'] for d in ds); oo = sum(PO[d][0] for d in ds if d in PO); gg = sum(PO[d][1] for d in ds if d in PO); e = tk * oo / kk; gpo.append(gg / oo); rate.append(oo / kk); ea = tk * sum(M[d]['a'] for d in ds) / kk
    P(f"  {nm}: クリック率 {kk/ii:.2%}・クリック1回 {cc/kk:.0f}円・注文÷クリック {oo/kk:.2%}・クリック1回の粗利 {gg/kk:.0f}円（倍率 1.25 の線 {gg/kk/1.25:.0f}円・1.5 の線 {gg/kk/1.5:.0f}円）→ {tk:.0f}クリックの見込み {e:.1f}件・{to}件以下になる確率 {ple(to, e):.0%}｜カート（Meta）の見込み {ea:.1f} → 実際 {ta:.0f}（{ta:.0f}以下 {ple(int(ta), ea):.0%}）")
s = 2 / math.sqrt(tk); P(f"  クリック1回 {tc/tk:.0f}円・クリック率 {tk/ti:.2%} は {tk:.0f}クリックだと幅 ×{math.exp(-s):.2f}〜{math.exp(s):.2f}（±2σ）＝クリック1回なら {tc/tk*math.exp(-s):.0f}〜{tc/tk*math.exp(s):.0f}円")
# ---- 今日の終わりまでに要る件数 ----
bud = 8000; end = T['2026-11-26']['cost'] + bud
P(f"■ ③ 今日（11/27）の終日までの通算: 広告費は 11/26 の {T['2026-11-26']['cost']:,.0f} ＋ 日予算 {bud:,} ＝ 約 {end:,.0f}円")
for m_ in (1.25, 1.5, 1.94):
    need = end * m_; lo, hi = need / max(gpo), need / (PRICE - COST)
    P(f"  通算の倍率 {m_}{'（過去の当たり6本の2日目までの下の端）' if m_ == 1.94 else ''}: 粗利 {need:,.0f}円 ＝ 注文 {lo:.1f}〜{hi:.1f}件（1注文の粗利 {max(gpo):,.0f}〜{PRICE-COST:,}円）→ いま {to}件・あと {max(0, math.ceil(lo) - to)}〜{max(0, math.ceil(hi) - to)}件")
spent = T['2026-11-27']['cost']; left = bud - spent; cpc = tc / tk
P(f"  今日の残り: 日予算 {bud:,} − 使った {spent:,.0f} ＝ {left:,.0f}円 → いまのクリック1回 {cpc:.0f}円なら あと {left/cpc:.0f}クリック → 見込みの注文 {left/cpc*min(rate):.1f}〜{left/cpc*max(rate):.1f}件（粗利 {left/cpc*min(rate)*min(gpo):,.0f}〜{left/cpc*max(rate)*max(gpo):,.0f}円＝残りの広告費 {left:,.0f}円との差 {left/cpc*min(rate)*min(gpo)-left:+,.0f}〜{left/cpc*max(rate)*max(gpo)-left:+,.0f}円）")
for m_, lab in ((1.25, '1.25'), (1.5, '1.5')):
    need = math.ceil(end * m_ / max(gpo)) - to; lam = (left / cpc * min(rate), left / cpc * max(rate))
    P(f"  今日のうちに通算 {lab} に届く（あと {need}件以上）確率: {1 - ple(need - 1, lam[0]):.0%}〜{1 - ple(need - 1, lam[1]):.0%}（過去の 注文÷クリック・いまのクリックの値段のままとして）")
P(f"  事故停止（基準6）は「購入0のまま {(PRICE-COST)*3:,}円」＝1件売れているので当たらない")
open(D + 'brush_h14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
