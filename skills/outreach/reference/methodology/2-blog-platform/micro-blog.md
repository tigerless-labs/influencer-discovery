# Micro.blog

**入口已验证,产出未测。** 平台的发现页是 JS 模板,真正可取的是它背后的 JSON Feed,
免 key、免登录:

```
GET https://micro.blog/posts/discover
```

一次 50 条,`items[].author` 给 `name`、`url`、`_microblog.username`。
50 条里有 40 个不同作者。

**`author.url` 就是他自己的站**,平台不用猜归属 —— 这一档里少见的确定性绑定。
其中一部分是自定义域名,其余落在 `*.micro.blog` 子域上;
两者都按[第二跳](../_shared/landing-page-two-hop.md)走。

平台上没有邮箱字段,这条路的产出全部来自第二跳。

## 去重的键

`(_microblog.username, Micro.blog)`。

## 待验证

- **翻页与话题。** 只取过一次首屏 50 条,能不能往回翻、能不能按 tagmoji 或话题取,没试。
- 自定义域名的占比,以及走完第二跳的邮箱命中率。
- 这批人的卖买比例 —— 整档共同的缺口,见 [index.md](index.md)。
