# TikTok

第三方 API:ScrapeCreators 或 SociaVault,两家端点等价(见 [providers.md](providers.md))。
**bio 在 profile 里,不在搜索结果里** —— 每个人都要单独再查一次,换供应商消不掉这一次。
**profile 不含任何结构化联系字段**,对外线索只有 `signature` 文本与 `bioLink`。

## 发现:两个端点,差一个量级

**`/v1/tiktok/search/users`** —— 参数只有 `query` / `cursor` / `trim`。
1 credit → 30 个 handle:

```
signature(bio)     一律为空
search_user_desc   只是昵称,不是 bio
follower_count     有值
```

**匹配的是用户名/昵称,不是资料内容** —— 检索词只会命中名字里带那些字的账号。
这一档能用的字段只有 `follower_count`。

**`/v1/tiktok/search/keyword`** —— 同样 1 credit → 30 条视频,**按内容匹配**,
从视频反推作者。带播放/点赞/评论数,同一个作者可重复出现。

作者的 `signature` 在这里同样是空的。

## 富化:`/v1/tiktok/profile`

**1 credit 一个人**,给 `signature`(bio,80 字符上限)和
`bioLink`(`{link, risk}`,risk 是 TikTok 自己的风险评分)。

**没有 Instagram 那组商务字段** —— 资料里的对外线索只有 `bioLink` 一个。

## 单次消耗

搜索、profile 各 1 credit。**搜索不带 bio,所以每个候选都要多付一次 profile** ——
这是它和 Instagram 唯一的成本差异来源。单价见 [providers.md](providers.md)。
