# 数据层

怎么把数据取出来。一份公开可访问的,其余每个平台一份;供应商是另一个轴,单独一份。

- [public.md](public.md) —— 免认证:纯 HTTP 或官方免费接口
- [providers.md](providers.md) —— 第三方 API 各家的能力、单价、认证与验证状态
- [instagram.md](instagram.md) —— 第三方 API,**已跑通**
- [tiktok.md](tiktok.md) —— 第三方 API,**已跑通**
- [linkedin.md](linkedin.md) —— cookie,不做
- [twitter-x.md](twitter-x.md) —— cookie,随 auto-gtm 合并获得
- [reddit.md](reddit.md) —— cookie,`rdt` CLI,已验证

## 凭据

**全部住 `~/.config/outreach/.env`,`chmod 600`。** 不进 repo、不进日志、不进 reference。
代码只按变量名读,路径只出现在配置里。

| 变量名 | 供应商 | 状态 |
|---|---|---|
| `SCRAPECREATORS_API_KEY` | ScrapeCreators | 已跑通 |
| `SOCIAVAULT_API_KEY` | SociaVault | 已跑通 |
| `LAMATOK_API_KEY` | LamaTok | 未验证,账户余额为 0 |
| `BRIGHTDATA_API_TOKEN` | Bright Data | 未验证,缺 zone |

余额、命中率这类会漂的运行时数值不写在这里 —— 查 `/v1/credits` 一类的余额端点,
或看运行报告。文档只写不随一次调用改变的事实。

**不要借用 `~/.config/last30days/.env`。** 那是另一个项目的凭据文件;共用会让任何一方的
key 轮换静默打断另一方。

## 三条共同事实

**cookie 不落盘** —— 要用时现从浏览器 cookie DB 读,值只在进程内存里活。
落盘就得自己管过期、加密、同步、泄漏面。本机 Chrome 可直接解密,无 keyring 阻塞。

**browser-use 当前不可用** —— Claude 的 Chrome 扩展只装在 Default profile,
且从未配对过(`list_connected_browsers` 返回 `[]`)。

**服务端 filter 普遍不存在** —— 粉丝数、地区、垂类都没有服务端筛选。但搜索结果自带
`follower_count`,**客户端筛不额外花钱**。唯一的例外是 Instagram 的 bio 关键词搜索:
筛选条件写进 query 本身,筛掉的人根本不产生调用。

## 一条排除规则

**有月费的一律不用。** Modash、HypeAuditor、CreatorDB、Janney AI 全部排除。
只接受按量付费、官方免费接口、自建。
