"""時間帯・日による購入率（決済完了セッション÷セッション）のぶれのうち、偶然（人数の少なさ）で説明できる分を測る。
入力（Shopify 実測・11/14 18時台取得）:
  sess_hourly_1015_1113.json  … 日×時間帯 のセッション・カート・決済画面・決済完了
  sess_day_lp_1015_1113.json  … 日×入口ページ のセッション・決済完了
期間: 2026-10-15〜11-13（祝日 11/3 を除く 29日）
考え方: 買う確率が本当に一定なら、決済完了数は二項分布（≒ポアソン）でぶれる。
  φ = Σ(観測−期待)²/期待 ÷ 自由度。φ≈1 なら偶然だけで説明できる。φ>1 の分が「本当のぶれ」。
"""
import json, math, random, collections
D = 'scripts/daily/ic1114/'
HOL = {'2026-11-03'}
rows = json.load(open(D + 'sess_hourly_1015_1113.json'))['rows']
n = collections.defaultdict(int); c = collections.defaultdict(int); cart = collections.defaultdict(int); chk = collections.defaultdict(int)
for d, h, s, a, r, done in rows:
    if d in HOL: continue
    k = (d, int(h)); n[k] += int(s); c[k] += int(done); cart[k] += int(a); chk[k] += int(r)
days = sorted({k[0] for k in n}); hours = range(24)
assert len(days) == 29 and len(n) == 29 * 24

def chi2_sf(x, df):      # 上側確率（正則化不完全ガンマ）
    a, z = df / 2, x / 2
    if z <= 0: return 1.0
    if z < a + 1:
        s = t = 1 / a; k = a
        while t > s * 1e-15: k += 1; t *= z / k; s += t
        return 1 - s * math.exp(-z + a * math.log(z) - math.lgamma(a))
    b = z + 1 - a; cc = 1e300; dd = 1 / b; h = dd; i = 0
    while True:
        i += 1; an = -i * (i - a); b += 2
        dd = an * dd + b; dd = 1 / dd if dd else 1e300
        cc = b + an / cc if cc else 1e-300
        de = dd * cc; h *= de
        if abs(de - 1) < 1e-15: break
    return math.exp(-z + a * math.log(z) - math.lgamma(a)) * h

def pois_ci(mu):          # ポアソンで 2.5%〜97.5% に入る件数
    p = math.exp(-mu); cum = p; k = 0; lo = None
    while True:
        if lo is None and cum >= 0.025: lo = k
        if cum >= 0.975: return lo, k
        k += 1; p *= mu / k; cum += p

N = sum(n.values()); C = sum(c.values()); P = C / N
print(f'■ 期間 10/15〜11/13（祝日11/3除く29日）: 来訪 {N:,}・決済完了 {C:,}・購入率 {P:.2%}')

