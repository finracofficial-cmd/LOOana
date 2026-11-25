# -*- coding: utf-8 -*-
"""11/26 の答え合わせ（CLAUDE.md「予算を動かす基準」で 11/12 に約束した分）。対象は 11/13〜11/25。
① 動かした回数と幅（data/budget-snapshots.csv。途中の記録は変わった行だけなので、状態を積んでから差を取る）。11/4〜11/12（pace_1515: 90回・金額の変更 63回・うち2割超 28回）と並べる
② 動かしたあとの成績: 変更の前3日 → 後3日（11/23 の変更は後2日。変更当日は除く・前後とも広告費 3,000円/日以上の商品だけ）。上げ／下げ／上げた直後の戻し に分け、上げは直前7日の倍率（1.86以上／1.5〜1.86／1.5未満）でも分ける
   ※ 前後を並べただけ。良い日のあとに上げ、悪い日のあとに下げるので、何もしなくても「上げたあとは下がり、下げたあとは戻る」向きに出やすい。原因の証明ではない（pace_1515 と同じ注意）
③ 店の1日あたりの利益: 11/13〜11/25 ↔ 10/30〜11/12
数字は data/daily の CSV と budget-snapshots.csv から毎回積み直す（w1125.py の関数を使う）。「一覧にない変更」の件数は data/decisions.md に書いた印からの数えで、このスクリプトでは数えない"""
import io, contextlib, csv, collections, datetime, statistics as st, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1125.py').read(), g)
WIN, agg, A, ACCT, ALLD, MAP, MULTI, S = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD'], g['MAP'], g['MULTI'], g['S']
out = []
def P(s=''): print(s); out.append(s)
dn = lambda d, n: (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()
# ---- 予算の記録を積む ----
SN = collections.OrderedDict()
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN.setdefault(r['snapshot_date'], {})[(r['campaign'], r['adset'])] = int(r['daily_budget'])
labs = sorted(SN, key=lambda k: (k[:10], k[10:]))
state = {}; EV = []; END = {}      # EV: (ラベル, キャンペーン, 広告セット, 前, 後)
for lab in labs:
    new = dict(SN[lab]) if len(SN[lab]) >= 8 else {**state, **SN[lab]}
    if state:
        for k in set(new) | set(state):
            x, y = state.get(k, 0) or 0, new.get(k, 0) or 0
            if x != y: EV.append((lab, k[0], k[1], x, y))
    state = new; END[lab[:10]] = dict(state)
def count(a, b, lab):
    ev = [e for e in EV if a <= e[0][:10] <= b]; chg = [e for e in ev if e[3] and e[4]]; on = [e for e in ev if not e[3]]; off = [e for e in ev if not e[4]]
    big = [e for e in chg if abs(e[4] / e[3] - 1) > 0.2001]; nd = (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1
    up = [e for e in chg if e[4] > e[3]]; dw = [e for e in chg if e[4] < e[3]]
    P(f"  {lab}（{nd}日）: 合計 {len(ev)}回（1日 {len(ev)/nd:.1f}回）＝ 金額の変更 {len(chg)}回（上げ {len(up)}・下げ {len(dw)}）・開始/再開 {len(on)}回・停止 {len(off)}回｜金額の変更のうち2割を超えたもの {len(big)}/{len(chg)}回（上げ {sum(e in big for e in up)}・下げ {sum(e in big for e in dw)}）")
    return ev
P('■ ① 動かした回数（予算の記録から。広告セット単位）')
count('2026-11-04', '2026-11-12', '11/4〜11/12'); ev = count('2026-11-13', '2026-11-25', '11/13〜11/25')
byd = collections.Counter(e[0][:10] for e in ev); P('    日ごと: ' + '・'.join(f"{d[5:]} {byd.get(d, 0)}" for d in [dn('2026-11-13', i) for i in range(13)]))
byc = collections.defaultdict(list)
for e in ev: byc[e[1]].append(e)
rep = 0
for c, es in byc.items():
    ch = sorted({e[0][:10] for e in es if e[3] and e[4]}); dd = [datetime.date.fromisoformat(d) for d in ch]
    if any((q - p).days == 1 for p, q in zip(dd, dd[1:])): rep += 1
P(f"    金額を2日続けて動かしたことがある商品: {rep}/{len(byc)}（上げた翌日の戻し＝基準 4-2 を含む）")
# ---- ② 前後 ----
inv = {}
for n in S: inv[n] = n
for n, c in MAP.items(): inv[c] = n
for n, cs in MULTI.items():
    for c in cs: inv[c] = n
days = [d for d in ALLD if d >= '2026-10-25']; SER = collections.defaultdict(dict)
for d in days:
    WIN['r' + d] = [d]; N, DC, Q, K = agg([d], 'r' + d)
    for n in set(N) | set(MULTI) | set(MAP): SER[n][d] = (N.get(n, 0) - K.get(n, 0), A([d], n))
CB = {}
for d, stt in END.items():
    c = collections.Counter()
    for (cp, a_), v in stt.items(): c[inv.get(cp, cp)] += v
    CB[d] = c
LAST = '2026-11-25'; rows = []
for d in [dn('2026-11-13', i) for i in range(13)]:
    p = dn(d, -1)
    if p not in CB or d not in CB: continue
    for n in set(CB[d]) | set(CB[p]):
        x, y = CB[p].get(n, 0), CB[d].get(n, 0)
        if not x or not y or x == y or n not in SER: continue
        bf = [dn(d, -i) for i in (3, 2, 1)]; af = [z for z in (dn(d, i) for i in (1, 2, 3)) if z <= LAST]
        ok = len(af) >= 2 and all(z in SER[n] and SER[n][z][1] >= 3000 for z in bf + af)
        w7 = [dn(d, -i) for i in range(7, 0, -1)]; g7 = sum(SER[n].get(z, (0, 0))[0] for z in w7); a7 = sum(SER[n].get(z, (0, 0))[1] for z in w7)
        prev_up = any(CB.get(dn(d, -k), {}).get(n, 0) > CB.get(dn(d, -k - 1), {}).get(n, 0) > 0 for k in (1, 2))
        r = dict(d=d, n=n, x=x, y=y, r=y / x - 1, ok=ok, naf=len(af), m7=(g7 / a7 if a7 else None), p7=(g7 - a7) / 7, revert=(y < x and prev_up))
        if ok:
            f = lambda zs: (sum(SER[n][z][0] for z in zs), sum(SER[n][z][1] for z in zs)); (g1, a1), (g2, a2) = f(bf), f(af)
            r.update(m1=g1 / a1, m2=g2 / a2, p1=(g1 - a1) / 3, p2=(g2 - a2) / len(af), a1=a1 / 3, a2=a2 / len(af))
        rows.append(r)
P(f"■ ② 11/13〜11/25 の金額の変更（商品単位・その日の最後の記録どうしの差）{len(rows)}件。前3日 → 後3日（11/23 の変更は後2日・11/24 以降の変更は後がまだ無い）")
for r in sorted(rows, key=lambda r: (r['d'], r['n'])):
    kind = '戻し' if r['revert'] else ('上げ' if r['r'] > 0 else '下げ'); m7 = '—' if r['m7'] is None else f"{r['m7']:.2f}"
    tail = f"倍率 {r['m1']:.2f} → {r['m2']:.2f}・利益/日 {r['p1']:+,.0f} → {r['p2']:+,.0f}・広告費/日 {r['a1']:,.0f} → {r['a2']:,.0f}" if r['ok'] else ('後の日数がまだ足りない' if r['naf'] < 2 else '前後に広告費 3,000円未満の日がある')
    P(f"  {r['d'][5:]} {r['n']}: {r['x']:,} → {r['y']:,}（{r['r']:+.0%}・{kind}・直前7日の倍率 {m7}）｜{tail}")
def summ(lab, f):
    L = [r for r in rows if r['ok'] and f(r)]
    if not L: P(f"  {lab}: 0件"); return
    P(f"  {lab}: {len(L)}件・利益/日が増えた {sum(r['p2'] > r['p1'] for r in L)}件・倍率が上がった {sum(r['m2'] > r['m1'] for r in L)}件｜利益/日の合計 {sum(r['p1'] for r in L):+,.0f} → {sum(r['p2'] for r in L):+,.0f}・広告費/日の合計 {sum(r['a1'] for r in L):,.0f} → {sum(r['a2'] for r in L):,.0f}・後の倍率が 1.25 以上 {sum(r['m2'] >= 1.25 for r in L)}件・後の利益/日が直前7日の利益/日 以上 {sum(r['p2'] >= r['p7'] for r in L)}件（直前7日の利益/日の合計 {sum(r['p7'] for r in L):+,.0f}）")
P('  ─ まとめ（前後とも数字がそろった件だけ）')
summ('上げ（全部）', lambda r: r['r'] > 0)
summ('　上げ・直前7日の倍率 1.86 以上', lambda r: r['r'] > 0 and r['m7'] is not None and r['m7'] >= 1.86)
summ('　上げ・直前7日の倍率 1.5〜1.86', lambda r: r['r'] > 0 and r['m7'] is not None and 1.5 <= r['m7'] < 1.86)
summ('　上げ・直前7日の倍率 1.5 未満', lambda r: r['r'] > 0 and r['m7'] is not None and r['m7'] < 1.5)
summ('　上げ・2割まで', lambda r: 0 < r['r'] <= 0.2001); summ('　上げ・2割超', lambda r: r['r'] > 0.2001)
summ('戻し（上げた直後 1〜2日で下げた）', lambda r: r['revert'])
summ('下げ（戻し以外・全部）', lambda r: r['r'] < 0 and not r['revert'])
summ('　下げ・2割まで', lambda r: -0.2001 <= r['r'] < 0 and not r['revert']); summ('　下げ・2割超', lambda r: r['r'] < -0.2001 and not r['revert'])
P('  （10/20〜11/8 の45件: 2割までの下げ 18件中12件で利益増・2割超の下げ 12件中4件・上げ 15件のうち出して10日以内 5件中3件／それ以降 10件中1件＝pace_1515・ramp_1535）')
# ---- ③ 店の利益 ----
def tot(a, b):
    ds = [d for d in ALLD if a <= d <= b]; WIN['t' + a + b] = ds; N, DC, Q, K = agg(ds, 't' + a + b); s = sum(N.values()); k = sum(K.values()); ad = ACCT(ds)
    per = []
    for d in ds:
        WIN['u' + d] = [d]; n1, _, _, k1 = agg([d], 'u' + d); per.append(sum(n1.values()) - sum(k1.values()) - ACCT([d]))
    return len(ds), s, k, ad, per
P('■ ③ 店の1日あたりの利益（決済手数料を引く前）')
for lab, a, b in (('10/30〜11/12', '2026-10-30', '2026-11-12'), ('11/13〜11/25', '2026-11-13', '2026-11-25'), ('　うち 11/13〜11/19', '2026-11-13', '2026-11-19'), ('　うち 11/20〜11/25', '2026-11-20', '2026-11-25')):
    n, s, k, ad, per = tot(a, b)
    P(f"  {lab}（{n}日）: 利益 {(s-k-ad)/n:,.0f}円/日（日ごとの中央値 {st.median(per):,.0f}・最小 {min(per):,.0f}・最大 {max(per):,.0f}）・倍率 {(s-k)/ad:.2f}・売上÷広告費 {s/ad:.2f}・広告費 {ad/n:,.0f}円/日・利益率 {(s-k-ad)/s:.1%}")
n1, s1, k1, a1, p1 = tot('2026-10-30', '2026-11-12'); n2, s2, k2, a2, p2 = tot('2026-11-13', '2026-11-25')
m1, m2 = (s1 - k1) / a1, (s2 - k2) / a2; d = (s2 - k2 - a2) / n2 - (s1 - k1 - a1) / n1
P(f"  差 {d:+,.0f}円/日 ＝ 倍率の分 {(m2 - m1) * a2 / n2:+,.0f}（{m1:.2f} → {m2:.2f}）＋ 量の分 {(m1 - 1) * (a2 / n2 - a1 / n1):+,.0f}（広告費/日 {a1/n1:,.0f} → {a2/n2:,.0f}）")
se = lambda p: st.stdev(p) / len(p) ** 0.5
P(f"  日ごとのぶれから見た平均の幅（±2×標準誤差）: 10/30〜11/12 ±{2*se(p1):,.0f}・11/13〜11/25 ±{2*se(p2):,.0f} → 差 {d:+,.0f} は {'幅の外' if abs(d) > 2 * (se(p1)**2 + se(p2)**2) ** 0.5 else '幅の中'}（差の幅 ±{2 * (se(p1)**2 + se(p2)**2) ** 0.5:,.0f}）")
open('scripts/daily/o1125/review_1126.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
