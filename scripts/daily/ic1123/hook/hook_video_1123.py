# -*- coding: utf-8 -*-
"""11/23 16時台「レザーフックをたくさん売るには何をしたらいい？」: フックの広告を動画ごとに並べる（どこまで見られたか・クリック率・クリック1回の値段・購入）。
入力: hook_ad_video_daily_0909_1123_raw.json（Meta・日別×広告セット。11/23 は 16時台までの日中）・hook_watchtime_*_raw.json（Meta・平均の再生秒。期間ごとに取り直した値）・
hook_sales_1118_1123_raw.json（Shopify・フックの日別）・data/daily/daily_sales.csv・daily_variant.csv（個数・売上・原価の群）。
動画の名前は product_tabs の EVENTS と data/relaunch-log.csv から（主力＝「0909」・v2/v4＝1115 (3).mp4・v5＝1118.mp4。-sub とフック２の動画名は記録なし）"""
import json, os, csv, collections, math, datetime
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D0 + '../../../../'
def table(f):
    return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
ROWS = [(r[0], r[1], r[2], [z(x) for x in r[4:]]) for r in table('hook_ad_video_daily_0909_1123_raw.json')]
# 列: cost, imp, clk, 3秒, 再生, 25%, 50%, 75%, 100%, ThruPlay(15秒か最後まで), カート, 購入
MAIN = '高見えレザーヘッドレストフック'
G = [('0909 の動画・売れた時期 9/11〜10/6', lambda d, c, a: a == MAIN and '2026-09-11' <= d <= '2026-10-06'),
     ('0909 の動画・10/7〜10/15', lambda d, c, a: a == MAIN and '2026-10-07' <= d <= '2026-10-15'),
     ('0909 の動画・10/16〜11/3', lambda d, c, a: a == MAIN and '2026-10-16' <= d <= '2026-11-03'),
     ('0909 の動画・出し直し 11/11〜12', lambda d, c, a: (a == MAIN or '1112複製' in a) and '2026-11-11' <= d <= '2026-11-12'),
     ('-sub の動画 10/14〜16', lambda d, c, a: a.endswith('-sub')),
     ('フック２の動画 11/1〜3', lambda d, c, a: a.endswith('フック２')),
     ('1115 (3).mp4（v2・v4）11/15〜16', lambda d, c, a: c.endswith('v2') or c.endswith('v4')),
     ('1118.mp4（v5）11/18〜22', lambda d, c, a: c.endswith('v5') and d <= '2026-11-22'),
     ('  うち v5 の 1〜2日目 11/18〜19', lambda d, c, a: c.endswith('v5') and d <= '2026-11-19'),
     ('  うち v5 の 3〜5日目 11/20〜22', lambda d, c, a: c.endswith('v5') and '2026-11-20' <= d <= '2026-11-22'),
     ('  v5 今日 11/23（16時台まで・日中）', lambda d, c, a: c.endswith('v5') and d == '2026-11-23')]
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
pc = lambda a, b: '%.1f%%' % (100 * a / b) if b else '—'
P('■ ① 動画ごと（Meta）: 広告費・表示｜CPM・クリック率・クリック1回｜3秒まで見た÷表示・15秒まで（ThruPlay）÷表示・最後まで÷表示・クリック÷3秒まで見た｜カート・購入・購入÷クリック')
T = {}
for name, f in G:
    v = [0] * 12
    for d, c, a, m in ROWS:
        if f(d, c, a):
            for i in range(12): v[i] += m[i]
    T[name] = v
    cost, imp, clk, s3, play, p25, p50, p75, p100, thru, atc, pur = v
    P('  %s: %s円・%s｜%s・%s・%s円｜%s・%s・%s・%s｜%d・%d・%s' % (name, f'{cost:,}', f'{imp:,}', f'{round(cost / imp * 1000):,}', '%.2f%%' % (100 * clk / imp), round(cost / clk), pc(s3, imp), pc(thru, imp), pc(p100, imp), pc(clk, s3), atc, pur, pc(pur, clk)))
P('  平均の再生秒（Meta・期間ごとに取った値）: 0909 9/11〜10/6 11秒・0909 10/14〜11/3 10秒・-sub 11秒・フック２ 8秒・0909 出し直し 8秒（主力 11/11・1112複製 11/12 とも）・1115 (3).mp4 6秒（v2・v4 とも）・1118.mp4（v5）8秒')
P('  1秒ごとの再生の残り方（video_play_curve）は Meta から値が返らなかった（全部 null）')
# クリック率の差が偶然の範囲か（2つの割合の差・正規近似）
def zdiff(a, b):
    (c1, n1), (c2, n2) = a, b; p = (c1 + c2) / (n1 + n2); se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); return (c1 / n1 - c2 / n2) / se
