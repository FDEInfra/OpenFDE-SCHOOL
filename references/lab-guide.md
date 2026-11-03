# 本地企业实验：报销预审与人工复核

本实验是学校设计的教学配套，使用 12 条虚构报销记录和一份模拟制度。它展示确定性规则、HTTP API、CLI、Skill 和评测之间的关系，不调用模型、不连接企业账号、不审批或付款。规则通过率只能描述本实验，不能用作真实财务准确率。

## 运行位置与准备

以下命令从 OpenFDE School 仓库根目录执行。需要 Python 3.9 或更高版本；无第三方依赖、无需账号或付费。导师先确认当前目录包含 `assets/enterprise-lab/lab.py`。学生安装在只读目录时，将学校目录复制到可写的练习目录再执行。

生成的文件保存在 `work/`，不属于分发清单。初始化拒绝覆盖已有目录；重复练习时选择新的工作目录，并同步修改后续命令中的路径。

```bash
python3 assets/enterprise-lab/lab.py --help
python3 assets/enterprise-lab/lab.py init --workspace work/expense-demo
```

在 `work/expense-demo/state.json` 查看虚构记录。金额使用整数分；50000 分为 500 元。`training-only` 是公开的教学标记，不是生产密码。

## 先在离线状态下跑评测

```bash
python3 assets/enterprise-lab/lab.py eval --workspace work/expense-demo --variant boundary-bug --output work/baseline.json
python3 assets/enterprise-lab/lab.py eval --workspace work/expense-demo --output work/current.json
```

第一条刻意使用错误的金额边界，预期退出码为 1，结果为 10/12；第二条预期退出码为 0，结果为 12/12。两个失败应为 C002 和 C011，它们的金额恰好等于限额。退出码 2 表示文件、参数或环境等执行错误，不能算成业务评测不通过。

这两个版本由同一程序选择，用于学习如何识别回归。学生不能把选择预置正确版本写成自己修复了代码；自主修改和新增用例应另外留 diff 与运行记录。

## 启动本机模拟系统

在一个终端运行：

```bash
python3 assets/enterprise-lab/lab.py serve --workspace work/expense-demo --port 8765
```

保留该终端。在另一个终端回到同一仓库根目录，设置公开的教学标记后查询。

macOS / Linux：

```bash
export FDE_LAB_TOKEN=training-only
python3 assets/enterprise-lab/lab.py list
python3 assets/enterprise-lab/lab.py precheck --id E003
```

Windows PowerShell：

```powershell
$env:FDE_LAB_TOKEN = 'training-only'
python assets/enterprise-lab/lab.py list
python assets/enterprise-lab/lab.py precheck --id E003
```

缺少或错误标记返回 HTTP 401，未知单号返回 404。E003 超出限额 1 分，应为 `manual_review`，规则为 `over_limit`。E004 缺少票据，应为 `needs_info`。输出里的 `approval` 与 `payment` 始终为 `false`。

## 进行一次受控写入

由导师展示预审结果与写入影响：只新增一条模拟复核建议，报销原单不变，不发生审批或付款。学生确认练习意图后，在 `work/review.json` 保存：

```json
{
  "decision": "manual_review",
  "rule": "over_limit",
  "policy_version": "training-1"
}
```

```bash
python3 assets/enterprise-lab/lab.py write-review --id E003 --payload work/review.json --idempotency-key demo-E003-v1 --confirm-training-write
python3 assets/enterprise-lab/lab.py reviews
```

第一次应返回 201。同样的请求与幂等键再次执行返回 200，`replayed` 为 `true`，复核记录仍只有一条。相同键配不同内容、同一制度下同一单据换键再写，均返回 409。省略确认参数会在 CLI 发请求前停止。服务端还会独立核对写入标记、当前制度和结果，不能只靠 Skill 提醒。

幂等键表示同一个业务动作，不应每次重试都随机生成。这个实验在单进程内串行处理写入；它不能证明多副本、高并发、数据库事务或跨系统补偿已经解决。

## 包装为 Skill

参考 `assets/expense-precheck-lab/SKILL.md`。它是教学模板，适配到学生自己的项目时要记录实验目录，让 Agent 通过 `--help` 发现命令，并把制度放在业务参考中。只有打开模拟 API 后，自然语言调用才可能产生真实工具执行记录；仅复述规则不能记成 Agent 接入成功。

## 证据与故障定位

保留以下文件：SOW、SPEC、离线评测报告、CLI 实际输出、`work/expense-demo/audit.jsonl`、写入前后复核列表，以及一次失败定位记录。每项标明“本地模拟”。

| 现象 | 优先检查 | 不能得出的结论 |
|---|---|---|
| 连接失败 | 服务是否运行、端口与终端目录 | 模型判断错误 |
| 401 | 当前终端的教学标记 | 系统数据为空 |
| 409 | 幂等键、重复记录、制度版本与预审结果 | 可以直接重写或放行 |
| 评测退出码 1 | 报告中的失败用例与期望 | 环境一定坏了 |
| 评测退出码 2 | 文件路径、JSON 格式与参数 | 业务通过率为 0% |

修改制度文件后重启模拟服务，重新运行评测。结束时在服务终端按 Ctrl+C 停止；需要重新开始时选择新工作目录，保留旧证据供比较。

无法启动端口时仍可完成离线规则与评测，网络读写节点记为 `blocked`。没有 Python 时可手工对 12 条记录判断并对照期望，记为 `simulated`，不能填入脚本已运行。没有模型或 Agent 账号不妨碍学习，但 Skill 的自动触发与自然语言执行仍是未验证项。
