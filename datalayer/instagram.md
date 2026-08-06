# Instagram

第三方 API:ScrapeCreators。**唯一按资料内容检索账号、且返回商务联系字段的平台。**

## 发现:`/v1/instagram/search/profiles`

`query` 吃的是 **bio 或 caption 的关键词**,不是用户名。这是 175 个端点里唯一能按
博主属性找人的地方。

**1 credit → 10 个博主**,结果直接带:

```
biography · bio_links · external_url · follower_count · following_count
media_count · category_name · is_business_account · is_professional_account
is_verified · is_private · username · full_name
```

**搜索结果已带 bio 与外链,不必再逐个查 profile。** 这是它和 TikTok 的结构性差别。

query 吃 bio 文本本身,所以筛选条件可以写进检索词,不必事后过滤。

底层是 Google 索引的包装(cursor 是 Google 结果页),**单个 query 大约几十到一百来个结果**,
铺量要靠多个 query 变体,不是无限翻页。

## 富化:`/v1/instagram/profile`

1 credit,给 `business_email` / `business_phone_number` / `business_address_json` /
`business_contact_method`。专业号填了就在响应里,**不经过网页上那个 CAPTCHA 保护的按钮**。

同一次调用还带 `edge_related_profiles`(32 个同类账号)和近 12 条帖的互动数据。

## 单次消耗

搜索、富化各 1 credit。单价见 [providers.md](providers.md)。
