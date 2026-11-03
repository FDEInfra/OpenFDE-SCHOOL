# ④ CLI 打通企业内部系统

状态：alpha（课节完整）

来源：OpenFDE ✖️ 观猹 FDE 共学营第 4 课，全长 02:37:11。[原课程](https://openfde.net/zh/resources/guancha-fde)。

## 学习结果

完成本地模拟系统的一次读取、受控写回和错误定位，解释接入层、业务校验与人工责任。

## 来源与边界

主讲雾明（字幕亦有“吴明”等写法），另有百炼 CLI 与 DeskClaw 分享嘉宾；姓名与产品信息以原课程介绍为准。

以下案例按授课时的介绍呈现，案例效果未经本校独立审计。工具能力与招聘信息在使用时核对官方来源。课程训练完成与真实生产交付分别记录。

## 课节

按目标选课；缺少背景时只补相关节点。下列教学内容均已落为独立课节，进入对应节点时再读取。

| 节点 | 文件 |
|---|---|
| API、CLI 与 MCP：按任务选择接入方式 | `../lessons/cli-enterprise-integration/01-why-cli-not-mcp.md` |
| 先接认证与读取：最小可观察链路 | `../lessons/cli-enterprise-integration/02-auth-and-read.md` |
| 写入：服务端校验、幂等与责任边界 | `../lessons/cli-enterprise-integration/03-write-validation-idempotency.md` |
| CLI 与 Skill 的分工和版本边界 | `../lessons/cli-enterprise-integration/04-cli-skill-packaging.md` |
| 可靠性：状态、限流与故障定位 | `../lessons/cli-enterprise-integration/05-reliability-and-operations.md` |
| 业务翻译、平台装配与分阶段上线 | `../lessons/cli-enterprise-integration/06-business-translation-and-rollout.md` |

## 原课内容覆盖

- API/CLI/MCP 关系与接入选型
- 认证、配置与先读后写
- 业务封装、参数、服务端校验与幂等
- CLI/Skill 发现、安装与团队版本约定
- 长链路、状态、限流、测试、观测与恢复
- 百炼/DeskClaw、业务翻译、能力装配与分阶段上线

## 练习与原课作业

原课要求 Agent 接入真实或模拟企业系统，并完成一次读取或写入。本校进一步增加幂等、错误与观测练习；这些不代表真实企业部署已经完成。

## 完成证据

- 选型图与实际 HTTP 读取记录；
- 一次模拟写回、重复重放与冲突结果；
- Skill 工具调用记录，自动触发未验证时明确保留；
- 失败定位、恢复与上线计划、证据卡；

## 实施条件与降级

技术练习可使用 `references/lab-guide.md` 的本地模拟环境；配套规则、数据与脚本由本校设计，不冒称复刻讲师系统。无法运行、缺少真实反馈或只有手工演练时，节点按 `references/state-schema.md` 记为 `blocked`、`simulated` 或保留未验证项。文件与演练可继续积累，不能提前写成真实接入或生产效果。

非技术学习者由导师执行命令、学生负责预测与核对。讲授、练习、证据核对均在主对话进行；每个节点完成后保存产物与进度，由学生决定下一步。
