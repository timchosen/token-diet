# Long command output: RTK

Put `rtk` in front of commands whose output is long: `rtk git log`, `rtk git status`, `rtk git diff`, `rtk ls`, `rtk test <test command>`, `rtk err <build command>`. It keeps the key lines and drops the rest. `rtk gain` shows what it has saved. In Claude Code, `rtk init -g` installs a hook that does this for every shell command, so nothing needs prefixing.

Fallback when rtk is missing: bound the output yourself. Send it to a file and read the end or the failures:

```bash
npm test > /tmp/test.log 2>&1; echo "exit $?"; rg -n "FAIL|Error|✗" /tmp/test.log | head -40
git log --oneline -30
```

If the short output hides what you need, read the saved log with `rg`; do not rerun the command unfiltered.
