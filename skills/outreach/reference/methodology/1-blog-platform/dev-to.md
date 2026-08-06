# DEV.to

公开 API 免 key、免登录。**发现和作者字段一次拿到,不用逐个查资料页。**

## 全链路

```
① 内容搜索        0 请求/人   → 每 tag 100 篇,内联作者的 website_url 与 handle
② 客户端筛        0 请求      → 按 reactions;字段已在结果里
③ 自有站走第二跳   1 请求/人
```

### ① 内容搜索

```
GET https://dev.to/api/articles?tag=<tag>&per_page=100&top=365
```

**`top` 参数是这条链的成败所在。** 不带它拿到的是最新流,**七成作者零 reaction**;
带 `top=365` 之后零 reaction 降到 7%,reactions 中位数 18、九分位 163。
`state=rising` 和最新流一样差。

从 `user` 对象取:

```
username · name · website_url · github_username · twitter_username
```

从文章取 `public_reactions_count`(受众信号)与 `canonical_url`
(指向站外 = 他有自己的博客,是自有域名的硬信号)。

铺量靠换 tag,不是翻页。**去重按 `username` 在累积时做** —— 跨 tag 重复出现的约两成,
那是垂类相关度的信号。

### ② 客户端筛

`reactions` 是这个平台唯一的公开受众指标,没有粉丝数字段。

### ③ 自有站走第二跳

顺 `website_url` 出去,见 [landing-page-two-hop.md](../_shared/landing-page-two-hop.md)。

## 可预期的命中

十二个 tag 一轮,558 个去重作者:

```
website_url        约 64%
canonical 指向站外  约 18%      ← 自有博客
跨 tag 出现        约 22%
```

## 两条不走的路

**不查资料页抠 bio。** `GET /api/users/by_username?url=<username>` 每人多一次请求,
bio 非空率 98% 但**里面有邮箱的只有 2%**。这条路的成本全部白付。

**不走 `github_username` 那一跳。** 它确实给得出邮箱,但拿这个字段当联系路径等于用
「这个人在写代码」筛「这个人会做分发」,选出来的偏 founder 与自建者 ——
按准入那一档不进表。判别见 [seller-vs-buyer.md](../_shared/seller-vs-buyer.md)。

## 停止语义

搜索型 —— **连续无新**。`top=365` 是一个时间窗不是目录,翻完不等于枯了,换 tag 还有人。

## 去重的键

`(username, DEV.to)`。

handle 唯一且稳定。**显示名不做键** —— `name` 可改可重。

## 边界

- 这个平台的人多是开发者写自己在做的东西,**买方密度可能高于个人博客**,
  卖买判别不能省。
- 作者的主场常常不在这里(自有博客、newsletter),`canonical_url` 指向站外的那批尤其。
  **从主场发现同一个人更便宜。**

## 待验证

- **卖买比例。** 这一档最关键的缺口,一次都没测。已抓到的标题与 tag 分布够判,还没跑。
- 剔掉 GitHub 那一跳之后,只走 `website_url` 的最终邮箱命中率。现有的可触达数字含
  GitHub,不能直接用。
- `top` 换成 30 / 90 与 365 的产出差别。