# ---- A. 日ごと ----
nd = {d: sum(n[d, h] for h in hours) for d in days}; cd = {d: sum(c[d, h] for h in hours) for d in days}
X2 = sum((cd[d] - nd[d] * P) ** 2 / (nd[d] * P * (1 - P)) for d in days); df = len(days) - 1
phi_day = X2 / df
rates = [cd[d] / nd[d] for d in days]
mean_r = sum(rates) / len(rates); sd_obs = (sum((x - mean_r) ** 2 for x in rates) / (len(rates) - 1)) ** .5
nmed = sorted(nd.values())[len(days) // 2]; sd_ch = (P * (1 - P) / nmed) ** .5
print('\n■ A. 日ごとのぶれ')
print(f'  1日の来訪 中央値 {nmed:,}・決済完了 中央値 {sorted(cd.values())[14]}')
print(f'  実際の購入率: 最低 {min(rates):.2%}（{days[rates.index(min(rates))]}）〜 最高 {max(rates):.2%}（{days[rates.index(max(rates))]}）・ばらつき(SD) ±{sd_obs/P:.0%}')
print(f'  買う確率が毎日まったく同じでも出るばらつき: ±{sd_ch/P:.0%}（来訪 {nmed:,}人のとき）')
print(f'  φ = {phi_day:.2f}（自由度{df}・偶然だけなら1）・偶然だけでこれ以上になる確率 {chi2_sf(X2, df):.3f}')
print(f'  → 日ごとのぶれ（分散）のうち 偶然で説明できる分 {min(1, 1/phi_day):.0%}・それ以外 {max(0, 1-1/phi_day):.0%}')
random.seed(1114); sims = []
for _ in range(4000):
    rs = []
    for d in days:
        mu = nd[d] * P; k = 0; t = math.exp(-mu); s = t; u = random.random()
        # ポアソン乱数（逆関数法・mu~90 なので正規近似で十分だが厳密に）
        while u > s: k += 1; t *= mu / k; s += t
        rs.append(k / nd[d])
    sims.append((min(rs), max(rs)))
sims_lo = sorted(x[0] for x in sims); sims_hi = sorted(x[1] for x in sims)
print(f'  買う確率が毎日 {P:.2%} で一定でも、29日の最低〜最高は ふつう {sims_lo[2000]:.2%}〜{sims_hi[2000]:.2%}（90%の範囲: 最低 {sims_lo[200]:.2%}〜{sims_lo[3800]:.2%}・最高 {sims_hi[200]:.2%}〜{sims_hi[3800]:.2%}）')

# 曜日
WD = '月火水木金土日'
import datetime
wn = collections.defaultdict(int); wc = collections.defaultdict(int)
for d in days:
    w = datetime.date.fromisoformat(d).weekday(); wn[w] += nd[d]; wc[w] += cd[d]
X2w = sum((wc[w] - wn[w] * P) ** 2 / (wn[w] * P * (1 - P)) for w in wn)
print('  曜日別の購入率: ' + '・'.join(f'{WD[w]} {wc[w]/wn[w]:.2%}' for w in range(7)) + f'（差が偶然で出る確率 {chi2_sf(X2w, 6):.2f}）')

# ---- B. 時間帯（29日まとめ） ----
nh = {h: sum(n[d, h] for d in days) for h in hours}; ch = {h: sum(c[d, h] for d in days) for h in hours}
X2h = sum((ch[h] - nh[h] * P) ** 2 / (nh[h] * P * (1 - P)) for h in hours)
print('\n■ B. 時間帯ごとの購入率（29日まとめ。1時間あたりの来訪は29で割った平均）')
for h in hours:
    r = ch[h] / nh[h]; se = (P * (1 - P) / nh[h]) ** .5; z = (ch[h] - nh[h] * P) / (nh[h] * P * (1 - P)) ** .5
    mark = '★高い' if z > 2 else ('▼低い' if z < -2 else '')
    print(f'  {h:2d}時台: 来訪 {nh[h]/29:5.0f}/日・決済完了 {ch[h]/29:4.1f}/日・購入率 {r:.2%}（偶然の幅 ±{2*se:.2%}） {mark}')
print(f'  時間帯で購入率に差があるか: 差が偶然で出る確率 {chi2_sf(X2h, 23):.2g}')
blocks = [('0〜5時台', range(0, 6)), ('6〜8時台', range(6, 9)), ('9〜13時台', range(9, 14)), ('14〜18時台', range(14, 19)), ('19〜23時台', range(19, 24))]
for name, hs in blocks:
    bn = sum(nh[h] for h in hs); bc = sum(ch[h] for h in hs)
    bcart = sum(cart[d, h] for d in days for h in hs); bchk = sum(chk[d, h] for d in days for h in hs)
    print(f'  {name}: 購入率 {bc/bn:.2%}・カート投入 {bcart/bn:.2%}・決済画面÷カート {bchk/bcart:.0%}・決済完了÷決済画面 {bc/bchk:.0%}・来訪 {bn/29:,.0f}/日')

# ---- C. 1時間ごと（日×時間帯のマス） ----
# 期待 = 来訪 × その日の水準 × その時間帯の水準（反復比例当てはめ）
a = {d: 1.0 for d in days}; b = {h: P for h in hours}
for _ in range(200):
    for d in days: a[d] = cd[d] / sum(n[d, h] * b[h] for h in hours)
    for h in hours: b[h] = ch[h] / sum(n[d, h] * a[d] for d in days)
E = {(d, h): n[d, h] * a[d] * b[h] for d in days for h in hours}
X2c = sum((c[k] - E[k]) ** 2 / E[k] for k in E); dfc = len(E) - (len(days) + 24 - 1)
X2c0 = sum((c[k] - n[k] * P) ** 2 / (n[k] * P) for k in E)
print('\n■ C. 1時間ごとのぶれ（29日×24時間＝696マス）')
print(f'  φ（日と時間帯の水準を除いたあと）= {X2c/dfc:.2f}（偶然だけなら1）・偶然でこれ以上になる確率 {chi2_sf(X2c, dfc):.2f}')
print(f'  参考: 何も除かない φ = {X2c0/(len(E)-1):.2f}')
out = sum(1 for k in E if not (pois_ci(E[k])[0] <= c[k] <= pois_ci(E[k])[1]))
# 偶然だけでも 95% の外に出るマスの割合（離散なので 5% ちょうどにならない）→ 期待値をそのまま計算
exp_out = 0
for k in E:
    lo, hi = pois_ci(E[k]); mu = E[k]; p = math.exp(-mu); cum = 0; inside = 0
    for j in range(hi + 1):
        if j >= lo: inside += p
        p *= mu / (j + 1)
    exp_out += 1 - inside
print(f'  「偶然では起きにくい」（95%の外）に見えるマス: 実際 {out}/{len(E)}（{out/len(E):.1%}）・偶然だけでも出る数 {exp_out:.0f}（{exp_out/len(E):.1%}）＝1日あたり約{exp_out/29:.1f}時間')
z0 = sum(1 for k in E if E[k] >= 3 and c[k] == 0); e0 = sum(math.exp(-E[k]) for k in E if E[k] >= 3)
print(f'  決済完了が3件以上見込める時間に0件だったマス: 実際 {z0}・偶然だけで出る数 {e0:.1f}')
for h0 in (8, 12, 20):
    rs = [c[d, h0] / n[d, h0] for d in days]; mu = ch[h0] / 29
    lo, hi = pois_ci(mu)
    print(f'  例 {h0}時台: 来訪 {nh[h0]/29:.0f}/日・決済完了 平均 {mu:.1f}件 → 偶然でも {lo}〜{hi}件（購入率 {lo/(nh[h0]/29):.1%}〜{hi/(nh[h0]/29):.1%}）にぶれる。実際の29日: {min(rs):.1%}〜{max(rs):.1%}')

# ---- D. 日ごとの本当のぶれは「どの商品ページに人が来たか」で説明できるか ----
lp = json.load(open(D + 'sess_day_lp_1015_1113.json'))['rows']
pn = collections.defaultdict(int); pc = collections.defaultdict(int); dn = collections.defaultdict(lambda: collections.defaultdict(int))
for d, path, s, done in lp:
    if d in HOL: continue
    pn[path] += int(s); pc[path] += int(done); dn[d][path] += int(s)
assert all(sum(dn[d].values()) == nd[d] for d in days), '日×入口ページの合計が日別の来訪と合わない'
big = {p for p in pn if pn[p] >= 1000}
rate = {p: pc[p] / pn[p] for p in big}
oth_n = sum(pn[p] for p in pn if p not in big); oth_c = sum(pc[p] for p in pn if p not in big); oth = oth_c / oth_n
Emix = {d: sum(s * rate.get(p, oth) for p, s in dn[d].items()) for d in days}
assert abs(sum(Emix.values()) - C) < 1e-6
X2m = sum((cd[d] - Emix[d]) ** 2 / (Emix[d] * (1 - P)) for d in days); phi_mix = X2m / (df - len(big))
# 自由度: ページ率をこの29日から推定したぶん（ページ数）を引く。厳しめに引いた場合と引かない場合の両方を出す
phi_mix_loose = X2m / df
print('\n■ D. 日ごとのぶれを「どの商品ページに人が来たか（入口ページの構成）」で説明できるか')
print(f'  入口ページ {len(big)}種（29日で来訪1000以上）＋その他。ページ別の購入率は29日まとめの値で固定')
print(f'  構成だけで予想した購入率の日ごとの幅: {min(Emix[d]/nd[d] for d in days):.2%}〜{max(Emix[d]/nd[d] for d in days):.2%}')
print(f'  φ: 構成を考えない {phi_day:.2f} → 構成を考える {phi_mix_loose:.2f}（ページ率の推定分の自由度を引くと {phi_mix:.2f}）')
ex0 = phi_day - 1; ex1 = max(0, phi_mix_loose - 1)
if ex0 > 0: print(f'  → 偶然を超える日ごとのぶれのうち、入口ページの構成で説明できる分 約{(ex0-ex1)/ex0:.0%}（自由度を引かない控えめな見方）')
print('  日別（実際 ／ 構成からの予想 ／ 差の偶然らしさ）:')
for d in days:
    z = (cd[d] - Emix[d]) / (Emix[d] * (1 - P)) ** .5
    print(f'    {d}（{WD[datetime.date.fromisoformat(d).weekday()]}）: {cd[d]/nd[d]:.2%} ／ {Emix[d]/nd[d]:.2%} ／ z={z:+.1f}' + ('  ←偶然では起きにくい' if abs(z) > 2 else ''))
print('  ページ別（29日まとめ・購入率）: ' + '・'.join(f'{p.split("/")[-1][:28]} {rate[p]:.1%}（{pn[p]:,}）' for p in sorted(big, key=lambda p: -pn[p])))

# ---- E. 今日（11/14）の時間帯を同じ物差しで見る ----
T = json.load(open(D + 'sess_hour_1114_1830.json'))['rows']      # 18時台は途中なので 0〜17時台だけ使う
tn = {int(r[0]): int(r[1]) for r in T}; tchk = {int(r[0]): int(r[3]) for r in T}; tc = {int(r[0]): int(r[4]) for r in T}
print('\n■ E. 今日（11/14・0〜17時台）')
for name, hs in (('0〜8時台', range(0, 9)), ('9〜17時台', range(9, 18))):
    sn = sum(tn[h] for h in hs); sc = sum(tc[h] for h in hs); sk = sum(tchk[h] for h in hs)
    past = [(sum(c[d, h] for h in hs) / sum(n[d, h] for h in hs), sum(c[d, h] for h in hs) / max(1, sum(chk[d, h] for h in hs))) for d in days]
    low_cvr = sum(1 for x in past if x[0] <= sc / sn); low_cmp = sum(1 for x in past if x[1] <= sc / sk)
    print(f'  {name}: 購入率 {sc/sn:.2%}（{sc}/{sn}）→ 29日のうち今日以下は {low_cvr}日（29日の範囲 {min(x[0] for x in past):.2%}〜{max(x[0] for x in past):.2%}）'
          f'・決済完了÷決済画面 {sc/sk:.0%}（{sc}/{sk}）→ 29日のうち今日以下は {low_cmp}日（範囲 {min(x[1] for x in past):.0%}〜{max(x[1] for x in past):.0%}）')
hr = [(h, tc[h] / tn[h]) for h in range(18)]
print('  今日の1時間ごとの購入率（6時台以降・来訪80以上）: ' + '・'.join(f'{h}時 {r:.1%}' for h, r in hr if tn[h] >= 80))

# ---- F. 本当に購入率が変わったと言えるまでに必要な日数 ----
per_day = sorted(cd.values())[14]
print('\n■ F. 購入率の変化を偶然と区別するのに必要な日数（1日の決済完了 約%d件で計算・2σ）' % per_day)
for drop in (0.05, 0.10, 0.20, 0.30):
    k = (2 / per_day ** .5 / drop) ** 2
    print(f'  {drop:.0%} の変化: {math.ceil(k)}日分' + (f'（1時間あたり約{per_day/24:.1f}件なので {math.ceil(k*24)}時間分）' if k < 1 else ''))

# ---- G. 今日の朝の不足は「朝に来た人が昼に戻って買った」で説明できるか ----
from datetime import datetime as _dt, timedelta as _td, timezone as _tz
JST = _tz(_td(hours=9))
J = json.load(open(D + 'journey_0918_1114.json'))['orders']
def jst(s): return _dt.fromisoformat(s.replace('Z', '+00:00')).astimezone(JST)
back = [o['name'] for o in J if any(jst(m['occurredAt']).date().isoformat() == '2026-11-14' and jst(m['occurredAt']).hour <= 8
                                     for m in o['customerJourneySummary']['moments']['nodes'])]
assert all(o['customerJourneySummary']['momentsCount']['count'] <= 20 for o in J)
mn = sum(tn[h] for h in range(9)); mc = sum(tc[h] for h in range(9))
mrate = sum(ch[h] for h in range(9)) / sum(nh[h] for h in range(9))
print('\n■ G. 今日の朝（0〜8時台）の不足と、朝に来て9〜17時台に買った人')
print(f'  朝の決済完了: 実際 {mc} ／ 29日の朝の購入率 {mrate:.2%} なら {mn*mrate:.1f} → 不足 約{mn*mrate-mc:.0f}')
print(f'  9〜17時台の注文 {len(J)}件のうち、今日の0〜8時台にも来ていた人: {len(back)}件（{", ".join(back)}）')
