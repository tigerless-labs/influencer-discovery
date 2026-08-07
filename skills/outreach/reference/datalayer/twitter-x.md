# X / Twitter

**发现要认证,匿名做不到。** 匿名 API 通道 2023 年已封;不带 cookie 取 `x.com/<handle>`
返回 200,Open Graph 标签里有显示名、handle 与 bio 文本,**没有外链、没有粉丝数、没有推文**。
`twitter.com` 与 `x.com` 返回同一份。从话题找到人这一步,匿名不存在。

## 已确定的

**认证走浏览器 cookie,不走密码,且取数层自己取。** `auth_token` + `ct0` 从浏览器读出、
喂给 **twscrape** 的 cookie 入口,不需要用户名密码、不需要邮箱验证码,也不需要人手动加账号 ——
账号池为空时取数层自动补一次。**twikit 过不了 X 的反爬握手**,同一份 cookie twscrape
能返回实时结果。

没登录 x.com 的浏览器里没有 `auth_token`,这份 cookie 就配不齐。

**搜索一次就给全。** `search` 返回的每条推文内联完整作者对象:

```
username · displayname · rawDescription(bio)· descriptionLinks(bio 里的外链)
followersCount · friendsCount · statusesCount · location · verified · blue
```

**不必再查资料页** —— 这是它和 Instagram / TikTok / Threads 的结构性差别,那三家的搜索
都不给粉丝数。

搜索支持 X 自己的查询语法(`lang:en`、`min_faves:` 之类),筛选条件可以写进查询本身。

同一个作者在一次搜索里会重复出现(一人多推),按 `username` 累积去重。

## 未确定的

**翻页上限、速率限制、以及被判定为自动化的阈值都没测。** cookie 属于真人账号,
触发风控的代价是那个账号,不是配额。

## 单次消耗

免费 —— 走的是账号自己的会话,不经过任何供应商。
