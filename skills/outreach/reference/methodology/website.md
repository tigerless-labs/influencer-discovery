# Website

公司站或产品站。**和 Blog / Newsletter 的根本区别:这里拿到的地址多半不属于某个人。**

目标表里这一档大量是 `Contact Method = Contact Form`,不是 `Email`——这不是抓取失败,
是这类站点本来就只提供表单。

## 入口

**搜索型**,但更多是**被动的**:website 这一档的行大多不是搜出来的,是从别的渠道
(GitHub 项目、LinkedIn、文章署名)顺过来的落点。

把它当独立的发现渠道产出很低;当作**第二跳的终点**才是它真正的角色,
见 [landing-page-two-hop.md](landing-page-two-hop.md)。

## 拿联系方式

```
/contact   /contact-us   /about   /team   /company   /imprint   /legal   /privacy
```

- **`/team` 与 `/about`** —— 找具体的人。有的团队页直接给每个人的邮箱或 LinkedIn。
  **这是这一档唯一能产出「某个人的联系方式」的地方。**
- **法务页**(privacy / terms / imprint)—— 常被忽略,但按法规必须列一个可达的联系方式。
  表里已有的 contact note 里出现过好几次「隐私政策列 …@…」「ToS 列 …@…」。
  **命中率被低估的一路。**
- **contact 表单** —— 记下表单 URL 作为联系方式,**不填**。填表单是写操作,不在范围内。

## 面向职能的地址:这里是唯一的例外

`info@` / `sales@` / `contact@` 通则上不算数
(见 [landing-page-two-hop.md](landing-page-two-hop.md))。**本渠道是唯一的例外**:
目标本身就是公司或产品(`Type = Competitor` / `Partner` / `Engineering Team`)时,
那本来就是对外入口,算数。

判据只有 `Type` 列。目标是某个人就退回通则 —— 这是本渠道最容易出错的一处。

## 停止语义

作为第二跳终点时**没有停止语义**——它不是发现渠道,不产生候选,只解析已有的落点。
真把它当发现渠道跑时,是搜索型,靠连续无新。

## 去重的键

`(公司或产品名, Website)`。

同一个站点下住着不同的人时(创始人、CTO、官方账号),它们是**不同的行**,不是重复。
地址条目只用来省重复抓取,不参与判重。

## 边界

- 表单不填。
- 反爬邮箱(图片、JS 拼接)不破。
- 大公司站抓不到人是常态,不是失败——记 log,进不了表就算了。

## 待验证

- 法务页(privacy / terms / imprint)相对 `/contact` 的实际命中率。表里的 contact note
  暗示它不低,但没统计过。
- `/team` 页在目标表现有的 62 行 website 上有多少直接给个人邮箱。
- 「面向职能的地址」按 `Type` 分流的规则,在历史行上回放一遍是否与人的判断一致。
