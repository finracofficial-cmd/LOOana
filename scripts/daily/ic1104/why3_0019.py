# -*- coding: utf-8 -*-
"""11/04 0〜18時台: ドア・ナノ・クリーナーの悪化を「来訪の数（広告側）」と「来訪後の購入（ページ側）」に分ける。
過去は同じ0〜18時台（ナノ・クリーナー 10/28〜11/3の7日、ドア 11/1〜11/3の3日。10/31は途中開始のため除外）"""
import os, math, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
CID = {'マグネットドアクッション': '52581799551412', 'ナノガラス脱毛パッド': '6982162094208', '伸縮ガラスクリーナー': '52565416390612'}
M = {}; S = {}
for ln in open(D + 'meta_camp3_0018.txt'):
    if ln.startswith('#'): continue
    p = ln.strip().split(','); M[(p[1], p[0])] = [int(x) for x in p[2:]]
for ln in open(D + 'sess_camp3_0018.txt'):
    if ln.startswith('#'): continue
    p = ln.strip().split(','); S[(p[0], p[1])] = [int(x) for x in p[2:]]
T = '2026-11-04'
PAST = {'マグネットドアクッション': ['2026-11-01', '2026-11-02', '2026-11-03']}
ALL7 = ['2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31', '2026-11-01', '2026-11-02', '2026-11-03']
def agg(nm, days):
    m = [sum(M[(nm, d)][i] for d in days) for i in range(6)]; s = [sum(S[(CID[nm], d)][i] for d in days) for i in range(4)]
    return dict(cost=m[0], imp=m[1], clk=m[2], lpv=m[3], atc=m[4], pur=m[5], ses=s[0], cart=s[1], chk=s[2], done=s[3])
def met(a):
    return [('CPM', a['cost'] / a['imp'] * 1000, '{:,.0f}'), ('CTR', a['clk'] / a['imp'] * 100, '{:.2f}%'),
            ('来訪(Shopify)/広告1,000円', a['ses'] / a['cost'] * 1000, '{:.2f}'),
            ('カート率(来訪→カート)', a['cart'] / a['ses'] * 100, '{:.1f}%'),
            ('購入完了/来訪', a['done'] / a['ses'] * 100, '{:.2f}%'),
            ('カート→完了', a['done'] / a['cart'] * 100 if a['cart'] else float('nan'), '{:.0f}%'),
            ('購入完了/広告1,000円', a['done'] / a['cost'] * 1000, '{:.3f}')]
for nm in CID:
    days = PAST.get(nm, ALL7); t = agg(nm, [T]); p = agg(nm, days); n = len(days)
    print(f'\n■ {nm}（過去{n}日の0〜18時台合計 vs 今日0〜18時台）')
    print(f"  今日: 広告費{t['cost']:,}・表示{t['imp']:,}・来訪{t['ses']}・カート{t['cart']}・決済到達{t['chk']}・完了{t['done']}（Meta: LPV{t['lpv']}・カート{t['atc']}・購入{t['pur']}）")
    print(f"  過去{n}日の1日平均: 広告費{p['cost']/n:,.0f}・来訪{p['ses']/n:.0f}・カート{p['cart']/n:.1f}・完了{p['done']/n:.1f}")
    for (lab, tv, fm), (_, pv, _) in zip(met(t), met(p)):
        print(f'  {lab}: 今日 {fm.format(tv)} ／ 過去 {fm.format(pv)} （{tv/pv*100:.0f}%）')
    # 分解: 完了/1,000円 = 来訪/1,000円 × 完了/来訪
    a = math.log((t['ses'] / t['cost']) / (p['ses'] / p['cost'])); b = math.log((t['done'] / t['ses']) / (p['done'] / p['ses']))
    print(f'  分解（対数の寄与）: 来訪の取りやすさ {a/(a+b)*100:.0f}% ／ 来訪後の購入 {b/(a+b)*100:.0f}%')
    # 来訪後の購入率が過去並みなら今日の完了はいくつか（ポアソンで今日の完了数以下の確率）
    lam = t['ses'] * p['done'] / p['ses']; k = t['done']
    pk = sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
    print(f'  来訪{t["ses"]}に過去の完了率を当てると {lam:.1f}件 → 実際{k}件・この数以下になる確率 {pk*100:.1f}%')
    lamc = t['ses'] * p['cart'] / p['ses']; kc = t['cart']
    pc = sum(math.exp(-lamc) * lamc ** i / math.factorial(i) for i in range(kc + 1))
    print(f'  カートも同様: 期待 {lamc:.1f} → 実際{kc}・以下の確率 {pc*100:.1f}%')
    print('  日別 0〜18時台（来訪・カート・完了・広告費・CPM）:', [(d[5:], S[(CID[nm], d)][0], S[(CID[nm], d)][1], S[(CID[nm], d)][3], M[(nm, d)][0], round(M[(nm, d)][0] / M[(nm, d)][1] * 1000)) for d in days + [T]])

print('\n■ 店全体 0〜18時台（決済まわりに店全体の問題がないかの確認）')
R = {}
for ln in open(D + 'sess_store_0018.txt'):
    if ln.startswith('#'): continue
    p = ln.strip().split(','); R[p[0]] = [int(x) for x in p[1:]]
for d, (s, c, k, f) in R.items():
    print(f'  {d[5:]}: 来訪{s:,}・カート率{c/s*100:.1f}%・カート→完了{f/c*100:.0f}%・完了/来訪{f/s*100:.2f}%')
