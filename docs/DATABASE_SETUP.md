# Shongoti Database Setup Guide

Shongoti supports dual database operations:
1. **SQLite (Default for Local Development & Offline Testing)**:
   - Zero-configuration required.
   - Database file created automatically under `apps/api/data/shongoti_dev.db`.
   - Used by default in `.env.example` and test runners.

2. **PostgreSQL 16.8 (Production & Concurrency Verification)**:
   - Required for race condition testing and Phase 03 tenant isolation validation.
   - Host tool: `psql.exe` (PostgreSQL 16.8).
   - Local connection string:
     ```env
     DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/shongoti
     ```

### Creating the PostgreSQL Database
```powershell
# From PowerShell with psql in PATH:
psql -U postgres -c "CREATE DATABASE shongoti;"
```

### Applying Migrations
```bash
pnpm db:migrate
```

### Checking Migration State
```bash
pnpm db:check
```
