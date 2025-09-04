# Alembic Migrations

Alembic is used for handling database migrations. Follow these steps to set up and use Alembic in this project:

## 1. Install Alembic

If not already installed, add Alembic to your requirements:

```
pip install alembic
```

Or add to `requirements.txt` and run:

```
pip install -r requirements.txt
```

## 2. Initialize Alembic

This will create a `migrations/` folder in your project root:

```
alembic init migrations
```

## 3. Configure Alembic

- Edit `migrations/env.py` to set your SQLAlchemy `Base` and database URL.
- Example for FastAPI project:

```
from app.core.database import Base
# ...existing code...
target_metadata = Base.metadata
```

## 4. Create a Migration

To generate a migration after updating your models:

```
alembic revision --autogenerate -m "Initial migration"
```

## 5. Apply Migrations

To apply migrations to your database:

```
alembic upgrade head
```

---

Add these instructions to your README for easy reference.
