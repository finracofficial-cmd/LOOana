# -*- coding: utf-8 -*-
"""11/28 06時台「なんで昨日の倍率は低くて利益低いの？損益分岐的なこと？効率落ちた？／クリック値段高騰は全体的に？cpmのせい？／サンバイザーは今日売れてるね？／夏のように収益を戻す秘訣」の数字。
① 11/27 の倍率を 1注文の粗利 × 注文÷クリック ÷ クリック1回の値段（＝CPM ÷ クリック率）に分けて、前7日・前30日と比べる
② 11/27 に倍率 1.0（損益分岐）を下回った商品と、上回った商品
③ CPM・クリック率・クリック1回の値段: 11/25〜27 ↔ 11/18〜24 を キャンペーン別・性別×年代別・配置別に
④ サンバイザー・ガラスクロスの今日（11/28 06:50 ごろまで・途中の数字）
⑤ 月ごとの利益/日・広告費/日・倍率と、利益 2万円/日以上の商品の本数（7/17〜11/27）
入力: w1127.py（data/daily/*.csv）・data/daily/daily_order_bands.csv・o1127/meta_acct_daily_1004_1127.txt・o1127/ad_level_1026_1127.txt・o1127/moves1128.txt・o1127/meta_ad_1127_raw.json・
      この why/ の取得（acct_agegender_daily_1114_1127・acct_placement_daily_1114_1127・meta_ad_1128_0650・sales_1128_0650・lp_new_1128_0650）"""
import io, contextlib, json, os, csv, math, collections, re
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1127.py').read(), g)
A, ALLD, agg, WIN, ACCT = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT']
out = []
def P(s=''): print(s); out.append(s)
T = '2026-11-27'; O1 = 'scripts/daily/o1127/'
def tot(days):
    k = 'x' + days[0] + days[-1]; WIN[k] = days; N, DC, Q, K = agg(days, k); return sum(N.values()), sum(K.values()), ACCT(days), N, K
