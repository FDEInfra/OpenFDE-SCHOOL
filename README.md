# OpenFDE School · FDE 学校

<p align="center">
  <a href="https://github.com/Alan-Youngzhe/OpenFDE-School/stargazers"><img src="https://img.shields.io/github/stars/Alan-Youngzhe/OpenFDE-School?style=flat-square" alt="stars"></a>
  <img src="https://img.shields.io/badge/version-0.1.0%20alpha-orange?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/Claude%20Code-skill-000?style=flat-square&logo=anthropic&logoColor=white" alt="claude code skill">
  <img src="https://img.shields.io/badge/courses-7-blue?style=flat-square" alt="7 courses">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0%20%2B%20MIT-green?style=flat-square" alt="license"></a>
</p>

一所由 Agent 亲自带学的 FDE（Forward Deployed Engineer，前线部署工程师）学校。不是文档合集，而是导师在主对话里讲清原理，带你在真实业务场景里观察、定义问题、沉淀 Skill、建立评估集，直到你能独立完成一次可验收的交付。

内容蒸馏自 **OpenFDE ✖️ 观猹 FDE 共学营**（[官网课程页](https://openfde.net/zh/resources/guancha-fde)），覆盖从行业全景、需求挖掘、范围界定、Skills 实践、系统打通、Evals 到求职创业的完整链路。

适合想入行 FDE 的零基础学习者，也适合已经在做企业 AI 交付、想补齐方法论的从业者。

## 理念

- **全选修**——编号对应共学营课次，是稳定 ID，不代表必修顺序；按你的目标选课
- **真实操**——每节课都有真实实验和可检查的产物：观察记录、SOW、Skill、评估集，不接受"Agent 说完成就算完成"
- **学完有证据**——本地学习存档记录每个节点的完成证据、未验证项和下一步
- **随时打断**——学生随时可以提问，答完回到主线

## 课程

| ID | 课程 | 内容 | 状态 |
|---|---|---|---|
| ① `fde-landscape` | FDE 全景与企业需求挖掘 | 从 Palantir 到 OpenAI，五方玩家全景，需求热力图 | alpha |
| ② `scope-cli-prototype` | 项目范围界定、CLI 开发工作流与首个原型 | 写出能签字的 SOW，用 CLI 跑通首个原型 | beta |
| ③ `skills-in-enterprise` | Skills 的企业实践 | 把企业最佳实践沉淀成可复用的 Skill | beta |
| ④ `cli-enterprise-integration` | CLI 打通企业内部系统 | 让 Agent 接上真实企业系统完成读写 | beta |
| ⑤ `evals-to-production` | Evals 与从 Demo 到企业生产 | 评估集先行，从 Demo 走到生产级 | beta |
| ⑦ `demoday` | 结营与优秀项目 Demo Day | 5 个真实学员项目与评委点评，校准完成标准 | beta |
| ⑧ `fde-career` | 加餐：FDE 求职、作品集与创业路径 | 简历四信号、真假 FDE 岗鉴别、独立 FDE 商业模式 | beta |

## 怎么开始

先用 CC Quick Installer 安装并验证 Claude Code，再安装 OpenFDE School。装好之后它就是 Claude Code 里的一个命令：**`/fde`**。不需要记住仓库地址，也不需要打开任何文件。

## 下次怎么继续上课

打开 Claude Code，输入：

```text
/fde
```

就这一个命令。导师会读取你的学习存档，告诉你上次学到哪、已经有哪些证据，然后接着往下讲。

也可以在后面带上你想做的事：

- `/fde 继续` —— 接上次的进度
- `/fde 带我看课程` —— 重新看课程目录
- `/fde 什么是 FDE` —— 直接进入对应课程
- `/fde 我想接企业的单子` —— 让导师帮你推荐从哪开始

学习存档保存在你电脑的 `~/.openfde-school/me.json`，换台电脑需要把这个文件一起带过去。

### 推荐：直接让 Claude Code 安装

打开 Claude Code，把下面整段发给它：

```text
请先运行 git --version 检查 Git；没有就帮我安装并验证。
然后把 https://github.com/Alan-Youngzhe/OpenFDE-School.git
安装到 ~/.claude/skills/fde。
如果目录已经存在，先检查本地修改，不要覆盖；只有干净的 Git 仓库才执行 git pull --ff-only。
最后运行 python3 ~/.claude/skills/fde/scripts/validate_school.py 验证，并告诉我真实输出。
```

### macOS / Linux 一行安装或更新

```bash
curl -fsSL https://raw.githubusercontent.com/Alan-Youngzhe/OpenFDE-School/main/scripts/install.sh | bash
```

### Windows PowerShell 一行安装或更新

```powershell
irm https://raw.githubusercontent.com/Alan-Youngzhe/OpenFDE-School/main/scripts/install.ps1 | iex
```

只从本仓库官方地址运行脚本；想先检查内容时，打开对应脚本链接阅读后再执行。安装器不会覆盖本地修改：目标目录不是 Git 仓库或存在未提交变化时会停止。

### 验证并入学

1. 新开一个 Claude Code 会话（已经开着的会话不会识别新装的命令）；
2. 输入 `/fde`，或直接说"带我学 FDE"；
3. 确认导师展示课程目录、并问你一两句你是做什么的，而不是只回答一段通用 FDE 介绍；
4. 更新时重复运行同一个安装命令，再检查 `manifest.json` 版本。

## 学员墙

完成任意一项里程碑（第一次业务观察、第一份 SOW、第一个 Skill、第一个评估集、第一次 Demo、第一次真实交付），先创建"加入学员墙" Issue，再向 [WALL.md](WALL.md) 提交 PR，留下证据和一句话复盘。

## 与共学营的关系

本校是共学营内容的**学习化蒸馏**，不是替代。共学营的小作业、大作业、评选、奖品与面试直通属于当期活动机制；本校把作业要求保留为练习设计，不承诺证书或奖品。想获得完整体验，请到[官网课程页](https://openfde.net/zh/resources/guancha-fde)观看原视频。

## 项目结构

```
SKILL.md            教务处：导师的工作规则与课程路由
manifest.json       版本与文件清单
references/
  catalog.md        课程目录
  pedagogy.md       教学法细则
  courses/          7 门课程的教案
  lessons/          各课程的具体课节与实验
  lessons/shared/   安全与证据卡等共享节点
WALL.md             学员墙
```

## 状态

Alpha (v0.1.0)。第 ① 门课已完成 lesson 化，其余课程为可教大纲（beta），持续迭代中，欢迎 Issue 和 PR。

## 许可

- 课程 Markdown：[`CC BY-NC-SA 4.0`](https://creativecommons.org/licenses/by-nc-sa/4.0/)，允许署名、非商业、相同方式共享的学习与改编；
- 代码与自动化：MIT；
- 共学营原始内容与第三方材料仍遵循各自许可，见 [references/sources.md](references/sources.md)。

完整边界见 [LICENSE](LICENSE)。
