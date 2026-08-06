# 免认证

纯 HTTP 或官方免费接口就能取到,不需要登录态、不烧 credit。

覆盖 YouTube、Newsletter、Blog、Website、Podcast、Passionfroot、Paved、GitHub、
Hacker News、DEV.to、Product Hunt、Medium,以及任意站外页面。

## 已确定的

**YouTube** —— 频道的 `/about` 页,简介正文与链接区**都在初始 HTML 里**,
不需要执行 JS、不需要 key。About 页那个联系方式按钮由登录与 reCAPTCHA 保护,
匿名响应里只有它的占位标记、没有地址;官方 Data API 的频道资源里也没有对应字段。
链接区的地址是站内跳转形式,真实地址在查询参数里。

**Podcast** —— Apple 的公开搜索接口按关键词返回节目,**每条结果自带 feed 地址**,
免 key、免 cookie。feed 是标准 RSS,`<itunes:owner>` 里带邮箱是 Apple 收录规范的要求。

**GitHub** —— 走官方 API,不用 cookie 也不爬页面。用户资源里有 `email` 字段,
本人设为公开时才有值。带 token 与不带的速率差约两个数量级(核心接口 5000/h 对 60/h,
搜索 30/min 对 10/min)。

**公布的配额不是唯一的墙。** 列仓库那类接口有一道**次级限流**:核心配额还剩大半时就会
被拒,而**配额查询接口显示一切正常**。触发后同一批接口一起被拒,恢复要等核心配额重置。
并发是触发条件。

**Medium** —— 资料页、about 页、标签页对无浏览器的客户端一律 403;
`medium.com/feed/@<user>` 开着,是文章 RSS,不含资料页的 bio 与外链。

**Passionfroot** —— 创作者页 `passionfroot.me/<handle>` 公开且服务端渲染;
发现入口 `/discover` 要账号,sitemap 里没有创作者页。**没有公开目录。**

**Paved** —— 刊物页对爬虫直接 429,浏览器可读但关键数字被遮、无联系方式;
目录页要登录。

**聚合页** —— linktr.ee 的外链在初始 HTML 里,不需要浏览器;beacons.ai 拒爬虫。

**站外页面零成本** —— 不需要认证、不烧 credit,只是普通 HTTP。
约二十分之一的站会拒绝声明身份的爬虫(403/429)。

## 待探索

- **YouTube 官方 Data API 的免费配额**能不能承担「已知频道 → 简介与链接」的富化,
  从而只在发现阶段抓页面。
- **播客 feed 之外的目录**(Podcast Index 之类)能否直接查到 feed 地址。
- **赞助位市场之外的同类站点**有没有公开可翻的目录。
- **DEV.to、Hacker News、Product Hunt** 的公开接口形态,尚未探。
