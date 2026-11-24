# Spreadsheets and data files: DuckDB

Never paste or read a CSV. Ask the file a question and read the answer.

```bash
duckdb -c "DESCRIBE SELECT * FROM 'airports.csv'"                         # columns and types
duckdb -c "SELECT count(*) FROM 'airports.csv'"
duckdb -c "SELECT iso_country, count(*) AS n FROM 'airports.csv' WHERE type='large_airport' GROUP BY 1 ORDER BY n DESC LIMIT 10"
```

Works on `.csv`, `.tsv`, `.parquet` and `.json` by file name, and globs (`'sales/*.csv'`). For `.xlsx` use `read_xlsx('file.xlsx')`. Always `LIMIT`. For a Google Sheet, export it as CSV first.

Fallback: `python3 -c` with the `csv` module printing only the aggregate.

Settings in `config.json` under `duckdb`: `limit` is the `LIMIT` on every query. They override the numbers above.
