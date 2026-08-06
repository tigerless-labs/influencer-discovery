# 渠道方法论

拿到数据之后,**联系方式在哪一页、从哪个入口进**。取数方式在
[../../../../datalayer/](../../../../datalayer/index.md),两件事分开:那边只写平台的**能力边界**,
**做不做在这边裁决**,怎么拿也在这边。

**谁算目标不在这边** —— 三级准入(有受众的人 / 做分发的站 / 做自己产品的不进表)是设计,
见 [index.md](../../../../docs/design/index.md)。这里只写各渠道据此怎么落。

## 共享件(不是渠道)

- [landing-page-two-hop.md](landing-page-two-hop.md) —— 平台页 → 本人站点 → 联系页,
  各渠道的共同后半段。**噪声与「不算数的地址」的通则住这里,渠道只写自己的例外。**
- [seller-vs-buyer.md](seller-vs-buyer.md) —— 落点站是内容站还是产品站,
  **决定这一行进不进表**。写进表之前的最后一道闸门。
- [cost-ranking.md](cost-ranking.md) —— 多条路之间怎么选:免费的排在付费的前面,
  付费的之间效率压过单价。

## 已跑通

**每条口径都有实测支撑。** 2026-08-06 在 AI 垂类跑了两轮:一轮走付费取数层,
一轮把免费渠道逐个验了一遍。

免费、不烧 credit 的:

- [podcast.md](podcast.md) —— **产量最高**:一次免 key 的搜索 → feed → 邮箱,不解析页面
- [website.md](website.md) —— **只做分发站**(工具推荐、目录、榜单),要的是投递入口不是人
- [blog.md](blog.md) —— 四个免 key 的发现源;首页拿不到就走 GitHub 一跳
- [newsletter.md](newsletter.md) —— Substack 的公开接口给发现,feed 给地址
- [github.md](github.md) —— 四条路并集过半,搜仓库取作者那条最好
- [youtube.md](youtube.md) —— 简介直接给邮箱的不到一成,产量靠链接区

走付费取数层的:

- [instagram.md](instagram.md) —— 一步到位:搜索结果直接带 bio、外链、粉丝数
- [tiktok.md](tiktok.md) —— 两步,bio 里直接有邮箱的比例最高
- [reddit.md](reddit.md) —— 平台上没有联系方式,产出是人 + 他的域名
- [threads.md](threads.md) —— 两步,筛选只能在查完资料页之后做

## 已决定要做,数字未测

方法照着已跑通的渠道的形状写好了,**正文里的做法可用,命中率一个都还没测** ——
用之前先跑一轮,各自的「待验证」列了要先测哪几个数。

- [mastodon.md](mastodon.md) —— **自有域名不用推断**,平台自己做了归属校验;免 key 免登录
- [twitter-x.md](twitter-x.md) —— 话题搜索能找到人,取数走用户本人账号

## 裁决为不做

- [media.md](media.md) —— **多作者刊物整类的裁决**:一个域名几百个作者,
  站上只给投稿信箱。这份是清单,防止把媒体当博主渠道跑
- [paved.md](paved.md) —— **整个赞助位市场这一类的裁决**:验过二十家,
  「有公开目录」与「给联系方式」从不同时出现
- [medium.md](medium.md) —— 平台上没有联系方式,资料页对 CLI 关着门
- [linkedin.md](linkedin.md) —— **没有发现这一步**,认证也换不来;
  连带写做了之后怎么拿、不做会怎样影响这条链的形状
- [mastodon.md](mastodon.md) —— **自有域名不用推断**,平台自己做了归属校验;免 key 免登录

[passionfroot.md](passionfroot.md) 是半个:**没有发现能力**,只能已知 handle 解析页面,
留作顺手解析。

**发布社区**(DEV.to、Hashnode 等)归 [blog.md](blog.md) 的清单,均未跑通。
Hacker News 与 Lobsters 不是发布社区,是 blog.md 的发现源,已跑通。

未写的:Product Hunt。空着。
