# reference/scripts —— 数据层的验证探针

## 要解决的

数据层每句边界断言都要求「挂证据链回」(见 datalayer/CLAUDE.md)。现在证据是
`data/experiments/2026-08-06/` 下一堆无 docstring、名字随手起(`rule.py`、`sl.py`、`graph.py`)、
且 `data/` 全目录 gitignore 的脚本 —— 跟着一次实验生死,下次想复验一条边界没有可跑的东西。

把**能复验边界的那类脚本**提升成版本化工具,住 `skills/outreach/reference/scripts/`。

## 边界:哪些脚本进来,哪些不进

**只进「能力探针」** —— 一次性验证某条平台边界是否仍成立的脚本,不属于流水线。
例:「IG `/v1/instagram/search/profiles` 对两词 query 是否仍 500」「Threads 搜索是否仍不给
`follower_count`」。它的产出是一句判定,回填对应数据层文件的正文或「待探索」。

**不进流水线逻辑的副本。** 实测 `data/experiments/.../reddit-raw/` 里的脚本已被 `src/` 覆盖:
`rcook.py` = `session.rdt_cookie_header()`;`prof.py` 的 `social_link` 正则 = `channels/reddit.py`
的 `SOCIAL_LINK_BLOB`。搬这些进来就是第二份权威源,违反「代码是实现的唯一权威」与 DRY。
**这类脚本不迁移,git 历史留证即可。**

## 探针要满足的

- **凭据不硬编码。** 要 cookie 就 `import` `src/outreach/session.py`,不再写死 `/home/ryan/...`。
  探针复用流水线的取数入口,不自己拼。
- **产出不落 repo。** 探针打印判定与计数,**不写抓取样本、不写联系人数据**进 `reference/`。
  reference 全目录版本化,不是 `data/`。
- **一个探针一条边界**,文件名即所验证的边界。

## 与两份写作规约的关系

- **datalayer 自包含不破。** datalayer 正文仍不链任何外部文件(含 `../scripts/`)——
  脚本是「怎么试出来的」,按 datalayer/CLAUDE.md「只记结论」本就不进正文。探针靠
  `reference/scripts/index.md` 自己被发现,不靠数据层正文引用。
- **methodology 也不链。** 同理,机制不进 methodology。

## 单元与验收

1. **建 `reference/scripts/` 与其 `index.md`**,写清「只放能力探针、不放流水线副本、产出不落 repo」。
   验收:目录存在,index 讲明纳入标准。
2. **逐条边界补探针**(按需,不一次做完)。每加一个:数据层对应断言旁挂一句「探针见
   `scripts/<name>`」的引用形式待定 —— 若违反 datalayer 自包含,则改由 index 汇总,不在正文链。
   验收:跑一次探针,输出的判定与数据层正文一致。

## 悬而未决 —— 需要裁决

- **数据层正文能不能出现「探针见 scripts/x」这一句?** datalayer/CLAUDE.md 禁止链外部文件。
  两个选项:(A) 一律不链,探针只在 `scripts/index.md` 里按平台归档(保自包含);
  (B) 给数据层开一个「验证入口」例外,允许链 `../scripts/`。**倾向 A** —— 自包含是数据层
  能被搬走复用的前提,不该为验证便利破掉。
- **动手时机。** 主 checkout 有并行 session 正在重写 `src/outreach/channels/*` 并新增
  平台测试。探针 `import session` 安全,`import channels` 会撞 —— 等那批落地再补渠道探针。
