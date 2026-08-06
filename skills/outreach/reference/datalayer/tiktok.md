# TikTok

第三方 API:ScrapeCreators 或 SociaVault,两家端点等价(见 [providers.md](providers.md))。
**没有邮箱字段,且搜索结果不带 bio —— 后者是平台限制,换供应商无解。**

## 发现:两个端点,差一个量级

**`/v1/tiktok/search/users`** —— 参数只有 `query` / `cursor` / `trim`。
1 credit → 30 个 handle:

```
signature(bio)   30/30 全空
整个响应的邮箱    0 个
search_user_desc  只是昵称("Nancy | Fitness Coach"),不是 bio
```

匹配的是**用户名/昵称**,不是 bio 内容。搜 `"business inquiries" fitness coach`
命中的是 `@thefitnessbusinesscoach` 这类账号。可用的只有 `follower_count`。

**`/v1/tiktok/search/keyword`** —— 同样 1 credit → 30 条视频,从视频反推作者。
同一批关键词下质量高得多:粉丝 >5 万的 7 个 vs 搜用户的 4 个,且带播放/点赞/评论数。
**同一个作者重复出现本身就是垂类相关度的信号。**

作者的 `signature` 在这里同样是空的。

## 富化:`/v1/tiktok/profile`

**1 credit 一个人**,给 `signature`(bio,80 字符上限)和
`bioLink`(`{link, risk}`,risk 是 TikTok 自己的风险评分)。

没有 `business_email`,邮箱只能顺 `bioLink` 出去抓落地页。

## 消耗

**约 1.14 credit / 可触达联系方式** —— 是 Instagram 的 7.6 倍。

贵不是因为 bio 少 —— **bio 里直接给邮箱的比例反而是 Instagram 的两倍多**。
贵在搜索不带 bio,逼出了每人一次的第二步调用。

命中结构与做法见 [../methodology/tiktok.md](../methodology/tiktok.md),
选路见 [../methodology/cost-ranking.md](../methodology/cost-ranking.md)。
