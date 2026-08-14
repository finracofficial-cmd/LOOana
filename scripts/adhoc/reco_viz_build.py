# -*- coding: utf-8 -*-
"""/tmp/reco_viz.json から可視化ページ(HTML)を書き出す。数値の手打ちをしない。"""
import json, html

D = json.load(open('/tmp/reco_viz.json', encoding='utf-8'))
SRC, SLOT = D['sources'], D['slots']
OUT = ('/tmp/claude-0/-home-user-LOOana/42be2ed9-9967-56df-ab9c-75166f45bbc9/'
       'scratchpad/looty-reco.html')

def band(x):
    """広告1円あたり利益 → 等級。広告を出していない商品は測れないので none。"""
    if not x['adv'] or x['roi'] is None: return 'none'
    r = x['roi']
    if r < 0:    return 'neg'
    if r < 0.25: return 'low'
    if r < 0.60: return 'mid'
    return 'high'

BAND_JA = {'high': '広告1円あたり +0.60円以上', 'mid': '+0.25〜0.59円',
           'low': '+0.25円未満', 'neg': '赤字', 'none': '広告を出していない（測れない）'}
def val(x):  return '—' if band(x) == 'none' else f"{x['roi']:+.2f}"
def esc(s):  return html.escape(str(s))

# ── 見出しに出す3つの数字（すべてデータから計算する） ──────────────────
top4_total = sum(s['top4'] for s in SLOT)
seas4  = sum(s['top4'] for s in SLOT if s['season'])
noad4  = sum(s['top4'] for s in SLOT if not s['adv'])
winners = [s for s in SRC if band(s) == 'high']
win_names = {s['name'] for s in winners}
slot_by = {s['name']: s for s in SLOT}
win_top4 = sum(slot_by.get(n, {}).get('top4', 0) for n in win_names)

TAG = '<span class="tag">季節</span>'
rows = []
for s in SRC:
    cells = ''.join(
        f'<td class="cell b-{band(r)}" title="{esc(s["name"])} のページ 第{r["rank"]}枠 → '
        f'{esc(r["name"])}（{r["price"]:,}円 / {BAND_JA[band(r)]}）">'
        f'<span class="cn">{esc(r["name"])}</span><span class="cv">{val(r)}</span></td>'
        for r in s['recs'][:4])
    rows.append(
        f'<tr><th scope="row"><span class="sn">{esc(s["name"])}</span>'
        f'<span class="sv b-{band(s)}">{val(s)}</span>'
        f'{TAG if s["season"] else ""}</th>{cells}</tr>')

mx = max(s['top4'] for s in SLOT) or 1
bars = ''.join(
    f'<li><span class="bn">{esc(s["name"])}</span>'
    f'<span class="bt"><span class="bar b-{band(s)}" style="width:{s["top4"]/mx*100:.1f}%"></span></span>'
    f'<span class="bc">{s["top4"]}</span><span class="br b-{band(s)}">{val(s)}</span></li>'
    for s in SLOT if s['top4'] > 0)

lost = ''.join(
    f'<li><span class="ln">{esc(s["name"])}</span>'
    f'<span class="lv b-high">{val(s)}</span>'
    f'<span class="lc">上位4枠 {slot_by.get(s["name"],{}).get("top4",0)} 回</span></li>'
    for s in sorted(winners, key=lambda x: -x['roi']))

legend = ''.join(f'<span class="lg"><i class="b-{k}"></i>{BAND_JA[k]}</span>'
                 for k in ['high', 'mid', 'low', 'neg', 'none'])

