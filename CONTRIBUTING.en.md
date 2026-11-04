# Contributing to OpenFDE School

<p><a href="CONTRIBUTING.md">简体中文</a> &nbsp; | &nbsp; <strong>English</strong></p>

Help improve course accuracy, refine exercises, fix installation issues, or share your first piece of learning evidence.

## Start with a specific problem

- **Learning obstacles, factual errors, and broken links:** use [course feedback](https://github.com/FDEInfra/OpenFDE-SCHOOL/issues/new?template=course-feedback.yml). Identify the course, lesson, expected result, and actual behavior.
- **Learner milestones:** create a [learner wall Issue](https://github.com/FDEInfra/OpenFDE-SCHOOL/issues/new?template=join-wall.yml), then add your own row using the format in [WALL.md](WALL.md).
- **Course or lab improvements:** describe the learner's problem, the resulting behavior, and actual verification results in your PR. For substantial curriculum changes, discuss the goal and scope in an Issue first.

Course materials and community forms are currently primarily in Chinese. Include the course ID and lesson path so contributors can locate the relevant material regardless of the language of your feedback.

## Content standards

Each lesson should include an explanation, an action, an inspectable artifact, and acceptance criteria. When an experiment cannot run, provide a paper alternative and leave actual integration marked as unverified.

Preserve the original course's facts, speaker attribution, and citation boundaries. Link to official or primary sources for additional material, and include the verification date for facts that change quickly. Keep the file list in `manifest.json` synchronized when adding or removing files.

Submit anonymized material that you have permission to share publicly. Keep client information, personal contact details, credentials, and unauthorized content in your own environment. Confirm authorization before publishing a case study. Record curriculum practice, simulated experiments, and real client delivery as separate kinds of evidence.

## Verify before submitting

Run from the repository root with Python 3.9+:

```bash
python3 scripts/validate_school.py
python3 scripts/validate_wall.py
python3 scripts/validate_lab.py
python3 scripts/validate_install.py
```

Installer tests require Git. The local HTTP lab requires permission to listen on the loopback interface. When PowerShell 7 is available, installer checks also test the PowerShell script. CI runs the corresponding checks on Windows and Linux.

For changes to tutor behavior, follow the [onboarding, course selection, and resumption checks](references/learning-flow-checks.md) in real conversations and record the results in your PR. GitHub Actions verifies other checks; state clearly which checks you did not run.

## Licensing

Contributions follow the applicable license in [LICENSE](LICENSE): CC BY-NC-SA 4.0 for course Markdown, and MIT for code and automation.
