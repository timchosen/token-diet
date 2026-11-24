# Calls that sometimes fail: Tenacity

When you write a Python script that calls a network service, wrap the call so a failure retries inside the script. A failed call must not send the whole job back through the model.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10), reraise=True)
def fetch(url):
    r = httpx.get(url, timeout=30)
    r.raise_for_status()
    return r.json()
```

Retry only what is safe to repeat (reads, downloads). Do not retry a call that sends, pays or creates something unless it has an idempotency key.

In a loop over many items, save each result as it finishes, so a failure at item 80 resumes at 80.

Settings in `config.json` under `tenacity`: `attempts` is the number in `stop_after_attempt`. They override the numbers above.
