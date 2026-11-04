# 共建 OpenFDE School

<p><strong>简体中文</strong> &nbsp; | &nbsp; <a href="CONTRIBUTING.en.md">English</a></p>

欢迎补齐课程事实、改进练习、修复安装问题，也欢迎提交你的第一份学习证据。

## 从一个具体问题开始

- **课程卡点、事实错误与失效链接**：使用[课程反馈](https://github.com/FDEInfra/OpenFDE-SCHOOL/issues/new?template=course-feedback.yml)，注明课程、课节、预期与实际表现。
- **学员里程碑**：先创建[加入学员墙 Issue](https://github.com/FDEInfra/OpenFDE-SCHOOL/issues/new?template=join-wall.yml)，按 [WALL.md](WALL.md) 的格式新增自己的一行。
- **课程或实验改进**：PR 中说明学习者遇到的具体问题、修改后的行为，以及真实验证结果。较大课程调整先用 Issue 说明目标与范围。

## 内容标准

每个课节应有讲授、动作、可检查产物与验收条件。实验无法运行时，说明纸面替代路径，并把实际接入保留为未验证。

保留原课程的事实、讲师归属和引用边界。补充外部材料时附官方或一手来源，快速变动的信息标注核查日期。文件变动同步维护 `manifest.json` 的文件清单。

提交可公开的脱敏材料。客户信息、个人联系方式、凭证和未授权内容留在自己的环境；案例公开前确认授权。课程训练、模拟实验与真实企业交付分别记录证据。

## 提交前验证

在仓库根目录运行（Python 3.9+）：

```bash
python3 scripts/validate_school.py
python3 scripts/validate_wall.py
python3 scripts/validate_lab.py
python3 scripts/validate_install.py
```

安装器测试需要 Git；本地 HTTP 实验需要允许监听回环端口。有 PowerShell 7 时，安装器测试会同时验证 PowerShell 版本；CI 在 Windows 和 Linux 上执行对应检查。

涉及导师行为时，按[入学、选课与续学验证](references/learning-flow-checks.md)进行真实会话验证，并在 PR 记录结果。其它改动由 GitHub Actions 复核；未运行的项目如实标注。

## 许可

贡献沿用 [LICENSE](LICENSE) 中相应文件的许可：课程 Markdown 为 CC BY-NC-SA 4.0，代码与自动化为 MIT。
