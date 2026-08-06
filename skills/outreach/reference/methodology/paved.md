# Paved

赞助位市场,和 [passionfroot.md](passionfroot.md) 同一类,**但偏向 newsletter 而非
个人创作者**。目标表里 `paved.com/sites/<slug>` 的行几乎全是 newsletter,
且 `Type` 多为 `Paid Channel`。

机制、停止语义、判重与 Passionfroot 相同,**这里只写不同的地方。**

## 不同一:目标多是媒体产品,不是个人

Paved 上挂的大量是媒体化的 newsletter——有编辑部、有 rate card。拿到的入口对应的是
**广告位预订**,不是某个人。

这决定了它的用途:

- **要做赞助投放** —— 这是最直接的一路,页面上就有位置、档期、报价。
- **要做个人 outreach** —— 这条渠道给的东西大多**不算数**,
  见 [landing-page-two-hop.md](landing-page-two-hop.md) 的「不算数的东西」。

目标表里已有的 contact note 自己写着这句区分:「适合付费投放,不是个人 outreach」。
**开跑前先确认本轮要的是哪一种**,否则会往表里灌一批发不出个人邮件的行。

## 不同二:一个出版方多个刊物

同一家出版方在 Paved 上会挂多份 newsletter,各是一个 slug、一行——目标表里已经能看到
这种成串出现的形态。

它们是**不同的行**(不同的刊物、不同的受众、不同的投放位),不是重复。
但它们的联系方式往往指向同一个人或同一个 `sponsor@` 地址。

**这正是设计文档说的按联系方式去重会误合并的场景。** 判重只看 `(人, 平台)`,
所以这些行会正常保留——记在这里是为了让人看到成串的行时不误以为是 bug。

## 不同三:平台列填什么

同 Passionfroot:平台列填**人所在的地方**(Newsletter / Website),不填 Paved。
市场是发现他的地方,不是他所在的地方。

## 待验证

- 同 [passionfroot.md](passionfroot.md):**「翻到底」成立与否取决于目录的可翻范围**,
  那是取数层的问题。
- 站点页上有没有指向 newsletter 本体域名的链接——有的话能接上
  [newsletter.md](newsletter.md) 那条路去找真正的个人联系方式。
- 与 Passionfroot 的重合度。
