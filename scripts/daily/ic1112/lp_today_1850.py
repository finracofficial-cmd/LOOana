# -*- coding: utf-8 -*-
"""11/12(木) 18:5x 「なんでこんなパフォーマンス悪いの今日」
着地ページ別（0〜17時台）に、来訪・カートに入れた・購入完了を 今日 と 11/5〜11/11の平均 で比べ、
購入完了（来訪単位）の差を「来訪の数が違う分」と「買う割合が違う分」に分ける（中点で分けるので足すと差に一致）。
入力: lp_day_0017_raw.json（来訪の多い順に220行まで）・store_0017.txt（店全体。一覧に出ない分は「その他」に入れる）。日中の数字なので判定・予算の提案には使わない。"""
import os, json, csv, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = json.load(open(D + 'lp_day_0017_raw.json'))
NAME = {'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush': '伸縮ガラスクリーナー', 'vacuum-adsorption-car-mobile-phone-folding-360-rotating-suction-cup-bracket': 'W固定スマホ車載ホルダー',
        'washable-reusable-fuzz-remover': 'ナノガラス脱毛パッド', 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use': 'ワイド水切りワイパー',
        'car-wash-cotton-thread-telescopic-wax-mop': '伸縮ワックス洗車ブラシ', 'waterproof-film-for-car-rearview-mirror': 'クリアビューレインガードフィルム',
        'silicone-magnetic-door-lock-damping-pad-for-tesla-refresh-model-protective-accessory': 'マグネットドアクッション', 'portable-small-wireless-mini-dust-blower': '4-in-1マルチクリーナー',
        'soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function': '快適マジックインソール', 'small-portable-mini-sealing-machine-heat-seal-food-hand-press-snack-plastic-bag': 'ポータブルヒートシーラー',
        'smart-uv-light-oscillating-humidifier': 'コードレスダブルミスト加湿器', 'student-children-cushion-chair-waist-support': '姿勢サポートチェア',
        'winter-sweatwear-men-plush-thick-fleece-sweatpant-lambswool-thermal-trousers-casual-pants-waterproof-windproof-warm-cotton-pants': '防風あったか裏起毛パンツ',
        'smart-toothbrush-sterilizer': 'UV歯ブラシ除菌器', 'seat-hook-chair-back-hidden-small-rear-row-fur-creative-upgrade-seat-flip-back-row-object-storage-car-bag': '高見えレザーヘッドレストフック',
        'car-seat-gap-plug-strip-storage-box': 'すき間収納シートポケット'}
GROUP = collections.OrderedDict([('新しい4本', ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション']),
                                 ('以前からの5本', ['伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '4-in-1マルチクリーナー', '快適マジックインソール']),
                                 ('今は止まっている4本', ['ポータブルヒートシーラー', 'コードレスダブルミスト加湿器', '姿勢サポートチェア', 'すき間収納シートポケット']),
                                 ('今日出した・再開した3本', ['防風あったか裏起毛パンツ', 'UV歯ブラシ除菌器', '高見えレザーヘッドレストフック'])])
T = '2026-11-12'; P7 = ['2026-11-%02d' % d for d in range(5, 12)]
V = collections.defaultdict(lambda: [0, 0, 0, 0])
for d, path, s, c, k, p in RAW['rows']:
    n = NAME.get(path.replace('/products/', ''), None)
    if n:
        for j, x in enumerate((s, c, k, p)): V[(d, n)][j] += int(x)
ST = {}
for l in open(D + 'store_0017.txt'):
    if l[0] != '#' and l.strip(): r = l.strip().split(','); ST[r[0]] = [int(x) for x in r[4:8]]
def tod(n): return V[(T, n)]
def avg(n): return [sum(V[(d, n)][j] for d in P7) / 7 for j in range(4)]
def split(t, a):   # 購入完了の差を、来訪の数の分と買う割合の分に
    rt = t[3] / t[0] if t[0] else None; ra = a[3] / a[0] if a[0] else None
    if rt is None: rt = ra
    if ra is None: ra = rt
    if rt is None: return 0.0, 0.0
    return (t[0] - a[0]) * (rt + ra) / 2, (t[0] + a[0]) / 2 * (rt - ra)
print('■ 着地ページ別（0〜17時台）: 来訪・カートに入れた割合・購入完了　今日 ／ 11/5〜11/11の平均（割合は7日の合計）')
tot_t = [0, 0, 0, 0]; tot_a = [0, 0, 0, 0]; S1 = S2 = 0
for g, ns in GROUP.items():
    gt = [0, 0, 0, 0]; ga = [0, 0, 0, 0]; g1 = g2 = 0
    for n in ns:
        t, a = tod(n), avg(n); x1, x2 = split(t, a); g1 += x1; g2 += x2
        for j in range(4): gt[j] += t[j]; ga[j] += a[j]
        f = lambda v: f"{v[0]:,.0f}来訪・{(v[1]/v[0]*100 if v[0] else 0):.1f}%・{v[3]:.1f}件"
        print(f"    {n}: {f(t)} ／ {f(a)} ｜ 購入完了の差 {t[3]-a[3]:+.1f}件（来訪の分 {x1:+.1f}・割合の分 {x2:+.1f}）")
    print(f"  【{g}】来訪 {ga[0]:,.0f} → {gt[0]:,}・購入完了 {ga[3]:.1f} → {gt[3]}件（{gt[3]-ga[3]:+.1f}件＝来訪の分 {g1:+.1f}・割合の分 {g2:+.1f}）")
    for j in range(4): tot_t[j] += gt[j]; tot_a[j] += ga[j]
    S1 += g1; S2 += g2
st_t = ST[T]; st_a = [sum(ST[d][j] for d in P7) / 7 for j in range(4)]
ot = [st_t[j] - tot_t[j] for j in range(4)]; oa = [st_a[j] - tot_a[j] for j in range(4)]; o1, o2 = split(ot, oa)
print(f"  【その他（トップページ・一覧・広告のない商品など）】来訪 {oa[0]:,.0f} → {ot[0]:,}・購入完了 {oa[3]:.1f} → {ot[3]}件（{ot[3]-oa[3]:+.1f}件）")
print(f"  店全体: 来訪 {st_a[0]:,.0f} → {st_t[0]:,}・購入完了 {st_a[3]:.1f} → {st_t[3]}件（{st_t[3]-st_a[3]:+.1f}件）")
print(f"  検算: グループの差の合計 {sum(tot_t[3:4])-sum(tot_a[3:4])+ot[3]-oa[3]:+.1f} ＝ 店全体の差 {st_t[3]-st_a[3]:+.1f}")
assert abs((tot_t[3] - tot_a[3] + ot[3] - oa[3]) - (st_t[3] - st_a[3])) < 1e-6
print('\n■ クリアビューレインガードフィルムと伸縮ワックス洗車ブラシの日別（来訪／カート／購入完了）')
for n in ('クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'ワイド水切りワイパー'):
    print(f"  {n}: " + ' ｜ '.join(f"{d[5:]} {V[(d,n)][0]}／{V[(d,n)][1]}／{V[(d,n)][3]}" for d in P7 + [T]))
