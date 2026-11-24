# Structured output: Pydantic

When a script uses JSON from an API or a model, say what it must look like and check it before using it. On failure, print only the errors and fix only those fields.

```python
from pydantic import BaseModel, HttpUrl, ValidationError

class Repo(BaseModel):
    name: str
    stars: int
    url: HttpUrl

bad = []
for i, row in enumerate(rows):
    try:
        Repo.model_validate(row)
    except ValidationError as e:
        bad.append((i, [(".".join(map(str, x["loc"])), x["msg"]) for x in e.errors()]))
print(bad or "all valid")   # e.g. [(3, [('stars', 'Input should be a valid integer'), ('url', 'Field required')])]
```

Read `bad`, repair those rows, and re-check. Do not regenerate or re-read the rows that passed.
