# TikTok

取数见 [../datalayer/tiktok.md](../datalayer/tiktok.md),选不选这条路见
[cost-ranking.md](cost-ranking.md)。

搜索端点不返回 bio,联系方式在 bio 里 —— 必须两步:先拿 handle,再逐个查 profile。

## 全链路

```
① 内容搜索          1 credit    → 30 条视频,去重约 29 个作者(无 bio)
② 客户端筛          0 credit    → 按累计播放降序取前 N
③ 逐个查 profile    1 credit/人 → signature + bioLink
④ 从 bio 抠邮箱     0 credit
⑤ 无邮箱者走第二跳   0 credit
```

**筛必须在 ③ 之前。** 每放过一个人就是 1 credit,总开销由 ② 决定。

### ① 内容搜索

```
GET /v1/scrape/tiktok/search/keyword?query=<关键词>&sort_by=most-liked
```

**参数名是 `query`,不是 `keyword`。** 传错返 400,不扣 credit。

从 `data.search_item_list` 取三个字段:

```
aweme_info.author.unique_id        handle
aweme_info.author.follower_count   粉丝数
aweme_info.statistics.play_count   播放量
```

按 `unique_id` 去重并累加播放量。**同一作者重复出现是垂类相关度的信号。**

`author.signature` 在这里是空的。

不用 `search/users`:它匹配用户名/昵称而非内容,出来的多是空壳号。

### ② 客户端筛

按累计播放量降序。**播放量比粉丝数更能反映当下活跃度** —— 几千粉的账号可以有十几万播放。

### ③ 逐个查 profile

```
GET /v1/scrape/tiktok/profile?handle=<unique_id>
```

```
data.user.signature        bio,80 字符上限
data.user.bioLink.link     外链;bioLink 是 {link, risk} 对象,不是字符串
```

### ④⑤ 抠邮箱与第二跳

正则从 `signature` 抠。抠不到就顺 `bioLink.link` 走
[landing-page-two-hop.md](landing-page-two-hop.md)。

bio 里的联系方式不一定是邮箱 —— WhatsApp 号、Instagram handle **都算可触达**。

## 可预期的命中

```
bio 非空        约 100%
bio 有邮箱      约 53%      ← 高于 Instagram 一倍多
有 bioLink      约 93%
可触达          约 93%
```

## 解析上的坑

- **`search_item_list` 与 `user_list` 是 dict 不是 list**,键是 `"0"`…`"29"`。
  直接下标取 `[0]` 会 KeyError,要先 `.values()`。
- **`bioLink` 是对象**,取 `.link`。
- **空 bio 是真的空。** 百万粉账号也可能 `signature` 为空、`bioLink` 为 `None`,
  那是本人没填,不是端点坏了。

## 换供应商

ScrapeCreators 同链路端点等价,路径去掉 `/scrape`:
`/v1/tiktok/search/keyword`、`/v1/tiktok/profile`,参数名与字段路径一致。