A = T['0909 の動画・売れた時期 9/11〜10/6']; V5 = T['1118.mp4（v5）11/18〜22']; V24 = T['1115 (3).mp4（v2・v4）11/15〜16']; RE = T['0909 の動画・出し直し 11/11〜12']
P('■ ② クリック率の差は偶然の範囲か（表示とクリックの数から）')
P('  1115 (3).mp4 %s と v5 %s: 差 %.1fσ' % (pc(V24[2], V24[1]), pc(V5[2], V5[1]), zdiff((V24[2], V24[1]), (V5[2], V5[1]))))
P('  0909 の出し直し %s と v5 %s: 差 %.1fσ' % (pc(RE[2], RE[1]), pc(V5[2], V5[1]), zdiff((RE[2], RE[1]), (V5[2], V5[1]))))
P('  0909 の売れた時期 %s と 0909 の出し直し %s: 差 %.1fσ（同じ動画）' % (pc(A[2], A[1]), pc(RE[2], RE[1]), zdiff((A[2], A[1]), (RE[2], RE[1]))))
P('  （2σ を超えると偶然では起きにくい）')
# ③ クリック1回の粗利（Shopify の売上と原価 ÷ Meta のリンククリック）
S = collections.defaultdict(lambda: [0, 0]); VG = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == MAIN: S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_variant.csv')):
    if r['name'] == MAIN: VG[r['date']][r['cost_group']] = int(r['gross'])
def gp(d):
    g, dc = S[d]
    if not g: return 0, 0
    if d >= '2026-10-07': cg = g // 3980 * 732
    else: v = VG[d]; cg = v.get('黒', 0) // 3980 * 1275 + v.get('茶灰', 0) // 3980 * 1344
    return g - abs(dc) - cg, g // 3980
DAY = collections.defaultdict(lambda: [0, 0, 0])   # cost, imp, clk（全広告セット）
for d, c, a, m in ROWS:
    for i in range(3): DAY[d][i] += m[i]
def span(a, b):
    x = datetime.date.fromisoformat(a); o = []
    while x <= datetime.date.fromisoformat(b): o.append(x.isoformat()); x += datetime.timedelta(1)
    return o
P('■ ③ クリック1回の粗利（Shopify の 売上−値引−原価 ÷ Meta のクリック）と、そこから決まる「払ってよいクリック1回の値段」')
PER = [('9/11〜10/6', '2026-09-11', '2026-10-06'), ('10/7〜10/15', '2026-10-07', '2026-10-15'), ('10/16〜11/3', '2026-10-16', '2026-11-03'), ('v5 11/18〜22', '2026-11-18', '2026-11-22'), ('全部 9/9〜11/22', '2026-09-09', '2026-11-22')]
for nm, a, b in PER:
    ds = span(a, b); g = sum(gp(d)[0] for d in ds); u = sum(gp(d)[1] for d in ds); cost = sum(DAY[d][0] for d in ds); clk = sum(DAY[d][2] for d in ds)
    v = g / clk
    P('  %s: 粗利 %s円・%d個・クリック %s → 1回 %d円｜倍率 %.2f（クリック1回 %d円）｜払ってよい値段: 倍率1.25 まで %d円・1.5 まで %d円・1.86 まで %d円' % (nm, f'{g:,}', u, f'{clk:,}', v, g / cost, round(cost / clk), v / 1.25, v / 1.5, v / 1.86))
# ④ v5 の日別（Shopify は hook_sales_1118_1123_raw.json と daily_sales.csv の両方で確かめる）
sh = {r[0]: (int(r[1]), int(r[2]), int(float(r[3])), int(float(r[4]))) for r in json.load(open(D0 + 'hook_sales_1118_1123_raw.json'))['rows']}
P('■ ④ v5 の日別: 広告費・CPM・クリック率・クリック1回｜注文・個数（Shopify）')
tc = tg = 0
for d in span('2026-11-18', '2026-11-23'):
    m = [x for x in ROWS if x[0] == d and x[1].endswith('v5')][0][3]; o, u, g, dc = sh.get(d, (0, 0, 0, 0))
    if d <= '2026-11-22': assert g == S[d][0], (d, g, S[d]); tc += m[0]; tg += gp(d)[0]
    P('  %s%s: %s円・%s・%.1f%%・%d円｜%d注文・%d個' % (d[5:], '（16時台まで）' if d == '2026-11-23' else '', f'{m[0]:,}', f'{round(m[0] / m[1] * 1000):,}', 100 * m[2] / m[1], round(m[0] / m[2]), o, u))
