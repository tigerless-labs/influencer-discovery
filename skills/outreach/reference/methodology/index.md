# 渠道方法论

拿到数据之后,**联系方式在哪一页、从哪个入口进**。取数方式在
[datalayer/](../datalayer/index.md),两件事分开:那边只写平台的**能力边界**,
**做不做在这边裁决**,怎么拿也在这边。

**谁算目标不在这边** —— 三级准入(有受众的人 / 做分发的站 / 做自己产品的不进表)是设计,
见 [docs/design/index.md](../../../../docs/design/index.md)。这里只写各渠道据此怎么落。

## 目录即优先级

合作优先级由目录名的序号承载,**正文里不另写一份排序**。

**两档 blog 的分界是门槛,不是形态。** 自己买域名、自己建站、自己维护要花钱花力气,
**肯付这个成本的人才是把写作当事业的人** —— 那也正是会接商单的人。
注册就能发的平台没有这道筛子,上面多数人只是发过几篇文章,不是博主。

| 目录 | 是什么 | 渠道 |
|---|---|---|
| `_shared/` | 共享件,不是渠道 | 第二跳 · 卖买判别 · 成本排序 |
| `1-social/` | 大 social media | X · TikTok · Instagram · Threads · YouTube · Reddit · Mastodon |
| `2-blog-platform/` | 文章发在平台上,站不是他的 | [清单在它自己的 index](2-blog-platform/index.md) |
| `3-personal-site/` | **有门槛**:自己的域名、自己养的受众 | 自建博客 · Newsletter · Podcast |
| `4-distribution/` | 做分发的站,产出是投递入口不是人 | Website |
| `5-media/` | **有编辑审的多作者刊物**:目标是它的作者,不是刊物 | [清单在它自己的 index](5-media/index.md) |
| `_not-run/` | 不跑 | LinkedIn |

## 共享件

- [landing-page-two-hop.md](_shared/landing-page-two-hop.md) —— 平台页 → 本人站点 → 联系页,
  各渠道的共同后半段。**噪声与「不算数的地址」的通则住这里,渠道只写自己的例外。**
- [seller-vs-buyer.md](_shared/seller-vs-buyer.md) —— 落点站是内容站还是产品站,
  **决定这一行进不进表**。写进表之前的最后一道闸门。
- [cost-ranking.md](_shared/cost-ranking.md) —— 多条路之间怎么选:免费的排在付费的前面,
  付费的之间效率压过单价。

## 已跑通

**每条口径都有实测支撑。**

免费、不烧 credit 的:

- [podcast.md](3-personal-site/podcast.md) —— **产量最高**:一次免 key 的搜索 → feed → 邮箱,
  不解析页面
- [newsletter.md](3-personal-site/newsletter.md) —— 类目接口**目录型可穷尽**,feed 给地址
- [self-hosted.md](3-personal-site/self-hosted.md) —— 四个免 key 的发现源,偏性互补要交叉用
- [2-blog-platform/](2-blog-platform/index.md) —— 整档五个平台跑得通,全部免 key。
  **freeCodeCamp News 是其中唯一目录型可穷尽的**
- [youtube.md](1-social/youtube.md) —— 简介直接给邮箱的不到一成,产量靠链接区
- [website.md](4-distribution/website.md) —— 要投递入口,不要人

走付费取数层的:

- [instagram.md](1-social/instagram.md) —— 一步到位:搜索结果直接带 bio、外链、粉丝数
- [tiktok.md](1-social/tiktok.md) —— 两步,bio 里直接有邮箱的比例最高
- [reddit.md](1-social/reddit.md) —— 平台上没有联系方式,产出是人 + 他的域名
- [threads.md](1-social/threads.md) —— 两步,筛选只能在查完资料页之后做

## 已决定要做,数字未测

方法照着已跑通的渠道的形状写好了,**正文里的做法可用,命中率一个都还没测** ——
用之前先跑一轮,各自的「待验证」列了要先测哪几个数。

- [mastodon.md](1-social/mastodon.md) —— **自有域名不用推断**,平台自己做了归属校验;免 key 免登录
- [twitter-x.md](1-social/twitter-x.md) —— 话题搜索能找到人,取数走用户本人账号
- [micro-blog.md](2-blog-platform/micro-blog.md) —— 发现页背后的 JSON Feed 免 key,
  `author.url` 直接是他自己的站

## 不跑

- [linkedin.md](_not-run/linkedin.md) —— **没有发现这一步**,认证也换不来;
  连带写做了之后怎么拿、不做会怎样影响这条链的形状。

## 删掉的

对「找能做分发的博主」这个目标没有产出,原文在 git 历史里:

- **赞助位市场**(Passionfroot / Paved)—— 目录要账号,handle 只有历史链接一个来源,
  且六成已 404,会自然归零。
- **Medium** —— 平台上没有联系方式,资料页对 CLI 关着门。
- **GitHub** —— 那里的人多是 founder 与自建者,不是做分发的。
  作为**第二跳落点**仍然有用,做法留在 [landing-page-two-hop.md](_shared/landing-page-two-hop.md) 的第 ④ 档。

未写的:Product Hunt。空着。