ple = lambda k, l: sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
def table(f): return [l.strip().split(',') for l in json.load(open(f))['data']['data'].split('\n')[1:] if l.strip()]
ORD = {r['date']: int(r['orders']) for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
AC = {}
for l in open(O1 + 'meta_acct_daily_1004_1127.txt'):
    if l[0] == '#': continue
    r = l.strip().split(','); AC[r[0]] = (int(r[1]), int(r[2]), int(r[4]))   # 広告費・表示・リンククリック
# ---- ① ----
def parts(days):
    s, k, a, _, _ = tot(days); o = sum(ORD[d] for d in days); c = sum(AC[d][2] for d in days); i = sum(AC[d][1] for d in days); ma = sum(AC[d][0] for d in days)
    return dict(n=len(days), gp=s - k, ad=a, o=o, c=c, i=i, m=(s - k) / a, gpo=(s - k) / o, oc=o / c, cpc=a / c, cpm=ma / i * 1000, ctr=c / i)
t = parts([T]); p7 = parts(ALLD[-8:-1]); p30 = parts(ALLD[-31:-1]); assert ALLD[-8] == '2026-11-20' and ALLD[-31] == '2026-10-28'
P('■ ① 11/27 の倍率の中身（倍率 ＝ 1注文の粗利 × 注文÷クリック ÷ クリック1回の値段。クリック1回の値段 ＝ CPM ÷ クリック率）')
for lab, x in (('11/27', t), ('前7日（11/20〜26）', p7), ('前30日（10/28〜11/26）', p30)):
    P(f"  {lab}: 倍率 {x['m']:.2f}｜1注文の粗利 {x['gpo']:,.0f}円｜注文÷クリック {x['oc']:.2%}（注文 {x['o']/x['n']:.0f}/日・クリック {x['c']/x['n']:,.0f}/日）｜クリック1回 {x['cpc']:.1f}円（CPM {x['cpm']:,.0f}・クリック率 {x['ctr']:.2%}）｜利益 {(x['gp']-x['ad'])/x['n']:,.0f}/日・広告費 {x['ad']/x['n']:,.0f}/日")
for lab, b in (('前7日', p7), ('前30日', p30)):
    P(f"  11/27 ÷ {lab}: 倍率 ×{t['m']/b['m']:.2f} ＝ 1注文の粗利 ×{t['gpo']/b['gpo']:.2f} × 注文÷クリック ×{t['oc']/b['oc']:.2f} ÷ クリック1回の値段 ×{t['cpc']/b['cpc']:.2f}（CPM ×{t['cpm']/b['cpm']:.2f}・クリック率 ×{t['ctr']/b['ctr']:.2f}）")
e = t['c'] * p7['oc']; e30 = t['c'] * p30['oc']
P(f"  注文数: クリック {t['c']:,} × 前7日の 注文÷クリック ＝ 見込み {e:.1f}件 → 実際 {t['o']}件（{t['o']}件以下 {ple(t['o'], e):.0%}）｜前30日の割合なら 見込み {e30:.1f}件（{t['o']}件以下 {ple(t['o'], e30):.0%}）")
for lab, b in (('前7日', p7), ('前30日', p30)):
    ad2 = t['c'] * b['cpc']; P(f"  もし同じクリック数（{t['c']:,}）を {lab} の値段（{b['cpc']:.1f}円）で買えていたら: 広告費 {ad2:,.0f}（実際 {t['ad']:,.0f}・差 {t['ad']-ad2:+,.0f}）→ 倍率 {t['gp']/ad2:.2f}・利益 {t['gp']-ad2:,.0f}（実際 {t['gp']-t['ad']:,.0f}）")
# ---- ② ----
s, k, a, N, K = tot([T]); lo = []; hi = []
for n in sorted({x for x in set(N) | set(g['MAP']) if A([T], x)}, key=lambda x: -A([T], x)):
    gp = N.get(n, 0) - K.get(n, 0); ad = A([T], n); (lo if gp < ad else hi).append((n, gp, ad))
cat = a - sum(x[2] for x in lo + hi)
P('■ ② 11/27 の損益分岐（倍率 1.0 ＝ 粗利と広告費が同じ）')
P(f"  店全体: 粗利 {s-k:,.0f} ÷ 広告費 {a:,.0f} ＝ {(s-k)/a:.2f}（1.0 より上＝黒字 {s-k-a:,.0f}）")
P(f"  1.0 を下回った商品 {len(lo)}本: 広告費 {sum(x[2] for x in lo):,.0f}（{sum(x[2] for x in lo)/a:.0%}）・利益 {sum(x[1]-x[2] for x in lo):+,.0f} ／ " + '・'.join(f'{n} {gp/ad:.2f}' for n, gp, ad in lo))
P(f"  1.0 以上の商品 {len(hi)}本: 広告費 {sum(x[2] for x in hi):,.0f}（{sum(x[2] for x in hi)/a:.0%}）・利益 {sum(x[1]-x[2] for x in hi):+,.0f} ／ " + '・'.join(f'{n} {gp/ad:.2f}' for n, gp, ad in hi))
na = sum(N.get(n, 0) - K.get(n, 0) for n in N if not A([T], n))
P(f"  カタログの広告費 {cat:,.0f}・広告なしで売れた商品の粗利 {na:+,.0f}")
for d in ALLD[-8:-1]:
    s_, k_, a_, N_, K_ = tot([d]); l_ = [(n, N_.get(n, 0) - K_.get(n, 0), A([d], n)) for n in {x for x in set(N_) | set(g['MAP']) if A([d], x)}]; l_ = [x for x in l_ if x[1] < x[2]]
    out.append(f"    {d[5:]}: 1.0 未満 {len(l_)}本・広告費の {sum(x[2] for x in l_)/a_:.0%}・店の倍率 {(s_-k_)/a_:.2f}"); print(out[-1])
# ---- ③ ----
LATE = ('2026-11-25', '2026-11-27'); EARLY = ('2026-11-18', '2026-11-24')
def cmp_(rows, keyf, minshare=0.01):
    Ea = collections.defaultdict(lambda: [0, 0, 0]); La = collections.defaultdict(lambda: [0, 0, 0])
    for d, key, c, i, kk in rows:
        tgt = La if LATE[0] <= d <= LATE[1] else Ea if EARLY[0] <= d <= EARLY[1] else None
        if tgt is not None:
            for j, v in enumerate((c, i, kk)): tgt[key][j] += v
    lt = sum(v[0] for v in La.values()); res = []
    for key, l in sorted(La.items(), key=lambda x: -x[1][0]):
        e_ = Ea.get(key)
        if not e_ or e_[1] < 1000 or l[1] < 500 or l[0] / lt < minshare or not e_[2] or not l[2]: continue
        res.append((key, e_, l))
    return res, Ea, La
def show(title, res):
    P(title); up = sum(1 for _, e_, l in res if l[0] / l[1] > e_[0] / e_[1] * 1.05); upc = sum(1 for _, e_, l in res if l[0] / l[2] > e_[0] / e_[2] * 1.05)
    for key, e_, l in res:
        P(f"    {key}: CPM {e_[0]/e_[1]*1000:,.0f} → {l[0]/l[1]*1000:,.0f}（{l[0]/l[1]/(e_[0]/e_[1])-1:+.0%}）｜クリック率 {e_[2]/e_[1]:.2%} → {l[2]/l[1]:.2%}（{l[2]/l[1]/(e_[2]/e_[1])-1:+.0%}）｜クリック1回 {e_[0]/e_[2]:.0f} → {l[0]/l[2]:.0f}円（{l[0]/l[2]/(e_[0]/e_[2])-1:+.0%}）｜広告費/日 {e_[0]/7:,.0f} → {l[0]/3:,.0f}")
    li = sum(l[1] for _, _, l in res); P(f"    ＝ {len(res)}区分のうち CPM が 5% より大きく上がったのは {up}・クリック1回が 5% より大きく上がったのは {upc}")
    cm_e = sum(l[1] * e_[0] / e_[1] for _, e_, l in res) / li * 1000; cm_l = sum(l[0] for _, _, l in res) / li * 1000
    ct_e = sum(l[1] * e_[2] / e_[1] for _, e_, l in res) / li; ct_l = sum(l[2] for _, _, l in res) / li
    P(f"    顔ぶれをそろえた合計（11/25〜27 の表示の割合で）: CPM {cm_e:,.0f} → {cm_l:,.0f}（{cm_l/cm_e-1:+.0%}）・クリック率 {ct_e:.2%} → {ct_l:.2%}（{ct_l/ct_e-1:+.0%}）・クリック1回 {cm_e/1000/ct_e:.0f} → {cm_l/1000/ct_l:.0f}円（{(cm_l/ct_l)/(cm_e/ct_e)-1:+.0%}）")
P('■ ③ CPM・クリック率・クリック1回の値段: 11/18〜24（7日）→ 11/25〜27（3日）')
days14 = sorted(d for d in AC if d >= '2026-11-14')
P('  アカウント（日別）CPM｜クリック率｜クリック1回: ' + '・'.join(f"{d[5:]} {AC[d][0]/AC[d][1]*1000:,.0f}｜{AC[d][2]/AC[d][1]:.2%}｜{AC[d][0]/AC[d][2]:.0f}円" for d in days14))
LAST = {}
for l in open(O1 + 'moves1128.txt', encoding='utf-8'):
    m_ = re.match(r'^  (.+?): (2026-\d\d-\d\d)$', l.rstrip())
    if m_: LAST[m_.group(1)] = m_.group(2)
rows = []
for l in open(O1 + 'ad_level_1026_1127.txt', encoding='utf-8'):
    if l[0] == '#': continue
    d, c, a_, ad_, cost, imp, clk = l.strip().split(','); rows.append((d, c, int(cost), int(imp), int(clk)))
res, _, _ = cmp_(rows, None)
P('  (1) キャンペーン別（最後に予算を変えた日つき）')
up = 0
for key, e_, l in res:
    lc = next((v for kk, v in LAST.items() if kk in key or key in kk), '—')
    P(f"    {key}: CPM {e_[0]/e_[1]*1000:,.0f} → {l[0]/l[1]*1000:,.0f}（{l[0]/l[1]/(e_[0]/e_[1])-1:+.0%}）｜クリック率 {e_[2]/e_[1]:.2%} → {l[2]/l[1]:.2%}（{l[2]/l[1]/(e_[2]/e_[1])-1:+.0%}）｜クリック1回 {e_[0]/e_[2]:.0f} → {l[0]/l[2]:.0f}円（{l[0]/l[2]/(e_[0]/e_[2])-1:+.0%}）｜広告費/日 {e_[0]/7:,.0f} → {l[0]/3:,.0f}｜予算の変更 {lc[5:] if lc != '—' else '—'}")
li = sum(l[1] for _, _, l in res); cm_e = sum(l[1] * e_[0] / e_[1] for _, e_, l in res) / li * 1000; cm_l = sum(l[0] for _, _, l in res) / li * 1000; ct_e = sum(l[1] * e_[2] / e_[1] for _, e_, l in res) / li; ct_l = sum(l[2] for _, _, l in res) / li
P(f"    ＝ {len(res)}本のうち CPM が 5% より大きく上がったのは {sum(1 for _, e_, l in res if l[0]/l[1] > e_[0]/e_[1]*1.05)}本・クリック1回が 5% より大きく上がったのは {sum(1 for _, e_, l in res if l[0]/l[2] > e_[0]/e_[2]*1.05)}本｜顔ぶれをそろえた合計: CPM {cm_e:,.0f} → {cm_l:,.0f}（{cm_l/cm_e-1:+.0%}）・クリック率 {ct_e:.2%} → {ct_l:.2%}（{ct_l/ct_e-1:+.0%}）・クリック1回 {cm_e/1000/ct_e:.0f} → {cm_l/1000/ct_l:.0f}円（{(cm_l/ct_l)/(cm_e/ct_e)-1:+.0%}）")
ag = [(r[0], ('男性' if r[2] == 'male' else '女性') + ' ' + r[1], z(r[3]), z(r[4]), z(r[5])) for r in table(D0 + 'acct_agegender_daily_1114_1127_raw.json') if r[2] in ('male', 'female') and r[1] != 'Unknown']
tt = sum(x[2] for x in ag if x[0] == T); assert abs(tt - AC[T][0]) / AC[T][0] < 0.01, (tt, AC[T][0])
show('  (2) 性別×年代別', cmp_(ag, None)[0])
pl = [(r[0], r[1] + ' ' + r[2], z(r[3]), z(r[4]), z(r[5])) for r in table(D0 + 'acct_placement_daily_1114_1127_raw.json')]
tt = sum(x[2] for x in pl if x[0] == T); assert abs(tt - AC[T][0]) / AC[T][0] < 0.01, (tt, AC[T][0])
show('  (3) 配置別（広告費の 1% 以上）', cmp_(pl, None)[0])
# ---- ④ ----
P('■ ④ 新商品2本の今日（11/28 06:50 ごろの取得・途中の数字。判定は 11/29 朝に終日の数字で行う）')
M27 = table(O1 + 'meta_ad_1127_raw.json'); M28 = table(D0 + 'meta_ad_1128_0650_raw.json'); S28 = json.load(open(D0 + 'sales_1128_0650_raw.json'))['rows']; L28 = json.load(open(D0 + 'lp_new_1128_0650_raw.json'))['rows']
for nm_, hd, gp1 in (('2WAY防眩サンバイザー', 'car-day-and-night-sun-goggles', 3980 - 956), ('クリア仕上げガラスクロス', 'thickened-magic-cleaning-cloth', 3980 - 836)):
    r27 = [r for r in M27 if r[1] == nm_]; r28 = [r for r in M28 if r[1] == nm_]; assert len(r27) == 1 and len(r28) == 1
    c27, k27 = z(r27[0][4]), z(r27[0][6]); c28, i28, k28, atc28, pu28 = z(r28[0][4]), z(r28[0][5]), z(r28[0][6]), z(r28[0][8]), z(r28[0][9])
    so = [(int(r[1]), int(r[4]), int(float(r[2])) + int(float(r[3]))) for r in S28 if nm_ in r[0]]; o28, q28, n28 = (so[0] if so else (0, 0, 0))
    lp = [r for r in L28 if hd in r[0]]; ss, ca, ck, dn = (sum(int(r[i]) for r in lp) for i in (2, 3, 4, 5))
    cc = c27 + c28
    P(f"  {nm_}: 今日 広告費 {c28:,}・表示 {i28:,}・クリック {k28}（クリック1回 {c28/k28:.0f}円）・カート（Meta）{atc28}・購入（Meta）{pu28}｜Shopify 注文 {o28}件・{q28}個・売上 {n28:,}｜商品ページの来訪 {ss}・カート {ca}・決済画面 {ck}・購入まで行った来訪 {dn}")
    P(f"    出してからの通算（11/27 ＋ 今日の途中）: 広告費 {cc:,}・クリック {k27+k28}・{q28}個・粗利 {q28*gp1:,} → 倍率 {q28*gp1/cc:.2f}（途中）｜今日の終日までの広告費が 約 {c27+8000:,}円なら、1.25 ＝ {(c27+8000)*1.25/gp1:.1f}個・1.5 ＝ {(c27+8000)*1.5/gp1:.1f}個・1.94 ＝ {(c27+8000)*1.94/gp1:.1f}個")
tc = sum(z(r[4]) for r in M28); to = sum(int(r[1]) for r in S28 if r[0] and '優先配送' not in r[0] and 'VIP特典' not in r[0]); tn = sum(int(float(r[2])) + int(float(r[3])) for r in S28)
P(f"  店全体の今日（途中）: 広告費 {tc:,}・売上（値引後）{tn:,}・商品ごとの注文の合計 {to}")
# ---- ⑤ ----
P('■ ⑤ 月ごと（1日あたり）: 利益・広告費・倍率・売上÷広告費｜利益 2万円/日以上の商品（その月の合計 ÷ その月の日数）')
MON = collections.defaultdict(list)
for d in ALLD: MON[d[:7]].append(d)
for mth in sorted(MON):
    days = MON[mth]
    if mth < '2026-07': continue
    if mth == '2026-07': days = [d for d in days if d >= '2026-07-17']; mth = '2026-07（7/17〜31。ナノの色別の記録が 7/17 からのため）'
    s, k, a, N, K = tot(days); n = len(days); pr = sorted(((N.get(x, 0) - K.get(x, 0) - A(days, x)) / n, x, (N.get(x, 0) - K.get(x, 0)) / A(days, x) if A(days, x) else 0, A(days, x) / n) for x in set(N) | {y for y in g['MAP'] if A(days, y)}); pr.reverse()
    big = [x for x in pr if x[0] >= 20000]
    P(f"  {mth}（{n}日）: 利益 {(s-k-a)/n:,.0f}・広告費 {a/n:,.0f}・倍率 {(s-k)/a:.2f}・売上÷広告費 {s/a:.2f}｜2万円/日以上 {len(big)}本（合計 {sum(x[0] for x in big):,.0f}/日）: " + '・'.join(f"{x[1]} {x[0]:,.0f}（{x[2]:.2f}・広告費 {x[3]:,.0f}）" for x in big))
    P(f"      そのほかの商品の合計 {(s-k-a)/n - sum(x[0] for x in big) + (a - sum(A(days, x[1]) for x in pr))/n:,.0f}/日（カタログの広告費 {(a - sum(A(days, x[1]) for x in pr))/n:,.0f}/日は別）｜次の3本: " + '・'.join(f"{x[1]} {x[0]:,.0f}" for x in pr[len(big):len(big)+3]))
D7 = ALLD[-7:]; s, k, a, N, K = tot(D7); pr = sorted(((N.get(x, 0) - K.get(x, 0) - A(D7, x)) / 7, x, (N.get(x, 0) - K.get(x, 0)) / A(D7, x) if A(D7, x) else 0, A(D7, x) / 7) for x in set(N) | {y for y in g['MAP'] if A(D7, y)}); pr.reverse()
P(f"  直近7日（11/21〜27）: 利益 {(s-k-a)/7:,.0f}・広告費 {a/7:,.0f}・倍率 {(s-k)/a:.2f}｜上から5本: " + '・'.join(f"{x[1]} {x[0]:,.0f}（{x[2]:.2f}・広告費 {x[3]:,.0f}）" for x in pr[:5]))
open(D0 + 'why_1128.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
