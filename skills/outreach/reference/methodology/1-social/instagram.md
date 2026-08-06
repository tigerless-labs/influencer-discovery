# Instagram

取数见 [datalayer/instagram.md](../../datalayer/instagram.md),选不选这条路见
[cost-ranking.md](../_shared/cost-ranking.md)。

搜索结果自带 bio、外链、粉丝数 —— 一步到位,不需要逐个查 profile。

## 全链路

```
① bio 关键词搜索     1 credit/次  → 每次 10 个博主,带 bio + 外链 + 粉丝数
② 多组 query 变体    0 credit     → 变体间重叠严重,按 username 去重
③ 客户端筛           0 credit     → 粉丝区间;follower_count 已在结果里
④ 从 bio 抠邮箱      0 credit
⑤ 无邮箱者走第二跳    0 credit
```

### ① bio 关键词搜索

```
GET /v1/instagram/search/profiles?query=<bio 关键词>
```

**`query` 吃的是 bio 文本,不是用户名。** 筛选条件写进 query 本身,筛掉的人不产生调用:

```
"business inquiries" <垂类词>     只出主动挂了商务联系的
"@gmail.com" <垂类词>             锁定 bio 里写了邮箱的
"linktr.ee" <垂类词>              锁定有落地页的
<垂类词> <城市名>                  变相地区筛选
```

从 `profiles` 取:

```
username · full_name · biography · bio_links[].url · external_url
follower_count · media_count · category_name
is_business_account · is_professional_account · is_verified · is_private
```

### ② 多组 query 变体

底层是 Google 索引的包装(cursor 是 Google 结果页),**单个 query 大约几十到一百来个结果**。
铺量靠变体,不是翻页。**去重必须在累积时做**,否则同一个人被抓多次。

偶发 500,跳过该 query 继续,不重试。

### ③ 客户端筛

粉丝 <1,000 直接丢,全是噪声。

### ④⑤ 抠邮箱与第二跳

正则从 `biography` 抠。抠不到就顺 `bio_links[].url` 或 `external_url` 走
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md)。

## 可预期的命中

```
bio 有邮箱          约 22%
有外链              约 88%
落地页再挖出         约 36%(占无邮箱且有外链者)
可触达(邮箱∪外链)   约 94%
```

外链以 `linktr.ee` 为压倒性第一,其次 `youtube.com`、`stan.store`、`bit.ly`。
**创作者不把邮箱写 bio,他们挂 Linktree** —— 增量全在第二跳,而第二跳不花 credit。

落地页挖出的含噪声(模板占位符、建站平台公共邮箱),去噪后总净命中约 38–40%。
噪声类型见 [landing-page-two-hop.md](../_shared/landing-page-two-hop.md)。

**邮箱和外链都落空的那部分**,拿同一个 handle 去 Threads 换一份 bio 再试,
见 [threads.md](threads.md)。

## 解析上的坑

- **邮箱正则必须跑在 `biography` 原文串上,不能跑在 `json.dumps` 之后的串上。**
  dumps 把换行变成字面的 `\n`,`\w` 会匹配到那个 `n`,抠出 `nJoey@example.com` 这种粘连地址。
- **去尾部标点。** `xxx@gmail.com。` 会连句号一起抠走。

## 不做的

- **不用 `/v1/instagram/profile` 逐个富化。** 搜索结果已带除 `business_email` 外的全部字段。
  只有确认某人是专业号、且要 `business_email` 时才值得多花 1 credit。
- **不做 `edge_related_profiles` 滚雪球。** 一个种子展开 32 个,一层吃掉大量额度,
  而 bio 关键词搜索直接命中垂类,更省也更准。
