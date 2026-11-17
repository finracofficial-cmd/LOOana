# -*- coding: utf-8 -*-
"""11/17(火) 21:1x 「カートの落ち込みべつにそんなおちてねーのな。まあくわしくぶんせきしてみーよ」
店全体のカート÷来訪が 6月 7.9% → 11月 5.6% に下がった分を、入口ページ（＝ほぼ広告の商品）別に分ける。
①同じ商品の中で下がったのか（中の変化）②カート率の低い商品に来訪が移ったのか（顔ぶれの変化）を、隣り合う月どうしで分けて積み上げる。
  中の変化 ＝ Σ（両方の月にある商品）後の月の来訪の割合 ×（後の月のカート率 − 前の月のカート率）。顔ぶれの変化 ＝ 全体の差 − 中の変化
  上位120行に入らない入口ページは月ごとに「その他」1つにまとめる（月の合計 − 上位の合計）
入力: cart_by_page_raw.txt（入口ページ別）・cart_rate_all_raw.json（月の合計）"""
import json, collections
D = __file__.rsplit('/', 1)[0] + '/'
NM = {'umb':'形状記憶日傘','umb2':'完全遮光UV日傘','frill':'フリル日傘','nano':'ナノガラス脱毛パッド','pest':'害虫ブロッカー','fan4':'4WAYハンディファン','W':'W固定','glass':'ガラスクリーナー','insole':'インソール','parka':'UVパーカー','cooler':'卓上クーラー','sung':'サングラス','slip':'バランスケアスリッパ','sandal':'健康サンダル','muda':'ムダ毛シェーバー','tooth':'歯ブラシ除菌器','shower':'シャワーヘッド','arm':'アームカバー','fan3':'3WAYサーキュレーター','disp':'ディスペンサー','shaver':'携帯電動シェーバー','chair':'姿勢サポートチェア','4in1':'4-in-1','fan5':'5WAYファン','hook':'ヘッドレストフック','poncho':'ポンチョ','box':'2WAYシートボックス','hat':'UVハット','sealer':'ヒートシーラー','wiper':'ワイパー','door':'ドアクッション','brush':'洗車ブラシ','mochi':'もちふわサンダル','fanold':'瞬間冷却ファン(旧)','dress':'ワンピース','film':'レインガードフィルム','recov':'リカバリーサンダル','kassa':'かっさ','humid':'加湿器','neck':'ネックマッサージャー','plate':'保温プレート','home':'トップページ'}
X = collections.defaultdict(dict)
for l in open(D + 'cart_by_page_raw.txt'):
    if l[0] == '#': continue
    m, c, s, k, p = l.strip().split(','); X[m][c] = (int(s), int(k), int(p))
TOT = {r[0][5:7]: (int(r[1]), int(r[2]), int(r[4])) for r in json.load(open(D + 'cart_rate_all_raw.json'))['month']['rows']}
MS = ['05', '06', '07', '08', '09', '10', '11']
for m in MS:
    s = TOT[m][0] - sum(v[0] for v in X[m].values()); k = TOT[m][1] - sum(v[1] for v in X[m].values()); p = TOT[m][2] - sum(v[2] for v in X[m].values())
    assert s > 0 and k >= 0; X[m]['other'] = (s, k, p)
NM['other'] = 'その他（上位に入らない入口）'
rate = lambda v: v[1] / v[0]
print('■ 月ごとの店全体のカート÷来訪と、来訪の多い入口（その月の来訪の割合・カート率）')
for m in MS:
    S = TOT[m][0]; top = sorted((c for c in X[m] if c != 'other'), key=lambda c: -X[m][c][0])[:5]
    print(f"  {m}月: {TOT[m][1]/S*100:.1f}%（来訪 {S:,}）／ " + '・'.join(f"{NM[c]} {X[m][c][0]/S*100:.0f}% {rate(X[m][c])*100:.1f}%" for c in top) + f"・その他 {X[m]['other'][0]/S*100:.0f}% {rate(X[m]['other'])*100:.1f}%")
print('■ 同じ商品の月ごとのカート÷来訪（来訪1,000以上の月だけ・2か月以上ある商品）')
for c in sorted(NM, key=lambda c: -sum(X[m].get(c, (0,))[0] for m in MS)):
    ms = [m for m in MS if X[m].get(c, (0,))[0] >= 1000]
    if len(ms) < 2 or c == 'other': continue
    print(f"  {NM[c]}: " + '・'.join(f"{m}月 {rate(X[m][c])*100:.1f}%（{X[m][c][0]:,}）" for m in ms))
print('■ 隣り合う月どうしで分ける（パーセントポイント）。中の変化＝同じ商品のカート率の変化、顔ぶれ＝来訪の行き先の変化と新しい商品・やめた商品')
cw = cm = 0
for a, b in zip(MS, MS[1:]):
    Sb = TOT[b][0]; Ra = TOT[a][1] / TOT[a][0]; Rb = TOT[b][1] / Sb
    both = [c for c in X[b] if c in X[a]]
    w = sum(X[b][c][0] / Sb * (rate(X[b][c]) - rate(X[a][c])) for c in both)
    big = sorted(both, key=lambda c: X[b][c][0] / Sb * (rate(X[b][c]) - rate(X[a][c])))
    cw += w; cm += (Rb - Ra) - w
    print(f"  {a}→{b}月: {Ra*100:.2f}% → {Rb*100:.2f}%（{(Rb-Ra)*100:+.2f}）＝ 中の変化 {w*100:+.2f} ＋ 顔ぶれ {((Rb-Ra)-w)*100:+.2f}。中の変化の大きい商品: " + '・'.join(f"{NM[c]} {X[b][c][0]/Sb*(rate(X[b][c])-rate(X[a][c]))*100:+.2f}" for c in big[:3]))
R5 = TOT['05'][1] / TOT['05'][0]; R6 = TOT['06'][1] / TOT['06'][0]; R11 = TOT['11'][1] / TOT['11'][0]
print(f"  5月→11月の合計: {R5*100:.2f}% → {R11*100:.2f}%（{(R11-R5)*100:+.2f}）＝ 中の変化 {cw*100:+.2f} ＋ 顔ぶれ {cm*100:+.2f}")
