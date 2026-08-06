# TikTok

第三方 API:ScrapeCreators 或 SociaVault,两家端点等价(见 [providers.md](providers.md))。
**没有邮箱字段,且搜索结果不带 bio —— 后者是平台限制,换供应商无解。**

## 发现:两个端点,差一个量级

**`/v1/tiktok/search/users`** —— 参数只有 `query` / `cursor` / `trim`。
1 credit → 30 个 handle。实测:

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

## 实测

AI 垂类,内容搜索 → 逐个 profile(2026-08-06,SociaVault):

```
15 人 / 16 credits          ≈ 1.07 credit/人
bio 非空         15/15  100%
bio 直接有邮箱    8/15   53%
带 bioLink       14/15   93%
可触达           14/15   93%
```

**bio 里直接给邮箱的比例是 Instagram 的两倍多(53% vs 22%)。** 80 字符的限制反而
逼创作者只留最要紧的一条,而那条常常就是邮箱。样本只有 15,比 Instagram 那轮的 79 小得多,
数量级可信、精确值待更大样本。

个别账号 bio 里给的是 WhatsApp 号或 Instagram handle,不是邮箱 —— 也算可触达。

早前一次用 `/v1/tiktok/profile` 试 `@zasai26`(348 万粉)拿到空 `signature` 和
`bioLink: None`,曾被误读为「TikTok profile 也不给 bio」。那是**个别账号真没填**,
不是端点限制。

## 单价

```
Instagram   0.15 credit/可触达,搜索一步到位
TikTok      1.14 credit/可触达,必须两步
```

**TikTok 贵 7.6 倍,但不是因为 bio 少,是因为搜索不带 bio 逼出了第二步调用。**
排序与选择见 [../methodology/cost-ranking.md](../methodology/cost-ranking.md)。
