# -*- coding: utf-8 -*-
"""関連商品(Shopifyレコメンド)の可視化用データを作る。

推薦データ = looty-japan.com の公開エンドポイント /recommendations/products.json 実測
             （2026-08-14 09:5x JST 取得。intent=related, limit=10）
商品成績   = daily_sales.csv / daily_ad.csv（2026-08-01〜13）＋ Shopify注文数実測
             newprod0814.py の集計をそのまま再利用する（数値の二重管理を避ける）
"""
import csv, json, io, runpy, contextlib, collections

with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path('scripts/adhoc/newprod0814.py')
PERF = {r['n']: r for r in ns['rows']}          # 商品名 -> 成績
SEASON = ns['SEASON']

SHORT = {  # Shopifyの商品タイトル(装飾込み) -> 集計で使っている短縮名
    '形状記憶日傘': '形状記憶日傘', '完全遮光・形状記憶・晴雨兼用・UV日傘': '完全遮光・形状記憶',
    '4WAY 取り付けOK 小型瞬間冷却ハンディファン': '4WAY', '3WAYサーキュレーター扇風機': '3WAYサーキュレーター',
    '壁掛けディスペンサー': '壁掛けディスペンサー',
}
def short(t):
    t = (t.replace('【本日終了⏰】【累計15万台突破🏆】', '')
          .replace('【顧客満足度No.1獲得商品🥇】【全国送料無料🚗】', '')
          .replace('LOOTY', '').replace('LOTTY', '').strip())
    return SHORT.get(t, t)

R = list(csv.DictReader(open('data/raw/recommendations_20260814.csv', encoding='utf-8')))
for r in R:
    r['rec'] = short(r['rec_title'])
    r['rank'] = int(r['rank'])
    r['price'] = int(r['rec_price']) // 100      # 公開JSONのpriceは1/100単位（498000 = 4,980円）

def stat(name):
    p = PERF.get(name)
    if not p or p['c'] <= 3000:
        return dict(roi=None, adv=False, season=name in SEASON,
                    label='広告なし' if not p or p['c'] <= 3000 else '')
    return dict(roi=round(p['roi'], 2), adv=True, season=name in SEASON, label='')

srcs = []
for s in dict.fromkeys(r['src'] for r in R):
    rs = sorted([r for r in R if r['src'] == s], key=lambda x: x['rank'])
    srcs.append(dict(name=s, **stat(s), recs=[dict(rank=r['rank'], name=r['rec'],
                                                   price=r['price'], **stat(r['rec'])) for r in rs]))
cnt_all = collections.Counter(r['rec'] for r in R)
cnt_top = collections.Counter(r['rec'] for r in R if r['rank'] <= 4)
slots = [dict(name=n, all=v, top4=cnt_top[n], **stat(n)) for n, v in cnt_all.most_common()]

out = dict(captured='2026-08-14', window='2026-08-01〜13',
           sources=srcs, slots=slots,
           n_products=len(srcs), n_rows=len(R))
json.dump(out, open('/tmp/reco_viz.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- 要約を標準出力に（数値の確認用） ---
adv = [x for x in slots if x['adv']]
print(f"{len(srcs)}商品 × 10枠 = {len(R)}枠")
print('\n上位4枠を多く取っている順（roi = 広告1円あたり利益。広告を出していない商品は None）')
for x in sorted(slots, key=lambda x: -x['top4'])[:14]:
    print(f"  {x['name']:<26}上位4枠{x['top4']:>3}回 / 全体{x['all']:>3}回  roi={x['roi']}  {'季' if x['season'] else '通'}  {x['label']}")
print('\n成績上位なのに推薦されていない商品')
for n, p in sorted(PERF.items(), key=lambda x: -(x[1]['roi'] or 0)):
    if p['c'] > 3000 and cnt_all[n] <= 4:
        print(f"  {n:<26}roi=+{p['roi']:.2f}  被推薦 全体{cnt_all[n]}回 / 上位4枠{cnt_top[n]}回")
w = sum(x['top4'] for x in slots if x['season'])
print(f"\n上位4枠 {sum(cnt_top.values())} のうち 季節商品が {w} 回 = {w/sum(cnt_top.values()):.0%}")
noad = sum(x['top4'] for x in slots if not x['adv'])
print(f"上位4枠のうち 広告を出していない商品が {noad} 回 = {noad/sum(cnt_top.values()):.0%}")
