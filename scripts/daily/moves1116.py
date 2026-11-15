# -*- coding: utf-8 -*-
"""11/16 定例: 予算の基準（CLAUDE.md 2026-11-12）と動画を足す基準（2026-11-14 仮）の当てはめ。
入力: o1115/an1116_out.json（商品別の倍率・消化）、data/budget-snapshots.csv（部分スナップショットは前の値に上書きして積む）、o1115/ad_level_1026_1115.txt（広告別）"""
import csv, json, math, collections, datetime
# ---- 広告セットごとの予算の履歴（部分スナップショットを積む）と最後に変えた日 ----
SN = collections.OrderedDict()
for r in csv.DictReader(open('data/budget-snapshots.csv')):
    SN.setdefault(r['snapshot_date'], {})[(r['campaign'], r['adset'])] = int(r['daily_budget'])
state = {}; last = {}
for lab in sorted(SN):
    full = len(SN[lab]) >= 8          # 8行以上＝その時点の全体（それ未満は変わった行だけ）
    new = dict(SN[lab]) if full else {**state, **SN[lab]}
    for k in set(new) | set(state):
        if new.get(k) != state.get(k) and lab[:10] >= '2026-10-01' and state: last[k[0]] = lab[:10]
    state = new
# スナップショットの日付は「その時点の値」。日中の変更は変更した日（＝ラベルの日付）、00時台の全体スナップショットの差は前日の夜の変更
print('最後に予算を変えた日（キャンペーン単位・スナップショットのラベル）:')
for c in sorted(last, key=lambda c: last[c], reverse=True)[:20]: print(f'  {c}: {last[c]}')
OUT = {o['n']: o for o in json.load(open('scripts/daily/o1115/an1116_out.json'))}
# ---- ドア: いまの予算（11/12 に 8,000）になってからの消化 ----
AD = collections.defaultdict(dict)
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[r['campaign']][r['date']] = float(r['cost'])
for n, c, b in [('マグネットドアクッション', 'マグネットドアクッション', 9600), ('3WAY着る電気ブランケット', '3WAY着る電気ブランケット', 10000), ('W固定スマホ車載ホルダー', 'W固定スマホ車載ホルダー', 23000)]:
    print(f"\n{n} 11/15 消化: {AD[c]['2026-11-15']:,.0f} ÷ 日予算 {b:,} = {AD[c]['2026-11-15']/b:.0%} ／ 11/15 倍率 {OUT[n]['m1']:.2f}")
# ---- 動画を足す基準: 広告セットの配信の8割以上を1本の広告が使っている → その広告のクリック率を自分の過去と比べる ----
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))   # R[(camp,adset)][ (ad,date) ] = cost, imp, clk
for l in open('scripts/daily/o1115/ad_level_1026_1115.txt'):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(',')
    x = R[(c, a)][(ad, d)]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
def days(a, b):
    x = datetime.date.fromisoformat(a); out = []
    while x <= datetime.date.fromisoformat(b): out.append(x.isoformat()); x += datetime.timedelta(1)
    return out
R3, P7 = days('2026-11-13', '2026-11-15'), days('2026-11-06', '2026-11-12')
R7, P14 = days('2026-11-09', '2026-11-15'), days('2026-10-26', '2026-11-08')
active = {k for k, v in R.items() if any(d == '2026-11-15' and v[(ad, d)][0] > 100 for ad, d in v)}
print('\n動画を足す基準（直近3日 11/13〜15 ↔ 前7日 11/6〜12、直近7日 11/9〜15 ↔ 前14日 10/26〜11/8・ぶれは±2σ）')
def ctr(v, ad, ds):
    imp = sum(v[(ad, d)][1] for d in ds); clk = sum(v[(ad, d)][2] for d in ds); return imp, clk
for k in sorted(active):
    v = R[k]; ads = sorted({ad for ad, d in v})
    sp = {ad: sum(v[(ad, d)][0] for d in R3) for ad in ads}; tot = sum(sp.values())
    top = max(sp, key=sp.get); share = sp[top] / tot if tot else 0
    line = f'  {k[1]}: 直近3日の取り分 ' + '・'.join(f'{ad} {sp[ad]/tot:.0%}' for ad in ads if sp[ad]) + ' → '
    if share < 0.8: print(line + '8割未満（2本以上に配信が分かれている）＝対象外'); continue
    res = []
    for lab, a_, b_, th in (('急な落ち込み', R3, P7, 0.15), ('ゆっくり', R7, P14, 0.10)):
        i1, c1 = ctr(v, top, a_); i0, c0 = ctr(v, top, b_)
        if not i0 or c0 < 30 or not c1: res.append(f'{lab}: 前の期間が短い'); continue
        r1, r0 = c1 / i1, c0 / i0; ch = r1 / r0 - 1; band = 2 * math.sqrt(1 / c1 + 1 / c0)
        hit = ch <= -th and ch < -band
        res.append(f"{lab} {r1:.2%}（{c1}）←{r0:.2%}（{c0}）{ch:+.0%}・ぶれ±{band:.0%}{' ★当たる' if hit else ''}")
    print(line + f'{top} の: ' + ' ／ '.join(res))

# ---- 広告B（足した広告）の取り分とクリック率: 足した日〜11/15 ----
print('\n広告B の結果（足した日以降・広告別 取り分／クリック率）')
for k, since in [(('マグネットドアクッション','マグネットドアクッション'),'2026-11-13'), (('伸縮ワックス洗車ブラシ','伸縮ワックス洗車ブラシ'),'2026-11-13'),
                 (('伸縮ガラスクリーナー','伸縮ガラスクリーナー'),'2026-11-14'), (('ワイド水切りワイパー','ワイド水切りワイパー'),'2026-11-14'),
                 (('スマートノーズEMS美顔器v2','スマートノーズEMS美顔器v2'),'2026-11-15'), (('携帯電動シェーバーv2','携帯電動シェーバーv2'),'2026-11-15')]:
    v = R[k]; ds = days(since, '2026-11-15')
    for d in ds + ['計']:
        dd = ds if d == '計' else [d]
        ads = sorted({ad for ad, x in v if x in dd})
        sp = {ad: sum(v[(ad, x)][0] for x in dd) for ad in ads}; tot = sum(sp.values()) or 1
        print(f'  {k[1]} {d}: ' + '・'.join(f"{ad} {sp[ad]:,}円({sp[ad]/tot:.0%}) CTR {sum(v[(ad,x)][2] for x in dd)/max(1,sum(v[(ad,x)][1] for x in dd)):.2%}（{sum(v[(ad,x)][2] for x in dd)}/{sum(v[(ad,x)][1] for x in dd):,}）" for ad in ads))
