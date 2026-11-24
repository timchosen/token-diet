# JSON and API replies: jq

Save the reply, look at its shape, then pull out only the fields the task needs.

```bash
curl -s "https://api.github.com/repos/BurntSushi/ripgrep" -o /tmp/r.json
jq -c 'if type=="array" then (.[0]|keys) else keys end' /tmp/r.json      # shape, one line
jq '{name, stars: .stargazers_count, language}' /tmp/r.json              # only what you need
jq -r '.items[] | [.name, .price] | @tsv' /tmp/list.json                 # rows as a small table
jq 'length' /tmp/list.json                                               # count, not contents
```

Never `cat` a JSON file to find out what is in it.

Settings in `config.json` under `jq`: `max_rows` is the most rows to print from a reply. They override the numbers above.
