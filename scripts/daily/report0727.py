# -*- coding: utf-8 -*-
import json, collections, datetime, sys
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open("final0727.py").read().split("json.dump({'rows':rows")[0])
REVF={v:k for k,v in FULL.items()}
UTIL={n:util(n) for n in BUD}

# ---- 増分MERの採否: 「直近の予算変更（=最後の1段）」を測る 曜日補正 と 全店コントロール が
#      同じ結論（<分岐 / 分岐〜目標 / ≥目標）に落ちたときだけ採用する。週次は文脈として別表示。
def adopt(n, br, tgt):
    ia = INCA.get(n,{})
    pair = [ia[k] for k in ('曜日','全店') if k in ia]
    if len(pair) < 2 or br=='' or tgt=='': return None, ia
    def zone(v): return 0 if v < br else (1 if v < tgt else 2)
    if zone(pair[0]) != zone(pair[1]): return None, ia
    return round(sum(pair)/2, 2), ia

TODAY = {'卓上冷感クーラー','ムダ毛シェーバー'}
NEXT = {'4WAY':'7/28','完全遮光・形状記憶':'7/28','接触冷感UVパーカー':'7/28','5WAY腰掛けファン':'7/28',
 '偏光・調光サングラス':'7/29','バランスケアスリッパ':'7/29','接触冷感UVアームカバー':'7/29','3WAYサーキュレーター':'7/29',
 '害虫ブロッカー':'7/30','ナノガラス脱毛パッド':'7/30','UV歯ブラシ除菌器':'7/30',
 '携帯電動シェーバー':'8/1','瞬間冷感ポンチョ':'8/1','壁掛けディスペンサー':'8/1',
 '形状記憶日傘':'なし(健全)','健康サンダル':'なし(健全)'}
PREV = {'卓上冷感クーラー':30000,'4WAY':85000,'完全遮光・形状記憶':34000,'接触冷感UVパーカー':28000}
CYCLE2 = {'壁掛けディスペンサー','UV歯ブラシ除菌器'}
NOREDEPLOY = ('転用先候補（害虫2.91/ナノ2.51/4WAY3.73）はいずれも直近の増額分の増分MERが未測定または分岐割れ。'
              '平均MERで転用益を見積もらない')

