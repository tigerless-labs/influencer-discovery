# 媒体

**多作者刊物。裁决为不做。** 这份是一张清单,存在的唯一理由是
**防止把媒体当成博主渠道去跑**。

## 为什么不做

媒体不是一个能替我们分发的人:

- **署名不等于可触达。** 站上给的是 `editors@` 或投稿信箱 —— 那是版面的入口,不是人的地址,
  按通则不算数(见 [landing-page-two-hop.md](landing-page-two-hop.md))。
- **一个域名,几百个作者。** 按站建行会把他们塌成一行,正是
  [dedup.md](../../../../docs/design/dedup.md) 说的误合并。
- **版面可以买。** 要曝光,买位比找人确定 —— 但那是发信侧的事,不在本项目范围内。

## 判据

**多作者 + 有编辑 + 卖广告位**,三条同时成立就是媒体。

下面的清单是**兜底,不是判据** —— 命中即不建行、只记 log。实现之后它移到 `config/`
的共享域名清单,这里只留判据。

VentureBeat · TechCrunch · The Register · Ars Technica · ZDNet · InfoQ ·
The New Stack · DevOps.com · SD Times · Unite.AI · The AI Journal ·
Towards Data Science

## 边界

- **媒体上的作者本人可能是目标** —— 他在别处往往有自己的博客或 newsletter。
  那要从那边发现他,键是 `(作者显示名, 那个平台)`。**不从媒体这边进。**
- 清单只挡建行,不挡引用:文章链接仍可以当发现线索用。

## 待验证

- 媒体的作者页当发现源能出多少人。现在不跑,跟进项在
  [docs/TODO.md](../../../../docs/TODO.md)。
