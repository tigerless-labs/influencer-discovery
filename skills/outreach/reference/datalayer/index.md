# 数据层

**每个平台的能力边界 —— 与用途无关。** 能取到什么、取不到什么、要什么凭据、代价多少。
换个人拿它去做选品、做舆情、做招聘,这一档照样能用。写法见 [CLAUDE.md](CLAUDE.md)。

一份公开可访问的,其余每个平台一份;供应商是另一个轴,单独一份。

- [public.md](public.md) —— 免认证:纯 HTTP 或官方免费接口
- [providers.md](providers.md) —— 第三方供应商名录:能力、网址、收费方式、实验记录
- [instagram.md](instagram.md) —— 第三方 API,**已跑通**
- [tiktok.md](tiktok.md) —— 第三方 API,**已跑通**
- [mastodon.md](mastodon.md) —— **无认证**,发现与取数都免 key
- [threads.md](threads.md) —— 匿名到资料页;发现要过审的官方 API 或第三方
- [linkedin.md](linkedin.md) —— cookie,发现这一步不存在
- [twitter-x.md](twitter-x.md) —— cookie,匿名只到 bio
- [reddit.md](reddit.md) —— cookie,`rdt` CLI,已验证

## 凭据

**全部住 `~/.config/outreach/.env`,`chmod 600`。** 不进 repo、不进日志、不进 reference。
代码只按变量名读,路径只出现在配置里。

| 变量名 | 供应商 | 状态 |
|---|---|---|
| `SCRAPECREATORS_API_KEY` | ScrapeCreators | 已跑通 |
| `SOCIAVAULT_API_KEY` | SociaVault | 已跑通 |
| `LAMATOK_API_KEY` | LamaTok | 未跑通,待充值 |
| `BRIGHTDATA_API_TOKEN` | Bright Data | 未跑通,待建 zone |

余额、命中率这类会漂的运行时数值不写在这里 —— 查 `/v1/credits` 一类的余额端点,
或看运行报告。文档只写不随一次调用改变的事实。

**不要借用 `~/.config/last30days/.env`。** 那是另一个项目的凭据文件;共用会让任何一方的
key 轮换静默打断另一方。

## 三条共同事实

**cookie 不落盘** —— 要用时现从浏览器 cookie DB 读,值只在进程内存里活。
落盘就得自己管过期、加密、同步、泄漏面。本机 Chrome 可直接解密,无 keyring 阻塞。

**浏览器可用,但取数不靠它。** 本机 Chrome 扩展已配对,能开标签页、读页面文本。
实测它的用途是**分清「爬虫看不到」和「真的没有」** —— 对被拒的站点,
它买回的是访问权,不是页面上原本就没有的东西。按域名逐个授权,只能串行。

**服务端 filter 普遍不存在** —— 粉丝数、地区、垂类都没有服务端筛选。但搜索结果自带
`follower_count`,**客户端筛不额外花钱**。唯一的例外是 Instagram:
它的检索词吃 bio 文本本身,筛选条件可以写进 query。

## 一条排除规则

**有月费的一律不用。** Modash、HypeAuditor、CreatorDB、Janney AI 全部排除。
只接受按量付费、官方免费接口、自建。

## 两类凭据,来路不同

**买来的 key** 住 env 文件,人填一次,过期要人换。

**登录态不落 env。** 它是用户浏览器里已经有的东西,现取现用:X 的会话 token 要从浏览器
读出来交给取数工具;Reddit 的 CLI 自己就从浏览器取,外部拿不到也不需要拿。
**两者都不写进任何文件、不进日志。**

**登录态不是配置项,是用户当下的状态** —— 浏览器里有就有,没有就没有,填不进 env。

读浏览器 cookie 要一个额外的库。
