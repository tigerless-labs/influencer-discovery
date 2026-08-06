# 免认证

纯 HTTP 或官方免费接口就能取到,不需要登录态、不烧 credit。

覆盖 YouTube、Newsletter(Substack / Ghost)、Blog、Website、Podcast、DEV.to、WordPress.com、
Micro.blog、Gravatar、Hashnode、freeCodeCamp News、HackerNoon、GitHub、Medium、
Passionfroot、Paved、Hacker News、Product Hunt,以及任意站外页面。

**这里列的平台与调用方做不做无关。** 边界是平台的属性;某个平台在调用方那边被裁决
不跑,它的边界仍然住在这里。

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

**DEV.to** —— 公开 API 免 key、免登录。文章列表端点**内联作者对象**,
一次请求拿到作者 handle、`website_url` 与互动数,不必逐个查资料页。
按 tag 取,单页上限 100 篇。**排序参数决定样本质量**:默认是最新流,
带时间窗的热门排序才拿得到有互动的作者。

**Substack** —— 刊物域名下与主站都有公开只读端点,无鉴权:
类目端点返回全部类目与 id,类目下的刊物列表**每页固定条数、带翻页标志**,
记录里含刊物名、子域、自定义域、作者真名与 handle。
另有按刊物 id 取推荐刊物的端点,返回被推荐刊物的**完整对象**。
**这些 JSON 端点一个邮箱字段都没有**;刊物的回信地址在它 RSS 的 `<webMaster>` 里。
**并发一高就限流**,失败返回长得不像 404。

**WordPress.com** —— `public-api.wordpress.com` 的阅读器接口免 key、免登录。
按标签取文章,**每篇内联作者对象**(名字、稳定的用户名、他自填的网址、Gravatar 资料页地址)
与篇级的站点地址、站名。**作者对象里的 `email` 字段恒为 `false`。**
默认按时间倒序,**没找到按互动或时间窗排序的参数**。

**Gravatar** —— 用户名后缀 `.json` 即公开资料,免 key。给显示名、简介、位置、
社交账号列表(twitter / linkedin / youtube 之类),**以及本人主动设为公开时的 `emails`**
(`[{primary, value}]`)。**没有可依赖的 `urls` 字段**;不存在的用户名返回 404。

**Micro.blog** —— 发现页是 JS 模板,同路径下的 `posts/discover` 是标准 JSON Feed,
免 key。一次 50 条,每条的 `author` 给显示名、**他自己的站点地址**与平台用户名。
**没有邮箱字段。** 翻页参数未探。

**Bear Blog** —— 发现页对声明身份的爬虫返回质询页(403),没有免浏览器的路。

**Tumblr** —— 官方标签接口要 API key,匿名 401。免认证面:标签页 HTML 一次 7 个博客,
**时间游标参数无效**,返回逐字节相同;每个博客的旧版 JSON 端点仍免 key,
只有七个字段,其中自定义域名与 feed 两项在 10 个抽样上**全空**;每博客 RSS 无任何作者或邮箱标签。
页面里嵌着一个匿名 bearer token,拿它可以翻页 —— **那是绕开 key 闸,不是免认证面。**

**write.as** —— 阅读站的 feed 免 key,一次 88 条 / 49 个博客,`author` 恒为博客标题而非人。
翻页在阅读站自己的路径下,**整个公开面约 150 篇的滚动窗口**,标签页几乎是空的,没有公开目录。
每个博客有免 key 的 JSON(含终身浏览量)与 ActivityPub actor(**无 attachment,故无联系字段**)。
**限流很紧**:2 秒间隔下三次之后即 429。

**Hashnode** —— **GraphQL 端点已撤**:任何请求都 301 到一份公告页,
**带不带 token 都一样**;旧的 `api.hashnode.com` 主机 404。平台自述读写都要刊物开 Pro。
剩下的免认证面是 HTML:标签页服务端渲染,一页约 20 个作者 handle;
资料页也服务端渲染,给社交外链与自有域名,**没有本人邮箱**。

**freeCodeCamp News** —— 站点跑在 Ghost 上但**不暴露 Content API 的只读 key**。
免认证面是标准 sitemap:作者子图**一次返回全部作者页地址、不翻页**(当前 559 条)。
作者页服务端渲染,给自有域名与社交外链,**没有邮箱字段**。
RSS 一次只有 10 条且 `dc:creator` 为空。

**HackerNoon** —— RSS 免 key,一次 20 条,`dc:creator` 带作者名,文章链接里含作者 handle。
**资料页与任何 `/api/` 路径对声明身份的爬虫返回质询页(403)**;sitemap 可读。

**Ghost** —— Content API 公开可读,**只读 key 以 `data-key` 明文写在站点首页源码里**。
`settings` 端点给站点的几个对外地址,`authors` 端点给作者的名字、简介与网址,
**其中的邮箱字段恒为空**。

**域名注册信息(RDAP)** —— 免 key 的标准 JSON 查询。**只覆盖 `.com/.net/.org`**,
`.io` `.me` `.co` 与各国后缀一律查不到。**必须串行**,并发即被限流。
返回里注册商的隐私转发地址与真实注册人地址混在一起。

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
- **Hacker News 与 Product Hunt** 的公开接口形态,尚未探。
- **WordPress.com 有没有非时间序的排序**,以及 **Micro.blog 的翻页与话题取法**。
- **Substack 类目端点的翻页上限**与各类目总量。
- **Ghost 那条路的站点覆盖面** —— 只在极少数站上验过。
