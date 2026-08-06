# 免认证

纯 HTTP 或官方免费接口就能取到,不需要登录态、不烧 credit。**本项目的主路。**

覆盖 YouTube、Newsletter、Blog、Website、Podcast、Passionfroot、Paved、GitHub、
Hacker News、DEV.to、Product Hunt、Medium,以及所有第二跳的落地页。

## 已确定的

- **只做公开页,不做认证墙后** —— 设计文档已定,见
  [platforms.md](../../../../docs/design/platforms.md)。
- **YouTube 频道页能取到的是简介文本与链接区。** About 页那个联系方式按钮由 reCAPTCHA
  保护,**不碰**;官方 Data API 的频道资源里没有对应字段,那条路也不存在。
- **GitHub 走官方 API,不用 cookie 也不爬页面。** 用户资源里有 `email` 字段,
  本人设为公开时才有值。
- **站外落地页零成本** —— 不需要认证、不烧 credit,只是普通 HTTP。

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
