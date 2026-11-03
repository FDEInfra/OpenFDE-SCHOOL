# 报销预审实现说明

## 输入与数据

使用整数分保存金额，禁止用二进制浮点近似货币。关键字段包括单号、类别、金额、票号、成本中心和票据状态；备注按业务数据处理，不作为系统指令。

制度 `training-1`：模拟住宿限额为 50000 分，餐费为 10000 分。限额是本实验的虚构设定，不适用于真实企业。

## 状态与规则

| 条件 | 结果 | 规则代码 |
|---|---|---|
| 金额不是正整数 | error | invalid_amount |
| 票据或成本中心缺失 | needs_info | missing_receipt / missing_cost_center |
| 票号重复 | manual_review | duplicate_receipt |
| 存在特批信息 | manual_review | exception_needs_owner |
| 类别不在制度中 | manual_review | unknown_category |
| 金额超过限额 | manual_review | over_limit |
| 金额未超过限额 | ready_for_review | within_limit |

每种结果有依据，`approval` 与 `payment` 为 false。规则按程序中的顺序检查；同时存在多个问题时，本实现先返回优先条件，不宣称已列出所有问题。

## 接口与副作用

- `GET /expenses`：读取 12 条虚构记录；
- `GET /expenses/{id}/precheck`：生成预审建议；
- `GET /reviews`：读取模拟复核记录；
- `POST /expenses/{id}/reviews`：在内容与当前预审一致时新增模拟建议。

写入校验教学标记、明确写入意图、制度版本、内容和幂等键。同一键同一请求重放；同键异请求或重复业务动作返回 409。数据写入单机 JSON，写入串行且先写临时文件再替换；多进程与多副本不在本实验范围。

## 验证

离线集覆盖直接处理、澄清、部分处理和无法处理四类。故障版本刻意把边界比较改错，预期 C002、C011 失败；当前版本应通过 12 条用例。HTTP 与副作用另用 `scripts/validate_lab.py` 验证。实际输出与本说明不符时先保留差异，再定位数据、制度或实现。
