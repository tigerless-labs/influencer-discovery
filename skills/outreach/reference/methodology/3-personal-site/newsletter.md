# Newsletter

目标表里第二大的渠道。**先认托管方 —— 它决定用哪条路,差别是一次请求和五次请求。**

认托管方**不能只看根页字符串**,会误判;拿托管方自己的接口证伪(打一次 Substack 的
`/api/v1/archive`,不是 200 就不是 Substack)。

## 入口

**Substack 自己开着两个免费入口,都不需要种子以外的东西。**

### 类目接口 —— 冷启动,目录型

```
substack.com/api/v1/categories                     全部类目与 id
substack.com/api/v1/category/public/<id>/all?page=N  每页 25 个刊物,带 more 翻页标志
```

每条记录直接带刊物名、subdomain、自定义域、**作者真名与 handle**、bio。
按类目定向,不需要任何种子。

**邮箱字段形同虚设** —— 记录里那两个邮箱字段几乎全空,地址要靠下面 feed 那一跳。

### 推荐图 —— 定向扩张,搜索型

```
<刊物域名>/api/v1/recommendations/from/<publication_id>
```

返回的不是链接,是**被推荐刊物的完整对象**。实测一跳扩张七倍多,每个都带作者真名与 handle。
只覆盖 Substack 内部,跨托管方不成图。

### 赞助位市场这条入口是死的

验过二十家,**「有公开目录」与「给联系方式」从不同时出现**。
Passionfroot 的目录要账号,handle 只有历史链接一个来源,而那批六成已 404。

## 拿联系方式

### Substack:平台上拿不到邮箱,只能走自定义域名

**feed 里已经没有 `<webMaster>` 了。**(2026-08-06 复验,十个刊物零命中。)
它的 JSON 接口也一个邮箱字段都不给。**这个平台上不存在直接取邮箱的路。**

那些接口给的是**身份**:作者真名与 handle 可以直接取,不必从页面猜。
判重的键 `(人, 平台)` 因此在这个平台上最扎实。

拿邮箱只剩一条:**记录里的自定义域名走[第二跳](../_shared/landing-page-two-hop.md)**,
没有自定义域名的刊物到此为止。

### Ghost:Content API 的 settings 端点

Ghost 的 Content API key 明文写在首页源码里,**这是给前端用的公开只读 key**。

```
/ghost/api/content/settings/?key=<key>    support / members / default 三个地址
/ghost/api/content/authors/?key=<key>     作者的 name / bio / website,email 恒为 null
```

**成色比 Substack 差一档,必须按值过滤**:`noreply@` 直接丢,`@ghost.io` 按平台转发地址
同等对待。样本还太小,当作补充路径而不是主路。

### beehiiv 与其余

**beehiiv 的 `<webMaster>` 填的是它自己的支持地址**,有值但不算数 ——
不能因为字段非空就采信。它的 API 要 key,页面里不明文带,没有 Ghost 那样的公开镜像。

WordPress、Buttondown、静态站生成器在 feed 里一个都不填。这些退回到站点本身:
和 Blog 相反,**newsletter 的邮箱更多在子页而不是首页**。`/advertise` 这类招商入口
只有零星几个站有,拿到之后还要过 [seller-vs-buyer.md](../_shared/seller-vs-buyer.md)。

再拿不到就退回第二跳,见 [landing-page-two-hop.md](../_shared/landing-page-two-hop.md)。
**第二跳的发射台优先用结构化字段**:Substack 作者 profile 的外链数组、
Ghost 作者的 `website` —— 都比解析页面便宜。

**每封邮件的页脚**也带联系方式,但那要求订阅 —— **不订阅**,那是写操作,
且会把本项目的身份暴露给目标。

## 判断:个人 newsletter 还是媒体产品

这个区分决定拿到的地址算不算数:

- **个人 newsletter** —— 作者本人的地址,算数。
- **媒体化 newsletter**(有编辑部、有 rate card)—— 拿到的是面向职能的地址。
  **对赞助投放有用,对个人 outreach 不算数**,见
  [landing-page-two-hop.md](../_shared/landing-page-two-hop.md) 的「不算数的东西」。

## 停止语义

**两种,按入口分开记。** 类目接口是**目录型**——翻到 `more` 为假就是枚举完了,是事实边界;
推荐图和站点搜索是**搜索型**,靠连续无新。混在一起记就看不出哪一路还值得投。

## 去重的键

`(newsletter 名, Newsletter)`。

注意同一个人可能既有 newsletter 又有 YouTube 频道 —— 那会落成**两行**,这是设计接受的
代价(方向安全,人看得见),不是 bug。

## 边界

- 大牌 newsletter 的 rate card 常要填表单才给,**不填表单**——那是写操作。
- 不猜测个人邮箱 —— 目标表里已有的 contact note 自己写着这句。
- **公开接口并发一高就限流**,串行加间隔;被限流的返回长得不像 404,别误判成「没有」。
- **历史链接不能直接复用。** 表里指向赞助位市场的那批已经大面积失效。

## 待验证

- Ghost 那条路的实际命中率 —— 样本太小,写进主路之前要补。
- beehiiv 刊物页有没有固定的作者落点。
- 推荐图第二跳的新增率与饱和点 —— 「连续无新」的阈值现在还没有实测依据。
- 类目接口的翻页上限与各类目总量。
