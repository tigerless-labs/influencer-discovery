# outreach

对外触达的目标清单与流水线。交付面是一张 Google Sheet(`outreach targets target list`),
本 repo 管产生和维护它的代码、配置与设计文档。

**当前状态:脚手架。** 只有 CLAUDE.md 与配置骨架,流水线尚未实现。待办见
[docs/TODO.md](docs/TODO.md)。

## Sheet 访问

流水线读写 Sheet 用 service account 模拟取短效 token,**不落长期密钥文件**。
gcloud 自带 OAuth client 被 Google 列为未验证,直接给 ADC 加 `spreadsheets` scope 会被
「This app is blocked」拦下——所以走这条路:

```bash
# 1. 拿 ADC token(身份:server@tigerless.com)
T=$(gcloud auth application-default print-access-token)

# 2. 模拟 SA,换一个带 spreadsheets scope 的短效 token
curl -s -X POST \
  -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  -d '{"scope":["https://www.googleapis.com/auth/spreadsheets"],"lifetime":"3600s"}' \
  "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/sheets-writer@github-market.iam.gserviceaccount.com:generateAccessToken"
```

前置条件(已配好,列出以备重建):`github-market` 项目启用 `sheets` / `iam` /
`iamcredentials` API;`server@tigerless.com` 持有该 SA 的
`roles/iam.serviceAccountTokenCreator`。新建 IAM 绑定后约 30 秒传播,首次 403 属正常,重试即可。