P('  11/18〜22: 広告費 %s・粗利 %s・倍率 %.2f。7日（11/18〜24）で 1.25 に届くには、11/23〜24 の広告費を X 円とすると 粗利 (%s＋X)×1.25 が要る' % (f'{tc:,}', f'{tg:,}', tg / tc, f'{tc:,}'))
P('  予算の日: 11/18〜19 8,000・11/20 12,000（00時台に上げた）・11/21〜 8,000（product_tabs の EVENTS）')
open(D0 + 'hook_video_1123.txt', 'w').write('\n'.join(out) + '\n')

# ⑤ 配置・性別をそろえても動画の差が残るか（0909 売れた時期・1115 (3).mp4＝v2＋v4・1118.mp4＝v5）
def agg(f, keyidx):
    o = collections.defaultdict(lambda: collections.defaultdict(lambda: [0] * 5))   # 動画 → 区分 → cost, imp, clk, 3秒, ThruPlay
    for r in table(f):
        c = r[0]; vid = '1118.mp4（v5）' if c.endswith('v5') else '1115 (3).mp4（v2・v4）' if (c.endswith('v2') or c.endswith('v4')) else '0909（9/11〜10/6）'
        k = ' '.join(r[1:1 + keyidx]); m = [z(x) for x in r[1 + keyidx:1 + keyidx + 5]]
        for i in range(5): o[vid][k][i] += m[i]
    return o
PL = agg('hook_placement_video_0911_1006_raw.json', 2); PL2 = agg('hook_placement_video_1115_1122_raw.json', 2)
GE = agg('hook_gender_video_0911_1006_raw.json', 1); GE2 = agg('hook_gender_video_1115_1122_raw.json', 1)
for src in (PL2, ):
    for k, v in src.items(): PL[k] = v
for k, v in GE2.items(): GE[k] = v
VID = ['0909（9/11〜10/6）', '1115 (3).mp4（v2・v4）', '1118.mp4（v5）']
def cell(m):
    cost, imp, clk, s3, th = m
    if imp < 100: return '—（表示 %d）' % imp
    return '表示 %s・3秒 %s・クリック率 %s・クリック÷3秒 %s（%dクリック）・CPM %s' % (f'{imp:,}', pc(s3, imp), '%.2f%%' % (100 * clk / imp), pc(clk, s3), clk, f'{round(cost / imp * 1000):,}')
P('■ ⑤ 性別・配置をそろえて並べる（3秒＝3秒まで見た÷表示）')
for k, lab in (('female', '女性'), ('male', '男性')):
    P('  ' + lab)
    for v in VID: P('    %s: %s' % (v, cell(GE[v][k])))
for k in ('facebook feed', 'facebook facebook_reels', 'instagram feed', 'instagram instagram_reels', 'instagram instagram_stories'):
    P('  ' + k)
    for v in VID: P('    %s: %s' % (v, cell(PL[v][k])))
tot = lambda d: [sum(x[i] for x in d.values()) for i in range(5)]
for v in VID:
    g = GE[v]; t = tot(g); P('  %s の表示の割合: 女性 %s・男性 %s' % (v, pc(g['female'][1], t[1]), pc(g['male'][1], t[1])))
g5 = GE['1118.mp4（v5）']; g15 = GE['1115 (3).mp4（v2・v4）']
P('  計算だけ（実測ではない）: 「v5 の 3秒まで見た割合」×「1115 (3).mp4 の クリック÷3秒」＝ 男性 %.1f%%・女性 %.1f%%' % (100 * g5['male'][3] / g5['male'][1] * g15['male'][2] / g15['male'][3], 100 * g5['female'][3] / g5['female'][1] * g15['female'][2] / g15['female'][3]))
P('  クリック1回の値段 ＝ CPM ÷ 1000 ÷ クリック率: クリック率 4.5%% なら CPM 5,200 で %d円・7,000 で %d円／5.5%% なら %d円・%d円' % (5200 / 1000 / 0.045, 7000 / 1000 / 0.045, 5200 / 1000 / 0.055, 7000 / 1000 / 0.055))
open(D0 + 'hook_video_1123.txt', 'w').write('\n'.join(out) + '\n')
