# 大 blog 平台

**注册就发、无编辑门槛的写作平台。** 与自建博客的分界是**站不是他的** ——
页脚没有他的邮箱,联系方式只能从平台的作者字段,或从他自己的域名走
[第二跳](../_shared/landing-page-two-hop.md)。

**这一档没有门槛,所以上面多数人不是博主。** 自建站要花钱花力气维护,
**肯付这个成本的人才会接商单**;这里注册就能发,那道筛子不存在。

所以这一档的第一道筛统一是:**他在平台之外还养着一个站吗。**
`canonical` 指向站外、作者字段里的自有域名、自定义域名 —— 哪个平台给什么各写在各自那份,
但判据是同一个。

## 有自己一份的

| 平台 | 入口 |
|---|---|
| [DEV.to](dev-to.md) | 公开 API 免 key,作者对象随文章内联 |
| [WordPress.com](wordpress-com.md) | 标签流免 key,`nice_name` 通向 Gravatar 的公开邮箱 |
| [Micro.blog](micro-blog.md) | 发现页背后的 JSON Feed,`author.url` 直接是他自己的站 |
| [Hashnode](hashnode.md) | 未跑通;官方有赞助通道 |

## 还没有,各自卡在哪

**每条都是实测的结论,不是猜的。**

| 平台 | 卡点 |
|---|---|
| Bear Blog | 发现页对诚实 UA 返回质询页。**不绕**,这一档到此为止 |
| Tumblr | 标签接口要 API key,免登录取不到 |
| write.as | 阅读页可取,但没有 feed,只能解析 HTML;没跑 |
| Mirror / Paragraph | 没试;写作者集中在加密垂类,和我们的垂类不重合 |

**freeCodeCamp News 与 HackerNoon 有编辑审**,不满足这一档「无门槛」的定义,
但它们的作者仍然自带受众。**归哪一档未定** —— 不要照着上面几份的做法套。

## 不归这一档的

- **自建博客**(自有域名、页脚是他的)—— 见 [self-hosted.md](../3-personal-site/self-hosted.md)。
- **Substack** —— 归 [newsletter.md](../3-personal-site/newsletter.md),那一档有赞助入口这条捷径。
- **Medium** —— **不做**:平台上没有联系方式,资料页对 CLI 关着门。
- **Hacker News 与 Lobsters** —— 不承载文章,是 self-hosted.md 的发现源。
- **多作者刊物** —— 有编辑、卖广告位的归 [media.md](../_not-run/media.md)。

## 待验证

- **卖买比例。** 这一档整体最关键的缺口:平台上的人有多少是做自己产品的。
  DEV.to 那一份里列为第一条,结论会外溢到整档。
- **样本质量。** 三个跑通的入口默认都是最新流。DEV.to 上已证实按时间取会拿到七成零互动的作者,
  另两个还没找到对应的排序开关。
