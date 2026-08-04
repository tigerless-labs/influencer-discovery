# TODO

- [ ] 确定 repo 边界:是通用触达系统,还是只服务某一个产品的推广?这决定渠道 adapter 要不要
      按产品分层。(与 `liruihan000/reachout_list` 的关系一并厘清——那个是 cost-xray 专用的
      手工清单,是并入还是各管各。)
- [ ] 写 `docs/design/index.md` 与首份设计文档:目标状态机(候选 → 已联系 → 有回复 → 有产出)
      与分层裁决规则。
- [ ] 核对 Sheet 各 tab 的列语义,区分「代码可算」与「人填」两类列,写进 `config/sheet.toml`。
- [ ] 实现 Sheet 读写模块,先对副本跑通再碰正式表。
- [ ] 补 `docs/testing.md` 与测试映射。
- [ ] 补 `dev_skills/index.md`,把取 token 的步骤从 README 抽成 skill。

## 待确认

- Sheet 目前共享设置是「任何人有链接即可编辑」,任何拿到链接的人都能改。表属 removed@example.invalid,
  需与其确认是否收紧。
