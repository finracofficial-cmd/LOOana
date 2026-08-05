#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-05 「害虫ブロッカーは購入しそうな層を刈り尽くしたのか」の検証
リーチ・頻度・CTR = Meta実測（配信指標のみ）／ 注文・売上 = Shopify実測
判別テスト:
  T1 母集団枯渇テスト  … 頻度が上がっているか（枯渇なら同じ人に再露出せざるを得ない）
  T2 リーチ調達テスト  … 同じ金額で同じ人数にリーチできているか
  T3 予算戻しテスト    … 同じ日予算だった過去週と今週のCTRを比べる（深掘り由来なら戻るはず）
  T4 学習リセットテスト … 7/19に新設した広告セット（同一素材）のCTRが本体と違うか
"""
import csv

W = list(csv.DictReader(open('data/analysis/gaichu_meta_weekly_reach.csv')))
CUM_REACH, CUM_FREQ, CUM_COST = 840806, 1.5675, 2924759   # Meta実測 2026-05-01〜08-04
ORDERS_TOTAL, GROSS_TOTAL = 1740, 12560880                # Shopify実測 2026-06-08〜08-04
REPEAT_RATE = 0.030                                        # Shopify実測 週次2〜4%

print('=' * 96)
print('T1 母集団枯渇テスト — 尽きたなら同じ人に何度も見せるしかなくなる')
print('=' * 96)
buyers = ORDERS_TOTAL * (1 - REPEAT_RATE)
print(f'3ヶ月の累積リーチ（重複除去）      {CUM_REACH:,} 人')
print(f'3ヶ月の累積頻度                    {CUM_FREQ:.2f} 回 ← 平均的な人は3ヶ月で1.6回しか見ていない')
print(f'週次頻度のレンジ                   {min(float(r["freq"]) for r in W):.2f} 〜 {max(float(r["freq"]) for r in W):.2f} 回（横ばい・上昇なし）')
print(f'購入者（重複除去・推計）            {buyers:,.0f} 人')
print(f'→ リーチした人の購入浸透率          {buyers/CUM_REACH*100:.3f} %  （見た人の {100-buyers/CUM_REACH*100:.2f}% はまだ買っていない）')
print('判定: 枯渇なら頻度は3〜5回に上がるが実測1.57。母集団は尽きていない ❌枯渇仮説')

print()
print('=' * 96)
print('T2 リーチ調達テスト — 金は同じだけ「人数」を買えているか')
print('=' * 96)
print(f"{'週':6}{'広告費':>10}{'リーチ':>10}{'1万円あたりリーチ':>18}{'CTR':>8}")
for r in W:
    c, rc = float(r['cost']), float(r['reach'])
    print(f"{r['week']:6}{c:10,.0f}{rc:10,.0f}{rc/c*10000:18,.0f}{float(r['ctr'])*100:7.2f}%")
per = [float(r['reach'])/float(r['cost'])*10000 for r in W]
print(f'→ 1万円あたりリーチは {min(per):,.0f}〜{max(per):,.0f} でほぼ一定。人数は同じだけ買えている')
print(f'→ 落ちたのはCTRだけ: {float(W[2]["ctr"])*100:.2f}% → {float(W[-1]["ctr"])*100:.2f}% ({(float(W[-1]["ctr"])/float(W[2]["ctr"])-1)*100:+.0f}%)')
print('判定: 「量」は買えていて「質」だけが落ちた ＝ 深く掘った層の質が低い ✅ランキング下降仮説')

print()
print('=' * 96)
print('T3 予算戻しテスト — 予算を戻せば質は戻るのか（決定的）')
print('=' * 96)
for lab, r in [('7月中旬 W29', W[5]), ('直近 W32', W[8])]:
    c, days = float(r['cost']), (7 if r is W[5] else 3)
    print(f'{lab:12} 日予算相当 {c/days:8,.0f}円/日   CTR {float(r["ctr"])*100:.2f}%   1万円あたりリーチ {float(r["reach"])/c*10000:,.0f}人')
a, b = W[5], W[8]
print(f'→ ほぼ同じ日予算（{float(a["cost"])/7:,.0f} vs {float(b["cost"])/3:,.0f}）なのにCTRは {(float(b["ctr"])/float(a["ctr"])-1)*100:+.0f}%')
print('判定: 予算を戻してもCTRは戻らない ＝ 予算の掘りすぎ「だけ」ではない。時間経過の劣化が実在する ✅')

print()
print('=' * 96)
print('T4 学習リセットテスト — 7/19新設の広告セット（同一素材）は蘇ったか')
print('=' * 96)
print('直近14日（7/23-8/5・Meta実測。購入数はMeta計上=参考）')
for name, cost, ctr, clicks, purch, note in [
    ('本体 / 素材A',        632786, 2.62, 6237, 209, '6月から継続'),
    ('０７１９ / 素材B',    202456, 2.67, 2330,  82, '7/19に新設した広告セット'),
    ('本体 / 素材B-コピー', 108519, 2.74, 1396,  33, '複製'),
]:
    print(f'  {name:18} CTR {ctr:.2f}%  CVR {purch/clicks*100:.2f}%  CPA {cost/purch:6,.0f}円   {note}')
print('→ 7/19に新設した「学習まっさら」の広告セットも、CTRは本体と同じ2.67%')
print('判定: 広告セットを作り直しても質は戻らない。壊れているのは学習ではなく「素材/訴求そのもの」か「市場」 ✅')

print()
print('=' * 96)
print('結論')
print('=' * 96)
print(f'・母集団は尽きていない（浸透率 {buyers/CUM_REACH*100:.2f}%・頻度1.57回）')
print('・尽きたのは「Metaが良い順に並べたときの上位」。予算6倍で6倍の人数に広げた分、下位まで掘った')
print('・ただし予算を戻してもCTRは戻らず、広告セット作り直しでも戻らない')
print('  → 残る未検証のレバーは「新しい素材/訴求」ただ一つ。ここが効けば需要は残っている、効かなければ市場側の終わり')
