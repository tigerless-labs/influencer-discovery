# Instagram

第三方 API:ScrapeCreators。**唯一能按资料内容检索账号的平台。**

## 发现:`/v1/instagram/search/profiles`

`query` 吃的是 **bio 或 caption 的关键词**,不是用户名。这是 175 个端点里唯一能按
博主属性找人的地方。

**1 credit → 4 至 7 个博主**,结果带:

```
biography · bio_links · external_url · category_name
is_business_account · is_professional_account · is_verified · is_private
username · full_name
```

**没有 `follower_count`** —— 粉丝数只在 profile 端点里。

**搜索结果已带 bio 与外链**,判人够用;这是它和 TikTok 的结构性差别。

**多词 query 会 500。** `ai agent` 正常,`ai tools` 稳定报错。

query 吃 bio 文本本身,所以筛选条件可以写进检索词,不必事后过滤。

底层是 Google 索引的包装(cursor 是 Google 结果页)。**翻页返回不稳定** —— 同一个 query
连翻三次拿到 5 / 7 / 3 个,首个结果会变。铺量靠多个 query 变体,不是翻页。

## 富化:`/v1/instagram/profile`

1 credit,给 `follower_count`、`biography`、`external_url`、`bio_links`。

**`business_email` 与 `business_phone_number` 恒为 null。** 74 个样本零命中,含
`is_business_account` 为真的账号。同一响应里 `business_contact_method` 有真值
(`CALL` / `UNKNOWN`)、`business_address_json` 有城市,**43 个账号的
`should_show_public_contacts` 还是 `true`** —— 结构是活的,只有这两个值被抠空。
匿名抓公开网页同样一个邮箱都没有。**值在登录墙后面,换供应商拿不到。**

同一次调用还带 `edge_related_profiles`(32 个同类账号)和近 12 条帖的互动数据。

## 单次消耗

搜索、富化各 1 credit。单价见 [providers.md](providers.md)。
