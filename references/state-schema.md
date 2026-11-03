# 学习存档结构

默认文件：`~/.openfde-school/me.json`。

```json
{
  "schema_version": "1.0",
  "handle": "me",
  "last_seen": "2026-11-03",
  "current_course": null,
  "current_lesson": null,
  "ability_profile": {
    "business": "unknown",
    "engineering": "unknown",
    "ai_tooling": "beginner",
    "delivery": "unknown"
  },
  "learner_profile": {
    "field": null,
    "role": null,
    "goal": null,
    "daily_tools": [],
    "analogy_mode": "ask",
    "working_analogies": [],
    "failed_analogies": []
  },
  "courses": {},
  "current_project": null,
  "evidence": [],
  "unverified": [],
  "questions": [],
  "next_recommended": null,
  "log": []
}
```

## 学习者背景

开课前的简短开场用来填这一段，学生可以拒答或随时修改。

```json
{
  "field": "会计 | 外贸 | 电商运营 | 前端开发 | 在校学生 | null",
  "role": "学生在这个领域实际干的活，一句话",
  "goal": "求职 | 接单 | 理解行业 | 已有企业场景",
  "daily_tools": ["他每天真在用的软件或系统"],
  "analogy_mode": "ask | on | off",
  "working_analogies": [
    { "concept": "SOW", "analogy": "外贸里的形式发票", "verified_by": "学生自己复述正确" }
  ],
  "failed_analogies": [
    { "concept": "evals", "analogy": "期末考试", "reason": "学生反而以为评测只在交付前做一次" }
  ]
}
```

- `analogy_mode` 为 `ask` 时只在类比是否合适会影响讲法时询问；`on` 表示愿意使用本行业类比；`off` 表示使用标准术语。不要为填写这个字段增加开场问卷。
- `working_analogies` 只记录**学生自己复述正确过**的类比，没验证过的不写。
- `failed_analogies` 同样重要：类比误导过学生就必须记下来，后面的课不许再用。
- 这一段只存学习相关背景，不存单位名称、职务、同事姓名、客户信息或任何可定位到具体个人与企业的内容。

## 课程记录

```json
{
  "status": "available | in-progress | paused | completed",
  "lessons": {
    "lesson-id": {
      "status": "not-started | in-progress | completed | simulated | blocked",
      "comprehension": "unknown | shaky | working | solid",
      "artifacts": [],
      "evidence": [],
      "failures": [],
      "unverified": []
    }
  }
}
```

## 写入规则

- 更新前读取现有合法 JSON，保留不认识的字段；先写同目录临时文件，解析成功后原子替换，再重新读取确认。存档损坏时保留原文件，不把它当作新生存档覆盖。
- 多份存档存在时由学生选择；handle 仅作文件名，拒绝路径分隔符和 `..`。
- 课节 ID 使用相对路径（如 `fde-landscape/01-what-is-fde`），与课程文件中的入口对应。迁移旧存档时保留原 ID 与证据，不重新判定完成。
- 不记录 API Key、账号密码、客户原始数据、企业机密、完整隐私信息或未经授权的内容。
- 未真实运行的实验只能标 `simulated` 或 `blocked`。
- 学生可以随时要求查看、修改或删除存档。
- 没有统一学分、必修课或总完成率；每门课独立记录。
