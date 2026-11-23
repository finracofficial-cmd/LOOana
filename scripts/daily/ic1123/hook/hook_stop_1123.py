# -*- coding: utf-8 -*-
"""11/23 17時台「フックは止めた方が良い？」: v5 を 1〜2日目とそれ以降に分け、続けてよい線（クリック1回の粗利 188円 → 150円）と並べる。
入力: hook_ad_video_daily_0909_1123_raw.json（Meta 日別・11/18〜22 の終日）・hook_v5_1122_1123_1707_raw.json（17:07 取得・11/23 は 17時台までの日中）・
hook_sales_1118_1123_raw.json と hook_sales_1120_1123_1707_raw.json（Shopify・フックの日別。行が無い日は 0注文）。原価 732円・売価 3,980円（product_tabs）"""
import json, os, math
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
def table(f): return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
M = {r[0]: [z(x) for x in r[4:7]] for r in table('hook_ad_video_daily_0909_1123_raw.json') if r[1].endswith('v5') and r[0] <= '2026-11-22'}   # cost, imp, clk
t = [r for r in table('hook_v5_1122_1123_1707_raw.json')]
assert z([r for r in t if r[0] == '2026-11-22'][0][2]) == M['2026-11-22'][0]
M['2026-11-23'] = [z(x) for x in [r for r in t if r[0] == '2026-11-23'][0][2:5]]
S = {}
for f in ('hook_sales_1118_1123_raw.json', 'hook_sales_1120_1123_1707_raw.json'):
    for r in json.load(open(D0 + f))['rows']: S[r[0]] = (int(r[1]), int(r[2]), int(float(r[3])), int(float(r[4])))
def gp(d):
    o, u, g, dc = S.get(d, (0, 0, 0, 0)); return g - abs(dc) - u * 732, o, u
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
def blk(nm, ds):
    c = sum(M[d][0] for d in ds); k = sum(M[d][2] for d in ds); g = sum(gp(d)[0] for d in ds); o = sum(gp(d)[1] for d in ds); u = sum(gp(d)[2] for d in ds)
    P('  %s: 広告費 %s・クリック %d（1回 %d円）｜%d注文・%d個・粗利 %s｜倍率 %.2f・利益 %s' % (nm, f'{c:,}', k, round(c / k), o, u, f'{g:,}', g / c, f'{g - c:+,}'))
    return c, k, g, o
P('■ v5 を分けて見る（11/23 は 17:07 までの日中）')
a = blk('1〜2日目 11/18〜19', ['2026-11-18', '2026-11-19'])
b = blk('3〜5日目 11/20〜22（終日）', ['2026-11-20', '2026-11-21', '2026-11-22'])
c = blk('今日 11/23（17:07 まで）', ['2026-11-23'])
d5 = blk('5日 11/18〜22（終日）', ['2026-11-18', '2026-11-19', '2026-11-20', '2026-11-21', '2026-11-22'])
P('■ 線: クリック1回の粗利 188円（9/9〜11/22・7,989クリック）→ 赤字にならない線 188円・続けてよい線（1.25）150円。v5 の3日目からは %d円（11/20〜22）・今日 %d円' % (round(b[0] / b[1]), round(c[0] / c[1])))
line = 4525   # 倍率 1.25 に要る 1注文の広告費（hook_1123.txt: v5 の 1注文の粗利 5,656円 ÷ 1.25）
gpo = d5[2] / d5[3]
P('■ 11/20〜22 の3日: 広告費 %s で %d注文。倍率 1.25 なら 1注文の広告費は %s円まで（1注文の粗利 %s円 ÷ 1.25）→ %.1f注文あるはず' % (f'{b[0]:,}', b[3], f'{round(gpo / 1.25):,}', f'{round(gpo):,}', b[0] / (gpo / 1.25)))
lam = b[0] / (gpo / 1.25); p = sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(b[3] + 1))
P('  本当は 1.25 の力があるのに %d注文以下になる確率 %.0f%%（終日3日分。注文数だけなら偶然の範囲内＝注文数では決められない）' % (b[3], 100 * p))
since = M['2026-11-22'][0] + M['2026-11-23'][0]
P('■ 最後の注文（11/21）のあと: 11/22 %s ＋ 今日 %s ＝ %s円で 0注文（参考: 新商品の事故停止の線は 購入0のまま (3,980−732)×3 ＝ 9,744円。v5 は購入があるので、この基準そのものには当たらない）' % (f'{M["2026-11-22"][0]:,}', f'{M["2026-11-23"][0]:,}', f'{since:,}'))
need = lambda x: (d5[0] + x) * 1.25 - d5[2]
P('■ 7日（11/18〜24）で 1.25 に届くには: 11/23〜24 の広告費が 16,000円なら 粗利があと %s円（1注文の粗利 %s円で %.1f注文）。これまでは 5日で %d注文・今日は 17時台まで 0' % (f'{round(need(16000)):,}', f'{round(gpo):,}', need(16000) / gpo, d5[3]))
P('■ あと2日続けたときの損得（広告費 16,000円として・計算）: 3〜5日目の倍率 %.2f のままなら %s円／クリック1回の粗利 188円・値段 %d円なら %s円／5日の倍率 %.2f のままなら %s円' % (b[2] / b[0], f'{round(16000 * (b[2] / b[0] - 1)):+,}', round(b[0] / b[1]), f'{round(16000 * (188 / (b[0] / b[1]) - 1)):+,}', d5[2] / d5[0], f'{round(16000 * (d5[2] / d5[0] - 1)):+,}'))
P('■ 直読（17:07）: キャンペーン ENABLED・広告セット 8,000円・配信中')
open(D0 + 'hook_stop_1123.txt', 'w').write('\n'.join(out) + '\n')
