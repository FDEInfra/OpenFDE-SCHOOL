# ③ Skills 的企业实践

状态：alpha（课节完整）

来源：OpenFDE ✖️ 观猹 FDE 共学营第 3 课，全长 02:00:51。[原课程](https://openfde.net/zh/resources/guancha-fde)。

## 学习结果

把一段工作经验封装为可调用、可评测、能说明边界的 Skill，并设计真实采用与反馈办法。

## 来源与边界

雾明主讲，瑞分享在职 FDE 的现场工作；身份按授课时介绍。

以下案例按授课时的介绍呈现，案例效果未经本校独立审计。工具能力与招聘信息在使用时核对官方来源。课程训练完成与真实生产交付分别记录。

## 课节

按目标选课；缺少背景时只补相关节点。下列教学内容均已落为独立课节，进入对应节点时再读取。

| 节点 | 文件 |
|---|---|
| Skill：经验封装与渐进式加载 | `../lessons/skills-in-enterprise/01-skill-basics.md` |
| 创建方法：输出、输入、步骤与评测 | `../lessons/skills-in-enterprise/02-authoring-method.md` |
| 两个案例：文章解读与系统预审 Skill | `../lessons/skills-in-enterprise/03-two-case-demos.md` |
| 工程化：脚本、动态知识与状态管理 | `../lessons/skills-in-enterprise/04-engineering-and-state.md` |
| Skill 评测：失败样本与反馈迭代 | `../lessons/skills-in-enterprise/05-evals-and-feedback.md` |
| 现场工作：从单个 Skill 到可复用交付 | `../lessons/skills-in-enterprise/06-field-work-and-reuse.md` |

## 原课内容覆盖

- Skill、提示词、三种来源与渐进加载
- 输出反推输入、隐性知识与步骤设计
- 文章解读、CLI 包装两个案例
- 脚本、静态/动态知识、自由度与状态
- 评测、bad case、优化与反馈
- 现场三阶段、RAG/NL2SQL、产品反哺与培训

## 练习与原课作业

逐字稿未记录群内发布的具体作业题。创建 Skill、评测与采用计划为本校设计的练习，不标为原课作业。

## 完成证据

- 选题与输出/输入/步骤设计；
- 一个真实存在的 Skill，3 次调用或清楚标记的手工演练；
- 不少于 6 条有期望的评测记录与改动比较；
- 资源/状态设计、复用与采用计划、证据卡；

## 实施条件与降级

技术练习可使用 `references/lab-guide.md` 的本地模拟环境；配套规则、数据与脚本由本校设计，不冒称复刻讲师系统。无法运行、缺少真实反馈或只有手工演练时，节点按 `references/state-schema.md` 记为 `blocked`、`simulated` 或保留未验证项。文件与演练可继续积累，不能提前写成真实接入或生产效果。

非技术学习者由导师执行命令、学生负责预测与核对。讲授、练习、证据核对均在主对话进行；每个节点完成后保存产物与进度，由学生决定下一步。
