# ② 项目范围界定、CLI 开发工作流与首个原型

状态：alpha（课节完整）

来源：OpenFDE ✖️ 观猹 FDE 共学营第 2 课，全长 02:38:24。[原课程](https://openfde.net/zh/resources/guancha-fde)。

## 学习结果

将一条模糊诉求变成有条件、有边界的 SOW，并通过 SPEC、原型与演示证据证明一条核心路径。

## 来源与边界

Lyon 主讲，张青等嘉宾参与答疑；部分姓名存在字幕异写，人物信息以原课程介绍为准。

以下案例按授课时的介绍呈现，案例效果未经本校独立审计。工具能力与招聘信息在使用时核对官方来源。课程训练完成与真实生产交付分别记录。

## 课节

按目标选课；缺少背景时只补相关节点。下列教学内容均已落为独立课节，进入对应节点时再读取。

| 节点 | 文件 |
|---|---|
| 传统 to B 交付链路与 FDE 铁三角 | `../lessons/scope-cli-prototype/01-tob-to-fde.md` |
| 线索判断与需求诊断 | `../lessons/scope-cli-prototype/02-lead-qualification.md` |
| SOW：范围、验收与可控变更 | `../lessons/scope-cli-prototype/03-sow.md` |
| CLI 工作流：从 SOW 到可运行原型 | `../lessons/scope-cli-prototype/04-cli-workflow.md` |
| 三个交付案例：数据闭环与可复用能力 | `../lessons/scope-cli-prototype/05-three-cases.md` |
| Demo、MVP 与交付移交 | `../lessons/scope-cli-prototype/06-demo-to-handover.md` |

## 原课内容覆盖

- 传统 to B 链路、角色与铁三角
- 线索、案例、关键人与需求诊断
- SOW、量化口径、变更与验收
- CLI 开发、小步验证、项目指导文件
- 素材、内容矩阵与银行客服三例
- Demo/MVP、付款经验边界、移交与复用

## 练习与原课作业

原课提供的实践方向是：认领业务命题、写 SOW、用 CLI 开发工作流做核心流程 Demo。本校的模拟报销实验是配套练习，不是原项目复刻。

## 完成证据

- 责任与诊断图，事实和假设分开；
- SOW、SPEC 与一项承诺对应的实际运行证据；
- 案例迁移、失败路径、演示脚本与移交说明；
- 证据卡，真实客户条件与未验证项分别记录；

## 实施条件与降级

技术练习可使用 `references/lab-guide.md` 的本地模拟环境；配套规则、数据与脚本由本校设计，不冒称复刻讲师系统。无法运行、缺少真实反馈或只有手工演练时，节点按 `references/state-schema.md` 记为 `blocked`、`simulated` 或保留未验证项。文件与演练可继续积累，不能提前写成真实接入或生产效果。

非技术学习者由导师执行命令、学生负责预测与核对。讲授、练习、证据核对均在主对话进行；每个节点完成后保存产物与进度，由学生决定下一步。
