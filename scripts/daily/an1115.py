# -*- coding: utf-8 -*-
"""11/15 定例の数値（昨日=11/14 土）。w1114.py の積み直し関数（qty/agg/A/ACCT）をそのまま使う（実測のみ）。
予算の基準（CLAUDE.md 2026-11-12）に当てはめるための 前日・前々日の倍率・3日・7日・消化（日別 広告費÷その日の最終日予算）・最後に予算を変えた日 も出す"""
import io, contextlib, statistics as st, datetime, csv, collections
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1114.py').read(), g)
WIN, agg, A, ACCT, ALLD, MAP = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD'], g['MAP']
def W(days):
    key = 'x' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
def tot(days):
    N, Q, K = W(days); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s, k, a, s - k - a
T = '2026-11-14'
for d in ['2026-11-12', '2026-11-13', T]:
    s, k, a, p = tot([d]); print(f'{d}: 実売{s:,} 原価{k:,} 広告{a:,.0f} 利益{p:,.0f}（{p/s:.1%}）MER{s/a:.2f} 倍率{(s-k)/a:.2f}')
last15 = ALLD[-15:]; P = {d: tot([d])[3] for d in last15}
print('利益 15日順位', sorted(last15, key=lambda d: -P[d]).index(T) + 1, '/15', {d[5:]: round(P[d]) for d in last15})
fri = [d for d in ALLD if datetime.date.fromisoformat(d).weekday() == 5 and '2026-09-19' <= d <= '2026-11-07' and d not in g['HOL']]
fs = [tot([d])[0] for d in fri]; s4 = tot([T])[0]; s28 = tot(['2026-11-07'])[0]
print('祝日でない土曜', [d[5:] for d in fri], f'平均実売{st.mean(fs):,.0f}・前週土{s28:,}', f'→ 11/14 {s4/st.mean(fs)-1:+.1%} ／ {s4/s28-1:+.1%}')
fp = [tot([d])[3] for d in fri]; print('祝日でない土曜 利益平均', round(st.mean(fp)), [round(x) for x in fp])
m3 = [round(tot([d])[3]) for d in ALLD[-3:]]; print('3日平均の利益', round(st.mean(m3)), m3)
p7 = tot(ALLD[-7:]); pp7 = tot(ALLD[-14:-7]); print(f'7日利益 {p7[3]:,.0f}（{p7[3]/p7[0]:.1%}・{p7[3]/7:,.0f}/日）前7日 {pp7[3]:,.0f}（{pp7[3]/7:,.0f}/日）')
cum = [d for d in ALLD if d >= '2026-11-01']; c = tot(cum); print(f'11月累計利益 {c[3]:,.0f}（{len(cum)}日・{c[3]/len(cum):,.0f}/日）')
for lab, days in [('7日', ALLD[-7:]), ('14日', ALLD[-14:]), ('30日', ALLD[-30:])]:
    t = tot(days); print(f'{lab}: 利益 {t[3]:,.0f}（{t[3]/len(days):,.0f}/日・{t[3]/t[0]:.1%}）売上÷広告費 {t[0]/t[2]:.2f} 倍率 {(t[0]-t[1])/t[2]:.2f} 広告費/日 {t[2]/len(days):,.0f}')
# ---- 予算: 日別の最終日予算（D の最終 = スナップショット D+1 の 00〜01時台 Meta直読）と最後に変えた日 ----
SN = collections.defaultdict(dict)
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
labs = sorted(SN)
nxt = lambda d: (datetime.date.fromisoformat(d) + datetime.timedelta(1)).isoformat()
BCAMP = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー'}   # 予算の記録は元の商品名で持っている
def bud(camp, d):
    camp = BCAMP.get(camp, camp)
    s = SN.get(nxt(d)); assert s, ('スナップショットなし', nxt(d)); return sum(v for (c, a), v in s.items() if c == camp)
lastchg = {}
prev = None
for l in labs:
    cur = SN[l]
    if prev is not None:
        for k in set(cur) | set(prev):
            if cur.get(k) != prev.get(k): lastchg[k[0]] = l[:10]
    prev = cur
print('\n商品: 11/14 個数・倍率・利益（広告） ／ 11/13 倍率 ／ ★=2日続けて1.25未満 ／ 3日 ／ 7日 倍率・利益 ／ 消化（11/12・11/13・11/14） ／ 最後に予算を変えた日')
D1, D0, D3, D7 = [T], ['2026-11-13'], ALLD[-3:], ALLD[-7:]
X = {k: W(v) for k, v in [('d1', D1), ('d0', D0), ('d3', D3), ('d7', D7)]}
names = set(X['d7'][0]) | {n for n, c in MAP.items() if A(D7, n)}
def mm(k, days, n):
    N, Q, K = X[k]; a = A(days, n); s = N.get(n, 0); kk = K.get(n, 0)
    return (None if not a else (s - kk) / a), s - kk - a, Q.get(n, 0), a
OUT = []
for n in sorted(names, key=lambda n: -A(D7, n)):
    if not A(D1, n) and not A(D7, n): continue
    camp = MAP.get(n, n)
    m1, p1, q1, a1 = mm('d1', D1, n); m0, *_ = mm('d0', D0, n); m3_, p3, *_ = mm('d3', D3, n); m7, p7_, *_ = mm('d7', D7, n)
    f = lambda v: '—' if v is None else f'{v:.2f}'
    flag = '★' if (m1 is not None and m0 is not None and m1 < 1.25 and m0 < 1.25) else ''
    cons = [A([d], n) / bud(camp, d) * 100 if bud(camp, d) else None for d in ALLD[-3:]]
    cs = '/'.join('—' if x is None else f'{x:.0f}' for x in cons)
    ch = lastchg.get(BCAMP.get(camp, camp), '—')
    print(f"  {n}: {q1}個・{f(m1)}・{p1:+,.0f}（広告{a1:,.0f}） ／ {f(m0)} ／ {flag} ／ 3日{f(m3_)} ／ 7日{f(m7)}・{p7_:+,.0f} ／ 消化{cs}% ／ 予算{bud(camp, T):,}・変更{ch}")
    OUT.append(dict(n=n, q1=q1, m1=m1, p1=p1, a1=a1, m0=m0, m3=m3_, m7=m7, p7=p7_, cons=cons, bud=bud(camp, T), chg=ch))
print('カタログ 11/14', g['CAT'](D1), '7日', g['CAT'](D7))
# 柱の本数（7日平均の利益が2万円/日以上の商品）
pill = [(o['n'], o['p7'] / 7) for o in OUT if o['p7'] / 7 >= 20000]
print('柱（7日平均 利益2万円/日以上）', len(pill), [(n, round(v)) for n, v in pill])
import json; json.dump(OUT, open('scripts/daily/o1114/an1115_out.json', 'w'), ensure_ascii=False, indent=1, default=str)

# 出して10日以内の商品（基準3-A）: 出した日からの通算の倍率と、前日の消化
for n, start in [('防風あったか裏起毛パンツ', '2026-11-11'), ('3WAY着る電気ブランケット', '2026-11-13'), ('スマートノーズEMS美顔器', '2026-11-14'), ('携帯電動シェーバー', '2026-11-14')]:
    days = [d for d in ALLD if d >= start]; N, Q, K = W(days); a = A(days, n); s_ = N.get(n, 0); k_ = K.get(n, 0)
    print(f'  {n}（{start}〜・{len(days)}日）: 通算 個数{Q.get(n,0)}・売上{s_:,}・原価{k_:,}・広告{a:,.0f}・倍率{(s_-k_)/a if a else 0:.2f}・利益{s_-k_-a:+,.0f}')
