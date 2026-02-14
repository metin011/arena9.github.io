**Alembic Migration Guide**

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Ensure `DATABASE_URL` or `SQLALCHEMY_DATABASE_URI` is set. Example for local sqlite (optional):

```powershell
# $env:DATABASE_URL = 'sqlite:///football_stats.db'
```

3. Initialize alembic (only if you haven't created `alembic/` directory). This repo already contains `alembic/` config. To create an initial revision run:

```powershell
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

Notes:
- The alembic `env.py` uses `DATABASE_URL` env var if present, otherwise falls back to value in `alembic.ini`.
- For Postgres on Render: set `DATABASE_URL` in environment; the `env.py` will convert `postgres://` -> `postgresql://` if needed.
