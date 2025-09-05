# Alembic Directory Structure and Integration

Alembic migration scripts are stored in:

	app/models/migrations/

The Alembic configuration file is located at the project root:

	alembic.ini

This setup keeps all database migration logic close to your models for consistency and easier maintenance. The `script_location` in `alembic.ini` is set to `app/models/migrations` to ensure Alembic uses the correct folder.

**Summary:**
- Migration scripts: `app/models/migrations/versions/`
- Alembic config: `alembic.ini` (root)
- Models: `app/models/models.py`

All migration and upgrade commands should be run from the project root using the `-c alembic.ini` flag.
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


This will create a `migrations/` folder under `app/models/`:

```
alembic init app/models/migrations
```

## 3. Configure Alembic

- Edit `app/models/migrations/env.py` to set your SQLAlchemy `Base` and database URL.
- Example for FastAPI project:

```
from app.core.database import Base
# ...existing code...
target_metadata = Base.metadata
```

## 4. Create a Migration

To generate a migration after updating your models:

```
alembic -c alembic.ini revision --autogenerate -m "Initial migration"
```

## 5. Apply Migrations

To apply migrations to your database:

```
alembic -c alembic.ini upgrade head
```

---

Add these instructions to your README for easy reference.
