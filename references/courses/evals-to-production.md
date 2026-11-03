# ⑤ Evals 与从 Demo 到企业生产

状态：alpha（课节完整）

来源：OpenFDE ✖️ 观猹 FDE 共学营第 5 课，全长 01:54:11。[原课程](https://openfde.net/zh/resources/guancha-fde)。

## 学习结果

为最小应用建立覆盖与判定方式，运行回归、定位过程失败，并提出有证据的试点或暂缓建议。

## 来源与边界

Derrick 主讲企业应用评测，陈宏分享 MemU 与服务落地；身份按授课时介绍。

以下案例按授课时的介绍呈现，案例效果未经本校独立审计。工具能力与招聘信息在使用时核对官方来源。课程训练完成与真实生产交付分别记录。

## 课节

按目标选课；缺少背景时只补相关节点。下列教学内容均已落为独立课节，进入对应节点时再读取。

| 节点 | 文件 |
|---|---|
| “发顺丰”四幕：把失败变成可定位的问题 | `../lessons/evals-to-production/01-shunfeng-four-acts.md` |
| 评测驱动开发：MVP 契约与决策留痕 | `../lessons/evals-to-production/02-evaluation-driven-development.md` |
| 评测集：四类任务与五个覆盖维度 | `../lessons/evals-to-production/03-eval-set-and-coverage.md` |
| 过程评估：工具轨迹与受控故障 | `../lessons/evals-to-production/04-traces-and-failure-injection.md` |
| 评估器、回归与测试集迭代 | `../lessons/evals-to-production/05-graders-and-regression.md` |
| 从 Demo 到生产：影子运行与发布门槛 | `../lessons/evals-to-production/06-production-gates.md` |
| 记忆与持续服务：可见进度和预期管理 | `../lessons/evals-to-production/07-memory-and-service.md` |

## 原课内容覆盖

- 发顺丰四幕、局部修复与全局回归
- EDD、MVP 契约与决策留痕
- 四类任务、五维覆盖、专家与合成样本
- 过程轨迹、诊断题、故障注入与权限边界
- 代码/人/模型评估器、回归与评测集迭代
- 影子运行、人工辅助、发布门槛与总成本
- 记忆需求、变化管理与持续客户沟通

## 练习与原课作业

逐字稿未给出本课专属的新作业题。本校的用例集、故障诊断与发布决策是教学设计；不将课堂经验百分比用作统一验收门槛。

## 完成证据

- 五项 MVP 契约与决策记录；
- 不少于 10 条有效用例，含四类任务、期望、来源与判定方式；
- 故障与当前版本两份报告、过程诊断与回归结论；
- 发布决策、记忆边界、周报与证据卡；

## 实施条件与降级

技术练习可使用 `references/lab-guide.md` 的本地模拟环境；配套规则、数据与脚本由本校设计，不冒称复刻讲师系统。无法运行、缺少真实反馈或只有手工演练时，节点按 `references/state-schema.md` 记为 `blocked`、`simulated` 或保留未验证项。文件与演练可继续积累，不能提前写成真实接入或生产效果。

非技术学习者由导师执行命令、学生负责预测与核对。讲授、练习、证据核对均在主对话进行；每个节点完成后保存产物与进度，由学生决定下一步。