COST = {'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240}
PRICE = {'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'ムダ毛シェーバー':5980,
'携帯電動シェーバー':4980,'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980}
SINGLE_CR = {'害虫ブロッカー':'本体（70,000円）','4WAY':'4WAY（95,000円）'}

def action(n, r, concl, prop, im, ia):
    a=[]
    cur = r[24] if isinstance(r[24],int) else 0
    if prop != cur and isinstance(prop,int) and cur:
        a.append(f'【広告】{cur:,}→{prop:,}円/日')
    elif n in TODAY:
        a.append(f'【広告】{cur:,}円/日 据置')
    else:
        a.append(f'【広告】据置（次回判定 {NEXT.get(n,"—")}）')
    dr, dev = DIAG.get(n, ([],[]))
    if dr: a.append('【診断】' + '・'.join(dr) + '（' + ' / '.join(dev) + '）')
    if n in SINGLE_CR: a.append(f'【CR】{SINGLE_CR[n]}は配信CR1本のみ。予備CRを追加（既存は止めない）')
    if 'D3 LP/オファー' in dr: a.append('【LP】FV・レビュー・配送日数を見直し。優先配送の訴求位置も')
    if 'D4 CPM上昇' in dr: a.append('【配信】Advantage+全開放と配信面の偏りを確認')
    cr = r[6]
    if isinstance(cr,float) and cr > 0.33:
        p,c = PRICE.get(n), COST.get(n)
        if p and c:
            y = 1-(p-c)/(p+1000-c)
            a.append(f'【原価】原価率{cr*100:.1f}%>33%。CJに数量交渉／【価格】+1,000円で数量−{y*100:.1f}%まで許容')
    if isinstance(r[7],float) and r[7] > 0.40: a.append('【広告費率】40%超。CR・LPで手当て（率のために黒字を削らない）')
    if ia:
        has_pair = '曜日' in ia and '全店' in ia
        tail = ('（曜日・全店の2手法が一致→採用）' if im is not None
                else ('（曜日補正と全店補正で結論が割れる→判定保留）' if has_pair
                      else '（週次のみ。直近1段のP1/P2は測定条件を満たさず＝参考値）'))
        a.append('【増分MER実測】' + ' / '.join(f'{k}{v:+.2f}' for k,v in ia.items()) + tail)
    return ' ／ '.join(a)

rows2=[]; trace=[]
for r in rows:
    full = r[0]; n = REVF.get(full, full)
    if not r[19]:                                   # 広告なし商品
        r[25] = '📦広告なし'; r[26] = '広告費ゼロ。利益=売上−原価'; r[24]='—'; rows2.append(r); continue
    im, ia = adopt(n, r[20], r[21])
    r[23] = im if im is not None else ''
    upd = U['d7'].get(n,0)/7
    cur = r[24] if isinstance(r[24],int) else 0
    p = {'判定日': n in TODAY, '次回判定日': NEXT.get(n,'未設定'), '日販':upd,'利益7':r[4],'MER':r[19],
         '目標MER':r[21],'分岐':r[20],'余裕':r[22],'消化率':UTIL.get(n) or 0,'増分MER':im,
         '予算':cur,'元予算':PREV.get(n),'赤字比率':abs((r[4]/7)/cur) if cur else 0,'2巡目':n in CYCLE2,
         '転用が有利': False, '転用不可理由': NOREDEPLOY, '転用利益':0}
    path, concl, prop = flow.judge(p)
    r[25] = concl; r[26] = action(n, r, concl, prop, im, ia)
    if n=='湯上がりガーゼワンピース':
        path, concl, prop = 'S-1:7/26に停止（S2b 機会費用）済み。以後は判定対象外', '⏹ 停止済み', 0
        r[25] = concl
        r[26] = '【広告】7/26に停止済み（0円/日）。再開は8月以降の秋物枠選定とあわせて検討 ／ 停止時点の診断: D3 LP/オファー（CVR 3.0%→2.1%）'
    rows2.append(r)
    trace.append([full, round(upd,1), r[4], r[19], r[21], r[20], r[22], UTIL.get(n) or 0,
                  im if im is not None else '未測定/保留', '○' if n in TODAY else NEXT.get(n,''),
                  cur, prop, concl, path])

# ===== 全体サマリー =====
FEE = 0.0349
def blk(label, S_, C_, A_):
    P = S_-C_-A_; f = S_*FEE
    return [label, S_, C_, round(A_), round(P), round(P/S_,4), round(f), round(P-f), round((P-f)/S_,4)]
SD  = {ds: (g-dc) for ds,g,dc,*_ in DAILY}
tot = json.load(open('calc0727.json'))['tot']
s1_= SD['2026-07-26']; s3_= sum(SD[d] for d in D3); s7_= sum(SD[d] for d in D7); s30_= sum(SD.values())
c1_= sum(C['d1'].values()); c3_= sum(C['d3'].values()); c7_= sum(C['d7'].values()); c30_= sum(C['d30'].values())
CUM = json.load(open('cum.json'))
cum = [CUM['S']+s1_, CUM['C']+c1_, CUM['A']+tot['A1'], 0]
summary = [blk(f'前日(7/26 日)', s1_, c1_, tot['A1']),
           blk('3日(7/24-26)', s3_, c3_, tot['A3']),
           blk('7日(7/20-26)', s7_, c7_, tot['A7']),
           blk('30日(6/27-7/26)', s30_, c30_, tot['A30']),
           blk('📅7/18〜7/26累積(9日)', cum[0], cum[1], cum[2])]
json.dump({'S':cum[0],'C':cum[1],'A':cum[2],'P':cum[0]-cum[1]-cum[2],'f':round(cum[0]*FEE)}, open('cum.json','w'))

# ヘッドライン
sun = [SD[d] for d in SD if wd(d)=='日']
def pct(a,b): return f'{(a/b-1)*100:+.1f}%'
h = [['売上(gross−値引)', s1_, round(sum(sun)/len(sun)), round(s3_/3), round(s7_/7), round(s30_/30), pct(s1_, s7_/7)+' ✅'],
     ['原価', c1_, '', round(c3_/3), round(c7_/7), round(c30_/30), pct(c1_, c7_/7)],
     ['広告費', round(tot['A1']), '', round(tot['A3']/3), round(tot['A7']/7), round(tot['A30']/30), pct(tot['A1'], tot['A7']/7)],
     ['利益', round(s1_-c1_-tot['A1']), '', round((s3_-c3_-tot['A3'])/3), round((s7_-c7_-tot['A7'])/7),
      round((s30_-c30_-tot['A30'])/30), pct(s1_-c1_-tot['A1'], (s7_-c7_-tot['A7'])/7)],
     ['利益率', f'{(s1_-c1_-tot["A1"])/s1_*100:.1f}%', '', f'{(s3_-c3_-tot["A3"])/s3_*100:.1f}%',
      f'{(s7_-c7_-tot["A7"])/s7_*100:.1f}%', f'{(s30_-c30_-tot["A30"])/s30_*100:.1f}%',
      f'{((s1_-c1_-tot["A1"])/s1_-(s7_-c7_-tot["A7"])/s7_)*100:+.1f}pt'],
     ['手数料控除後利益', round(s1_-c1_-tot['A1']-s1_*FEE), '', round((s3_-c3_-tot['A3']-s3_*FEE)/3),
      round((s7_-c7_-tot['A7']-s7_*FEE)/7), round((s30_-c30_-tot['A30']-s30_*FEE)/30),
      pct(s1_-c1_-tot['A1']-s1_*FEE, (s7_-c7_-tot['A7']-s7_*FEE)/7)]]
CAND = '・'.join(f"{r[0][:12]}({r[19]:.2f}>{r[21]:.2f}・{UTIL.get(REVF.get(r[0],r[0]),0)*100:.0f}%)"
                 for r in rows2 if r[19] and r[21] and r[19] >= r[21] and (UTIL.get(REVF.get(r[0],r[0])) or 0) >= 0.95)
ret_mtd = sum(r for ds,g,dc,r,*_ in DAILY if ds >= '2026-07-01')
gross_mtd = sum(g for ds,g,dc,r,*_ in DAILY if ds >= '2026-07-01')
data = {'date':'2026-07-27(月) 定例（昨日=7/26 日実績）','headline':h,'summary':summary,'products':rows2,
 'flow':flow.FLOW,'trace':trace,
 'notes':[
  f'売上=gross_sales−discounts（返品A案）。当月返品累計 7/26時点 {ret_mtd:,}円（返品率{ret_mtd/gross_mtd*100:.2f}%）。7/26 新規返品ゼロ',
  '★全店の週次実測: W1(7/13-19) 売上8,840,547円・広告3,325,602円・MER2.66 → W2(7/20-26) 売上10,424,162円・広告3,919,446円・MER2.66。'
  '広告+17.9%に対し売上+17.9%＝増額分は平均と同じ効率で回収できており、全店の分岐MER1.44を大きく上回る。'
  '「増額したのに売上が伸びていない」という状態ではない（完全週どうしの比較なので曜日補正は不要）',
  '★増分MERは「最後の1段」を測る。同じ商品でも 週次（ランプ全体）と P1/P2（直近の1段）で符号が逆になる。'
  '例: 卓上冷感クーラーは週次+3.29（15k→38kのランプ全体は成功）だが、直近の30,000→38,000の1段は−9.5（失敗）。予算の増減判定に使うのはP1/P2の方',
  '★P1/P2の補正を2通りで実施し、両方が同じ結論に落ちたときだけ採用する（割れたら判定保留）。'
  '①曜日指数補正 ②全店コントロール補正＝同期間の「他商品合計」の増減で割り戻す。'
  '②を追加した理由: 7/20は海の日で7/20-23の全店実績は曜日期待値の121〜127%と大きく上振れており、曜日指数だけでは補正しきれないため',
  f'曜日指数(30日実測): ' + '・'.join(f'{k}{v:.0f}' for k,v in sorted(IDX.items(), key=lambda x:-x[1])),
  '★S2b（機会費用）の評価式を修正: 転用先の増収は転用先の「実測の増分MER」で見積もる。'
  '平均MERで見積もると既存売上の下駄を履いた過大な転用益が出る（7/25の予算提言が外れた原因と同じ誤り）',
  '★壁掛けディスペンサーは7/25に12,000→6,000円へ半減。半減後の実績(7/25-26)は売上32,900円・原価6,490円・広告8,714円＝2日で+17,696円の黒字。'
  '7日累計が赤字なのは半減前(7/20-24)の分。半減は正解だった（増分MER 曜日+0.50/全店+0.22＝削った分は元々回収できていなかった）',
  '全期間の売上・原価・広告費はShopify/Metaの実測。推計・外挿・平均の流用は不使用。'
  'ナノガラス脱毛パッド・壁掛けディスペンサーはバリエーション別の実販売数で原価を加重（30日も実測。7日構成比の流用をやめた）',
  '30日窓の途中開始: 卓上冷感クーラー7/13(14日)・5WAY腰掛けファン7/19(8日)・瞬間冷感ポンチョ/ムダ毛シェーバー7/10(17日)',
  '広告セット19/21が配信CR1本（日予算合計の約92%）。害虫ブロッカー本体(70,000円)・4WAY(95,000円)が最大の単一CR依存',
  '★増額候補（自分の目標MER超え × 消化率95%以上）: ' + CAND,
 ]}
json.dump(data, open('report_data_0727.json','w'), ensure_ascii=False, indent=1)
print('--- 全体 ---')
for r in summary: print(f'{r[0]:26s} 売上{r[1]:>11,} 原価{r[2]:>10,} 広告{r[3]:>10,} 利益{r[4]:>10,} {r[5]*100:5.1f}%')
print('\n--- 判定 ---')
for t in trace:
    mk = ' ★変更' if t[10]!=t[11] else ''
    print(f'{t[0][:24]:26s}{t[10] if isinstance(t[10],int) else 0:>8,}→{t[11] if isinstance(t[11],int) else 0:>8,} {t[12]}{mk}')
    if t[9]=='○': print(f'    経路: {t[13]}')
