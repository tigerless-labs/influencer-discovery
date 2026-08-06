# 免认证

纯 HTTP 或官方免费接口就能取到,不需要登录态、不烧 credit。

覆盖 YouTube、Newsletter、Blog、Website、Podcast、Passionfroot、Paved、GitHub、
Hacker News、DEV.to、Product Hunt、Medium,以及所有第二跳的落地页。

## 已确定的

- **这是本项目的主路。** 设计文档已定:只做公开页,不做认证墙后
  (见 [platforms.md](../../../../docs/design/platforms.md))。
- **YouTube 的商务邮箱按钮后面是 reCAPTCHA**,不碰。能用的是简介文本和链接区。
- **YouTube 官方 Data API 没有邮箱字段** —— 不是权限问题,字段根本不存在。
- **GitHub 用官方 API,不用 cookie 也不爬页面。** 它是唯一系统性给 `email` 字段的平台。
- **落地页那一层不需要认证,也不烧 credit,是覆盖率增量最大的一块。**

## 待探索

各渠道的具体入口与页面形态 —— 逐个跑通后回填。已知要先答的几个:

- **要不要浏览器。** 频道简介与链接区、聚合页(linktr.ee / beacons.ai / stan.store)的
  链接,是在初始 HTML 里还是要执行 JS。这一条决定整档的取数形态。
- **YouTube 官方 Data API 的免费配额**能不能承担「已知频道 → 简介与链接」的富化,
  从而只在发现阶段抓页面。
- **GitHub API 带 token 与不带**的速率差,以及本项目的实际用量落在哪一档。
- **播客 RSS 的 `<itunes:owner>`** 是否普遍可取、从节目主页找到 feed 地址的可靠路径。
- **赞助位市场的公开目录不登录能翻到多少** —— 有没有分类/分页上限。这一条决定
  Passionfroot 与 Paved 是目录型(翻到底)还是退化成搜索型,是它们停止语义的前提。
- **Medium 未登录能看到作者资料页多少** —— 外链是否可见。
