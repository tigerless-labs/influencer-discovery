# Instagram

第三方 API:ScrapeCreators。**唯一直接给邮箱字段的平台。**

## 发现:`/v1/instagram/search/profiles`

`query` 吃的是 **bio 或 caption 的关键词**,不是用户名。这是 175 个端点里唯一能按
博主属性找人的地方。

**1 credit → 10 个博主**,结果直接带:

```
biography · bio_links · external_url · follower_count · following_count
media_count · category_name · is_business_account · is_professional_account
is_verified · is_private · username · full_name
```

搜索结果就带 bio 和外链,不用再逐个查 profile —— 这是它比 TikTok 便宜 10 倍的原因。

query 直接吃 bio 文本,等于可以自定义筛选条件:`"business inquiries" + 垂类词`、
`"@gmail.com" + 垂类词`、`"linktr.ee" + 垂类词`。

底层是 Google 索引的包装(cursor 是 Google 结果页),**单个 query 大约几十到一百来个结果**,
铺量要靠多个 query 变体,不是无限翻页。

## 富化:`/v1/instagram/profile`

1 credit,给 `business_email` / `business_phone_number` / `business_address_json` /
`business_contact_method` —— 专业号填了就直接给,不用点那个带 CAPTCHA 的按钮。

同一次调用还带 `edge_related_profiles`(32 个同类账号)和近 12 条帖的互动数据。

## 消耗

**约 0.15 credit / 可触达联系方式** —— 全部路径里最低。

命中结构与做法见 [../methodology/instagram.md](../methodology/instagram.md)。
