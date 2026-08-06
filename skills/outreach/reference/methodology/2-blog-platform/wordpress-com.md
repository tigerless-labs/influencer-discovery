# WordPress.com

**这一档里体量最大的平台,已跑通。** 免 key、免登录,一次请求同时拿到作者身份、
他自己的域名,以及通往一个免 key 邮箱源的钥匙。

## 用标签流发现人,作者对象随文章内联

```
GET https://public-api.wordpress.com/rest/v1.1/read/tags/<tag>/posts?number=40
```

每篇里的 `author` 给 `name`、`nice_name`、`URL`(他自填的网址)、`profile_URL`;
篇级另有 `site_URL` 与 `site_name`。**不必逐个查资料页。**

- **`author.email` 恒为 `false`** —— 这条路上平台自己不给邮箱。
- 一次 120 篇里有 86 个不同作者,**重复率不高,翻页值得**。
- **约四成作者的 `site_URL` 是自定义域名**,直接就是[第二跳](../_shared/landing-page-two-hop.md)的落点;
  其余留在 `*.wordpress.com` 子域上。

## Gravatar 一跳给邮箱

`nice_name` 就是 Gravatar 的用户名,资料页有公开 JSON,免 key:

```
GET https://gravatar.com/<nice_name>.json
```

- **约七成的名字取得回**,其余 404。
- 取得回的里面**约两成带 `emails`**(`[{primary, value}]`),是本人主动设为公开的地址,
  不是猜出来的 —— 符合[只用主动公开的联系方式](../_shared/landing-page-two-hop.md)那条。
- 另有 `accounts`(twitter / linkedin / youtube 之类)与 `aboutMe`,作为社交兜底与身份佐证。
- **没有 `urls` 字段可依赖**,外链要回到 `author.URL` 与 `site_URL`。

端到端:**每八个作者里约一个,在两次免 key 请求内拿到邮箱**,不进第二跳。

## 停止语义

搜索型 —— **连续无新**。

## 去重的键

`(author.nice_name, WordPress.com)`。`nice_name` 是平台内唯一且稳定的,
比显示名可靠 —— 显示名里大量是自动生成的乱码。

## 待验证

- **样本质量。** 标签流是最新流,肉眼可见混着大量垃圾账号,和 DEV.to 上
  「默认排序的作者七成零互动」是同一个病。**有没有带互动或时间窗的排序参数,还没找。
  这是这一份最要紧的一条** —— 没有它,发现量大但卖买比例会很难看。
- Gravatar 那两成的 `emails` 只在一个标签的三十个名字上测过,换垂类会不会掉。
- 自定义域名那四成走完第二跳的净增,没测。
