# 第三方供应商

名录。只记**能力、网址、收费方式、实验记录**。

**不比价、不排序、不推荐** —— 那要看用途,归
[../methodology/cost-ranking.md](../methodology/cost-ranking.md)。这里连单位换算都不做:
原样记收费方式,谁划算由用途去算。

全部按量付费。有月费的一律不用,见 [index.md](index.md)。

## 名录

| 供应商 | 覆盖 | 收费方式 | 实验记录 |
|---|---|---|---|
| ScrapeCreators | 20+ 平台 | $47 / 25,000 credits;$497 / 500,000 credits。**缓存命中免费** | ✅ Instagram、TikTok |
| SociaVault | 25+ 平台,credits 永不过期 | $29 / 6,000 credits;$79 / 20,000 credits | ✅ TikTok |
| LamaTok | TikTok 专属 | $0.001 / 请求,$50 / $100 / $300 有阶梯折扣 | ⬜ 账户无额度,待充值或后台领取 |
| Bright Data | 通用抓取 | $0.0015 / 条,每月免费 5,000 条 | ⬜ 待在控制台建 zone |
| TikHub | 16 平台,**含小红书 / B站 / 微博 / 知乎 / 快手 / 微信** | $0.001–0.01 / 请求 | ⬜ 未注册 |

## 网址与认证

凭据变量名见 [index.md](index.md#凭据)。

| 供应商 | base | 端点清单 | header |
|---|---|---|---|
| ScrapeCreators | `https://api.scrapecreators.com` | `openapi.json`(175 个) | `x-api-key` |
| SociaVault | `https://api.sociavault.com/v1/scrape/` | `llms.txt` | `X-API-Key` |
| LamaTok | `https://api.lamatok.com` | `/openapi.json`(23 个) | `x-access-key` |
| Bright Data | — | — | `Authorization: Bearer` |

两份端点清单都在各自的 docs 域下,免费可取。

## 独有能力

- **SociaVault `/tiktok/demographics`** —— 受众国家分布。按量提供受众画像的只此一家,
  别家这类数据都在月费产品里。
- **ScrapeCreators 缓存命中免费** —— 重复取同一批对象不再扣费。

## 探测不扣费

SociaVault 的余额端点 `/v1/credits` 与参数错误的请求都不扣 credit,可以放心探。

## 一条跨供应商的事实

**TikTok 拿 bio 要多付一次调用,换供应商消不掉这一次。**

bio 本身拿得到 —— `profile` 端点给 `signature` 与 `bioLink`。消不掉的是那次调用:
搜索只返回 handle,每个人都得单独再查一次。

ScrapeCreators 与 SociaVault 的搜索响应是 TikTok 内部接口的原始转发,结构完全相同,
`signature` 一律为空。任何包装该接口的服务都是同一个结果 —— **平台的响应结构决定的,
不是选型问题。** 除非某家不直接转发、自己做了富化,目前没有一家验证过。

## 未跑通的还差一条能力确认

LamaTok 的 profile 端点**返不返回 `signature` / `bioLink` 未知**。充值后第一件事是验它 ——
不返回的话它就只是个视频接口,覆盖那一栏要改写。
