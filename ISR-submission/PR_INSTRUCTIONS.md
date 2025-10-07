# How to create the PR

```bash
# from the root of your repo clone
mkdir -p submission tools
cp -r submission/* your_repo/submission/
cp -r tools/* your_repo/tools/

git checkout -b chore/isr-submission
git add submission tools
git commit -m "ISR submission: fill gaps, add RUNBOOK, appendices, bib builder, env"
git push -u origin chore/isr-submission
# open PR on GitHub: compare chore/isr-submission -> main
```