HTML = f'''<title>関連商品の枠を誰が取っているか</title>
<style>
:root{{
  --ground:#F6F7F8; --surface:#FFFFFF; --ink:#14201F; --muted:#5C6B6A;
  --hair:#DFE4E3; --accent:#0E6F6B;
  --b-high:#0E6F6B; --b-high-ink:#FFFFFF;
  --b-mid:#4FA8A2;  --b-mid-ink:#14201F;
  --b-low:#BCDCD8;  --b-low-ink:#14201F;
  --b-neg:#A33A2A;  --b-neg-ink:#FFFFFF;
  --b-none:#DDE2E1; --b-none-ink:#5C6B6A;
  --hatch:rgba(20,32,31,.16);
  --serif:"Hiragino Mincho ProN","Yu Mincho",YuMincho,"Noto Serif JP","Songti SC",serif;
  --sans:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP",system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --ground:#0E1615; --surface:#151F1E; --ink:#E8EDEC; --muted:#94A5A3;
  --hair:#2A3634; --accent:#6BC5BE;
  --b-high:#93DED7; --b-high-ink:#0E1615;
  --b-mid:#3B9B93;  --b-mid-ink:#0E1615;
  --b-low:#22504B;  --b-low-ink:#E8EDEC;
  --b-neg:#E08472;  --b-neg-ink:#0E1615;
  --b-none:#2C3837; --b-none-ink:#94A5A3;
  --hatch:rgba(232,237,236,.16);
}}}}
:root[data-theme="dark"]{{
  --ground:#0E1615; --surface:#151F1E; --ink:#E8EDEC; --muted:#94A5A3;
  --hair:#2A3634; --accent:#6BC5BE;
  --b-high:#93DED7; --b-high-ink:#0E1615;
  --b-mid:#3B9B93;  --b-mid-ink:#0E1615;
  --b-low:#22504B;  --b-low-ink:#E8EDEC;
  --b-neg:#E08472;  --b-neg-ink:#0E1615;
  --b-none:#2C3837; --b-none-ink:#94A5A3;
  --hatch:rgba(232,237,236,.16);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1080px;margin:0 auto;padding:56px 24px 96px;display:flex;flex-direction:column;gap:52px}}
.eyebrow{{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin:0 0 14px}}
h1{{font-family:var(--serif);font-size:clamp(30px,5vw,46px);line-height:1.24;margin:0 0 18px;
  font-weight:600;letter-spacing:.01em;text-wrap:balance}}
.lede{{max-width:62ch;margin:0;color:var(--muted);font-size:16px}}
.lede strong{{color:var(--ink);font-weight:600}}
h2{{font-family:var(--serif);font-size:22px;font-weight:600;margin:0 0 6px;letter-spacing:.02em}}
h2+.sub{{margin:0 0 20px;color:var(--muted);font-size:13.5px;max-width:64ch}}
section{{display:block}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}
.tile{{background:var(--surface);border:1px solid var(--hair);border-radius:3px;padding:20px 20px 18px}}
.tile .k{{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;color:var(--muted);
  text-transform:uppercase;display:block;margin-bottom:10px}}
.tile .n{{font-family:var(--serif);font-size:38px;line-height:1;font-variant-numeric:tabular-nums;
  display:block;color:var(--accent)}}
.tile .n small{{font-size:16px;color:var(--muted);margin-left:3px}}
.tile .d{{display:block;margin-top:10px;font-size:12.5px;color:var(--muted);line-height:1.6}}
.scroll{{overflow-x:auto;border:1px solid var(--hair);border-radius:3px;background:var(--surface)}}
table{{border-collapse:separate;border-spacing:2px;width:100%;min-width:820px}}
caption{{caption-side:top;text-align:left;padding:14px 14px 4px;font-size:12.5px;color:var(--muted)}}
thead th{{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);font-weight:400;padding:8px 10px;text-align:left;white-space:nowrap}}
tbody th{{text-align:left;font-weight:400;padding:8px 12px 8px 14px;white-space:nowrap;
  border-right:1px solid var(--hair)}}
.sn{{font-size:13.5px}}
.sv{{font-family:var(--mono);font-size:11px;font-variant-numeric:tabular-nums;
  padding:2px 6px;border-radius:2px;margin-left:9px;vertical-align:1px}}
.tag{{font-size:10.5px;color:var(--muted);margin-left:7px;border:1px solid var(--hair);
  padding:1px 5px;border-radius:2px}}
.cell{{padding:8px 11px;border-radius:2px;min-width:172px;vertical-align:middle}}
.cn{{display:block;font-size:12.5px;line-height:1.4}}
.cv{{display:block;font-family:var(--mono);font-size:10.5px;opacity:.85;
  font-variant-numeric:tabular-nums;margin-top:2px}}
.cell:hover{{outline:2px solid var(--ink);outline-offset:-2px}}
.b-high{{background:var(--b-high);color:var(--b-high-ink)}}
.b-mid {{background:var(--b-mid); color:var(--b-mid-ink)}}
.b-low {{background:var(--b-low); color:var(--b-low-ink)}}
.b-neg {{background:var(--b-neg); color:var(--b-neg-ink)}}
.b-none{{background:var(--b-none);color:var(--b-none-ink);
  background-image:repeating-linear-gradient(45deg,transparent 0 5px,var(--hatch) 5px 6px)}}
.legend{{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:16px;font-size:12px;color:var(--muted)}}
.lg{{display:inline-flex;align-items:center;gap:7px}}
.lg i{{width:15px;height:15px;border-radius:2px;display:inline-block;border:1px solid var(--hair)}}
ol.rank{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:5px}}
ol.rank li{{display:grid;grid-template-columns:minmax(140px,220px) 1fr 34px 52px;
  align-items:center;gap:12px}}
.bn{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bt{{display:block;height:15px;background:var(--hair);border-radius:2px}}
.bar{{display:block;height:100%;border-radius:0 4px 4px 0}}
.bc{{font-family:var(--mono);font-size:12px;text-align:right;font-variant-numeric:tabular-nums}}
.br{{font-family:var(--mono);font-size:10.5px;text-align:center;padding:2px 0;border-radius:2px;
  font-variant-numeric:tabular-nums}}
ul.lost{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}}
ul.lost li{{display:grid;grid-template-columns:minmax(150px,1fr) 60px auto;gap:14px;
  align-items:center;padding:9px 2px;border-bottom:1px solid var(--hair);font-size:13.5px}}
ul.lost li:last-child{{border-bottom:0}}
.lv{{font-family:var(--mono);font-size:11px;text-align:center;padding:2px 0;border-radius:2px;
  font-variant-numeric:tabular-nums}}
.lc{{font-family:var(--mono);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}}
.note{{background:var(--surface);border:1px solid var(--hair);border-left:3px solid var(--accent);
  border-radius:3px;padding:22px 24px}}
.note h3{{font-family:var(--serif);font-size:17px;margin:0 0 10px;font-weight:600}}
.note p{{margin:0 0 12px;max-width:64ch;font-size:14px}}
.note p:last-child{{margin-bottom:0}}
.note strong{{font-weight:600}}
footer{{border-top:1px solid var(--hair);padding-top:20px;font-size:12px;color:var(--muted);
  line-height:1.8}}
footer code{{font-family:var(--mono);font-size:11px}}
@media (max-width:640px){{
  ol.rank li{{grid-template-columns:minmax(110px,1fr) 1fr 30px 46px;gap:8px}}
  .wrap{{padding:36px 16px 64px;gap:40px}}
}}
</style>

<div class="wrap">
<header>
  <p class="eyebrow">LOOTY ／ {D['captured']} 実測</p>
  <h1>関連商品の枠を、<br>誰が取っているか</h1>
  <p class="lede">いま <strong>35商品すべてのページで、関連商品セクションは表示されていません</strong>（公開ページのHTMLで確認）。
  ただしShopifyのレコメンド機能自体は動いていて、各商品に10件の「関連商品」を返し続けています。
  ここに出しているのは、<strong>もしセクションを戻したら実際に何が並ぶか</strong>です。
  色は、その推薦先が <strong>広告1円あたりいくら利益を生んでいるか</strong>（{D['window']} 実測）。</p>
</header>

<section>
  <div class="tiles">
    <div class="tile"><span class="k">いま表示されている数</span>
      <span class="n">0<small>/ 35商品</small></span>
      <span class="d">どのページにも <code>product-recommendations</code> は無い。セクション自体が外れている。</span></div>
    <div class="tile"><span class="k">上位4枠を季節商品が占める割合</span>
      <span class="n">{seas4/top4_total*100:.0f}<small>%</small></span>
      <span class="d">{top4_total}枠のうち{seas4}枠。9月に売り物でなくなる商品へ客を送ることになる。</span></div>
    <div class="tile"><span class="k">上位4枠を広告停止中の商品が占める割合</span>
      <span class="n">{noad4/top4_total*100:.0f}<small>%</small></span>
      <span class="d">{noad4}枠。広告を出していない＝売る意思のない商品が枠を持っている。</span></div>
  </div>
</section>

<section>
  <h2>もしセクションを戻したら、各ページに並ぶ4件</h2>
  <p class="sub">行が商品ページ、列がその枠。左端の数字はその商品自身の広告1円あたり利益。
  セルの色と数字は<strong>推薦先</strong>の成績です。</p>
  <div class="scroll">
    <table>
      <caption>Shopifyレコメンド（intent=related）の実測順。全10件のうち上位4件を表示。</caption>
      <thead><tr><th>この商品のページに</th><th>第1枠</th><th>第2枠</th><th>第3枠</th><th>第4枠</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <div class="legend">{legend}</div>
</section>

<section>
  <h2>枠の取り合い</h2>
  <p class="sub">{D['n_products']}商品 × 上位4枠 = {top4_total}枠を、どの商品が何回取っているか。</p>
  <ol class="rank">{bars}</ol>
</section>

<section>
  <h2>いちばん儲かっている商品ほど、推薦されていない</h2>
  <p class="sub">広告1円あたり +0.60円以上を稼いでいる{len(winners)}商品が、{top4_total}枠のうち取れているのは合計 {win_top4} 枠だけ。</p>
  <ul class="lost">{lost}</ul>
</section>

<section class="note">
  <h3>なぜこうなるのか</h3>
  <p>Shopifyの関連商品は<strong>過去の注文履歴</strong>から算出されます。売れた実績が多いほど推薦されやすく、
  出したばかりの商品は履歴が無いので推薦されない。</p>
  <p>結果として、<strong>夏に大量に売れた季節商品と、もう広告を止めた商品が枠を独占</strong>し、
  いま一番効率のいいインソール・W固定スマホ車載ホルダー・2WAYシートボックスはほとんど出てこない。
  この仕組みは放っておくと必ずこうなります。履歴が増える頃には、その商品の旬は終わっているからです。</p>
  <h3 style="margin-top:18px">だから、どうするか</h3>
  <p><strong>今のまま（表示しない）で正しい。</strong>
  この並びのままセクションを戻すと、勝っている商品ページから、9月に消える季節商品へ客を流すことになります。
  以前おすすめ一覧を出してCVRが悪化したのは、この構造がそのまま出ていたためと説明がつきます。</p>
  <p>もし将来また出すなら、アルゴリズム任せではなく<strong>手動で並びを指定</strong>し、
  <strong>車まわり（W固定 ↔ 2WAYシートボックス）のように文脈がつながる組み合わせだけ</strong>に絞ってください。
  実際、2WAYシートボックスのページでは第1枠がW固定になっており、この1組だけはアルゴリズムも正しく当てています。</p>
</section>

<footer>
  推薦データ＝<code>looty-japan.com/recommendations/products.json</code>（{D['captured']} 取得・intent=related・limit=10）。
  成績＝Shopify実売（gross−discounts）とMeta広告費の {D['window']} 実測から算出した「広告1円あたり利益」。
  広告費が13日で3,000円に満たない商品は測れないため「広告を出していない」として扱っています。
  価格はすべて税込表示前の商品設定価格。
</footer>
</div>
'''
open(OUT, 'w', encoding='utf-8').write(HTML)
print('書き出し', OUT, len(HTML), 'bytes')
print(f'上位4枠 {top4_total} / 季節 {seas4} ({seas4/top4_total:.0%}) / 広告なし {noad4} ({noad4/top4_total:.0%})')
print(f'勝ち組{len(winners)}商品の合計上位4枠 = {win_top4}')
