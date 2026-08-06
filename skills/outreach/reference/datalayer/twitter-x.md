# X / Twitter

**随 auto-gtm 合并获得,不自建。** 这一条是定的,其余待探索。

## 已确定的

- 匿名通道 2023 年已封,**没有免登录的路**。
- auto-gtm 的方案:浏览器 cookie(`auth_token` + `ct0`)喂给 **twscrape**,现取现用,
  用一次性 db,不建自己的凭据存储。**twikit 过不了 X 的反爬握手**,同一份 cookie
  twscrape 能返回实时结果。
- 本机 Chrome 有 `auth_token` + `ct0`(已登录)。
- 没有邮箱字段。`description`(bio)和 `url` 两个字段,联系方式要么在 bio 文本里,
  要么在外链的落点 —— 打通认证拿到的也只是第二跳的又一个起点。

## 为什么值得等,而 LinkedIn 不值得

X 打通认证后**发现能力是真的** —— 搜索能从话题找到人。LinkedIn 没有这一步。
