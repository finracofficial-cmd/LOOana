#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""データソースの分担を機械的に強制する（2026-08-04 ユーザー指定）

Meta = 広告費と配信指標だけ。
売上・個数・注文数・単価は必ず Shopify。

2026-08-04に同じ原因で4件の誤りを出したため、口頭ルールではなく import して使う関数にした。
分析スクリプトは必ず先頭で `from datarules import *` すること。
"""

# Meta から取ってよいフィールド（配信の実績。Shopifyには存在しない）
META_OK = {
    'cost', 'impressions', 'CPM', 'link_CTR', 'outbound_clicks',
    'Frequency', 'reach', 'date', 'adcampaign_name', 'adset_name', 'ad_name',
}

# Meta から取れるが、損益計算に使ってはいけないフィールド
META_FORBIDDEN = {
    'offsite_conversions_fb_pixel_purchase':
        'Metaの購入数は「注文数」であり「個数」ではない。まとめ買い商品で必ずズレる。'
        'さらに実測より約9%少なく計上される。→ Shopifyの orders / net_items_sold を使う',
    'offsite_conversion_value_fb_pixel_purchase':
        'Metaのコンバージョン値はカート全体の金額。商品の売価ではない。'
        '÷購入数はAOVであって単価ではない。→ Shopifyの gross_sales を使う',
    'ROAS': 'Metaの自己申告。→ MER = Shopify実売 ÷ Meta広告費 を使う',
}


def check_meta_fields(fields):
    """Metaクエリのfieldsを検証する。禁止フィールドが混ざっていたら理由付きで落とす。"""
    if isinstance(fields, str):
        fields = [f.strip() for f in fields.split(',')]
    bad = [f for f in fields if f in META_FORBIDDEN]
    if bad:
        msg = '\n'.join(f'  - {f}: {META_FORBIDDEN[f]}' for f in bad)
        raise AssertionError(
            f'Metaから取ってはいけないフィールドが指定されています:\n{msg}\n'
            f'突合チェック目的なら check_meta_fields(..., reconciliation=True) を使うこと。')
    return fields


def meta_for_reconciliation(fields):
    """突合サニティチェック専用。ここで取った値は損益計算に流用しない。"""
    return fields


class Product:
    """商品1つ分の実測値。売上系は必ずShopify、広告費はMeta。

    gross      : Shopify gross_sales（値引き前）
    items      : Shopify net_items_sold（個数）
    orders     : Shopify orders（注文数）
    unit_cost  : 原価表（Shopify unitCost・送料込み）
    ad_cost    : Meta cost
    clicks     : Meta outbound_clicks（任意・CVR算出用）
    """

    def __init__(self, name, gross, items, orders, unit_cost, ad_cost, clicks=None):
        assert items > 0, f'{name}: 個数が0'
        self.name = name
        self.gross, self.items, self.orders = gross, items, orders
        self.unit_cost, self.ad_cost, self.clicks = unit_cost, ad_cost, clicks

    @property
    def price(self):
        """平均単価。Shopifyの gross ÷ 個数。Metaからは絶対に出さない。"""
        return self.gross / self.items

    @property
    def gp_unit(self):
        """1個あたり粗利"""
        return self.price - self.unit_cost

    @property
    def items_per_order(self):
        return self.items / self.orders

    @property
    def gp_order(self):
        """1注文あたり粗利 = 分岐CPA（注文ベース）。
        まとめ買い商品はこちらで判定する。1個分の粗利と比べると必ず赤字に見える。"""
        return self.gp_unit * self.items_per_order

    @property
    def cogs(self):
        return self.unit_cost * self.items

    @property
    def profit(self):
        return self.gross - self.cogs - self.ad_cost

    @property
    def mer(self):
        return self.gross / self.ad_cost

    @property
    def mer_be(self):
        """損益分岐MER"""
        return self.gross / (self.gross - self.cogs)

    @property
    def margin(self):
        return self.profit / self.gross

    @property
    def cpa_order(self):
        """注文あたりCPA。分岐は gp_order と比べる"""
        return self.ad_cost / self.orders

    @property
    def cvr(self):
        """CVR = Shopify注文数 ÷ Metaアウトバウンドクリック。
        分子はShopify、分母はMeta。Metaの購入数は使わない。"""
        assert self.clicks, f'{self.name}: クリック数が未設定'
        return self.orders / self.clicks

    def row(self):
        return dict(商品=self.name, 売上=self.gross, 個数=self.items, 注文=self.orders,
                    単価=round(self.price), 粗利_個=round(self.gp_unit),
                    個数_注文=round(self.items_per_order, 2),
                    分岐CPA_注文=round(self.gp_order), CPA_注文=round(self.cpa_order),
                    原価=round(self.cogs), 広告費=self.ad_cost, 利益=round(self.profit),
                    MER=round(self.mer, 3), 分岐MER=round(self.mer_be, 3),
                    余裕=round(self.mer - self.mer_be, 3))


def reconcile(product, meta_orders):
    """突合サニティチェック。Metaの計上率を出すだけ。判断には使わない。"""
    r = meta_orders / product.orders if product.orders else float('nan')
    flag = '' if 0.70 <= r <= 1.05 else ' ⚠️'
    return f'{product.name}: Meta計上率 {r*100:.0f}%{flag}'


if __name__ == '__main__':
    # 2026-08-04 の誤りを再現しないことの確認
    gaichu = Product('害虫ブロッカー', gross=1098480, items=275, orders=161,
                     unit_cost=867, ad_cost=504023, clicks=5496)
    print('7/27週 害虫ブロッカー（Shopify実測）')
    for k, v in gaichu.row().items():
        print(f'  {k:12} {v:>12,}' if isinstance(v, (int, float)) else f'  {k:12} {v:>12}')
    print()
    print(f'  1個分の粗利 {gaichu.gp_unit:,.0f}円 と CPA {gaichu.cpa_order:,.0f}円 を比べると赤字に見えるが、')
    print(f'  正しい分岐は 1注文あたり粗利 {gaichu.gp_order:,.0f}円。実際は余裕 +{gaichu.gp_order-gaichu.cpa_order:,.0f}円/注文。')
    print()
    print(' ', reconcile(gaichu, 162))
    print()
    try:
        check_meta_fields('date,adcampaign_name,cost,offsite_conversions_fb_pixel_purchase')
    except AssertionError as e:
        print('ガード動作確認 →')
        print(e)
