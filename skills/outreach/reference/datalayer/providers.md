# 供应商

平台之外的另一个轴:同一个平台可以由多家供应商提供。这里只写**各家能力与价钱**,
选哪家是方法论的事(见 [../methodology/cost-ranking.md](../methodology/cost-ranking.md))。

全部按量付费。有月费的一律不用 —— 见 [index.md](index.md) 的排除规则。

## 单价

| 供应商 | 最低档 | 单价 | 备注 |
|---|---|---|---|
| LamaTok | 充值即用 | **$0.001**/请求 | TikTok 专属,$50/$100/$300 有阶梯折扣 |
| Bright Data | — | **$0.0015**/条 | 通用抓取,每月免费 5000 条 |
| ScrapeCreators | $47 / 25,000 credits | **$0.00188**/credit | 20+ 平台,**缓存命中免费** |
| ScrapeCreators | $497 / 500,000 credits | $0.00099/credit | 量大才划算 |
| TikHub | 充值 | $0.001–0.01/请求 | **16 平台,含小红书/B站/微博/知乎/快手/微信** |
| SociaVault | $29 / 6,000 credits | **$0.0048**/credit | 25+ 平台,credits 永不过期 |
| SociaVault | $79 / 20,000 credits | $0.0040/credit | |

**单价不等于成本。** 真实成本要乘上每个可触达联系方式消耗多少次调用,而那取决于端点
一次返回几个人、带不带 bio。排序见方法论。

## 认证与状态

凭据全部读自 `~/.config/outreach/.env`,变量名见 [index.md](index.md#凭据)。

**ScrapeCreators** —— `SCRAPECREATORS_API_KEY`,header `x-api-key`,
base `https://api.scrapecreators.com`。
全量端点规格 `https://docs.scrapecreators.com/openapi.json` 免费可取,175 个端点。
**没有任何服务端 filter**(粉丝数、地区、垂类都没有),但搜索结果自带 `follower_count`,
客户端筛不额外花钱。**已跑通 Instagram 与 TikTok 两条链。**

**SociaVault** —— `SOCIAVAULT_API_KEY`,header `X-API-Key`,
base `https://api.sociavault.com/v1/scrape/`。
端点索引 `https://docs.sociavault.com/llms.txt`。余额查询 `/v1/credits` 不扣费,
参数错误返 400 也不扣费。**已跑通 TikTok 两步链。**

它有 ScrapeCreators 没有的 `/tiktok/demographics`(受众国家分布)——
**唯一按量提供受众画像的**,别家这类数据都在月费订阅里。

**LamaTok** —— `LAMATOK_API_KEY`,header `x-access-key`
(用 `access-key` 或 `Authorization` 都是 401)。
base `https://api.lamatok.com`,OpenAPI 在 `/openapi.json`,23 个端点。
**未验证:账户余额为 0,返回 `InsufficientFunds`。** 宣称的 100 次免费没到账,
需要充值或在后台领取。它的 profile 端点返不返回 `signature` / `bioLink` 仍然未知 ——
这决定了它是不是 TikTok 上最便宜的一条路。

**Bright Data** —— `BRIGHTDATA_API_TOKEN`,header `Authorization: Bearer <token>`。
**未验证:`/status` 报 `can_make_requests: false`,`auth_fail_reason: zone_not_found`。**
key 本身有效,但要先在控制台建 zone(Web Scraper API 或 Web Unlocker)才能发请求。

**TikHub** —— 未注册。唯一覆盖中文平台的一家;要做中文创作者时它没有替代品。

## 一条跨供应商的事实

**TikTok 的搜索端点不返回 bio,换供应商解决不了。**

ScrapeCreators 与 SociaVault 的搜索响应结构完全相同 —— `challenge_list` / `cursor` /
`global_doodle_config` / `log_pb` / `rid` / `status_code`,这是 TikTok 自己内部搜索接口的
原始响应,两家都只是转发。两家实测 `signature` 都是 30/30 全空。

任何包装 TikTok 官方搜索接口的服务都会是同一个结果。**这是平台限制,不是选型问题。**
