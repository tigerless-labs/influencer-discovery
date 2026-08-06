# X / Twitter

**发现要认证,取单个人不一定。** 匿名 API 通道 2023 年已封,但资料页本身还开着:
不带 cookie 取 `x.com/<handle>` 返回 200,Open Graph 标签里有显示名、handle 与 bio 文本;
**没有外链、没有粉丝数、没有推文**。`twitter.com` 与 `x.com` 返回同一份。

从话题找到人这一步,匿名做不到。

## 已确定的

- 浏览器 cookie(`auth_token` + `ct0`)喂给 **twscrape**,现取现用,用一次性 db,
  不建凭据存储。**twikit 过不了 X 的反爬握手**,同一份 cookie twscrape 能返回实时结果。
- 本机 Chrome 有 `auth_token` + `ct0`(已登录)。
- **搜索能从话题找到人** —— 认证之后发现能力是完整的。
- 用户资料对外只有 `description`(bio)与 `url` 两个字段。

## 待探索

搜索的翻页上限与速率限制,以及被判定自动化的阈值。
