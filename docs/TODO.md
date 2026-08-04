# TODO

- [x] 写 `docs/design/index.md` 与首批设计文档:流水线八阶段、身份、分层、Sheet 契约。
- [ ] 确定 repo 边界:是通用触达系统,还是只服务某一个产品的推广?这决定渠道 adapter 要不要
      按产品分层。(与 `liruihan000/reachout_list` 的关系一并厘清——那个是 cost-xray 专用的
      手工清单,是并入还是各管各。)
- [ ] 核对 Sheet 各 tab 的列语义,逐列判定机算/人填并写进配置;这是 sheet-contract 落地的前提。
- [ ] 清理整列默认值污染:先查清哪些列被刷满,再定「真实行」的判定口径。
- [ ] 三张主表各有一份状态列,需合并为单一状态机;确定事件从哪些列推导。
- [ ] Target List 的稳定键缺失——现在以显示名为事实上的键。补平台原生标识符。
- [ ] 实现 Sheet 读写模块,先对副本跑通再碰正式表。
- [ ] 补 `docs/testing.md` 与测试映射。
- [ ] 补 `dev_skills/index.md`,把取 token 的步骤从 README 抽成 skill。

## 待确认

- Sheet 目前共享设置是「任何人有链接即可编辑」,任何拿到链接的人都能改。表属 removed@example.invalid,
  需与其确认是否收紧。

## 参考件的处置

`build-partnership-tracker`(外部 skill,管谈成之后的点击跟踪与结算)不整包引入,理由与
缺陷见评估结论。值得移植的是 manifest → 校验 → 物化 的三段式与其校验严格度。
两个已知缺陷若要复用其代码需先修:归档内夹带真实联系人邮箱;硬编码 origin 只被替换了一半,
会静默指向他人账号下的域名。
