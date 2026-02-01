# Docker Setup: PostgreSQL + pgvector (for RAG)
*(Student handout — follow once, come to class ready.)*

This guide gets you:
1. PostgreSQL running in Docker
2. `pgvector` extension enabled
3. A quick **similarity search test** (so you know it works)

---

## 1) What you need (prerequisites)

### Install
1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
2. **Git** (optional, but nice)
3. A terminal:
   - Windows: PowerShell or Windows Terminal
   - Mac/Linux: Terminal

### Verify Docker is working
Run:

```bash
docker --version
docker compose version
```

If both print versions → you’re good.

---

## 2) Project folder
Create a folder and enter it:

```bash
mkdir pgvector-rag && cd pgvector-rag
```

You should end up here:
```
pgvector-rag/
```

---

## 3) Create `docker-compose.yml`

Create a file named **`docker-compose.yml`** in this folder with the following:

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: pgvector-db
    environment:
      POSTGRES_USER: raguser
      POSTGRES_PASSWORD: ragpass
      POSTGRES_DB: ragdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U raguser -d ragdb"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  pgdata:
```

### Notes
- `pgvector/pgvector:pg16` = PostgreSQL 16 with pgvector available.
- Port `5432` is the default PostgreSQL port.
- `pgdata` keeps your data even if the container restarts.

---

## 4) Start PostgreSQL
Run:

```bash
docker compose up -d
```

Check status:

```bash
docker compose ps
```

You should see `pgvector-db` **running** and eventually **healthy**.

---

## 5) Connect to Postgres (inside the container)

Open a Postgres shell:

```bash
docker exec -it pgvector-db psql -U raguser -d ragdb
```

You should now see a prompt like:
```
ragdb=#
```

---

## 6) Enable pgvector extension (one-time)
Inside `psql`, run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify it exists:

```sql
\dx
```

You should see `vector` in the extensions list.

Exit `psql` anytime with:

```sql
\q
```

---

## 7) Quick verification test (IMPORTANT)
This test proves vector storage + similarity search works.

### 7.1 Re-enter `psql`
```bash
docker exec -it pgvector-db psql -U raguser -d ragdb
```

### 7.2 Create a demo table
```sql
DROP TABLE IF EXISTS items;
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  title text,
  embedding vector(3)
);
```

### 7.3 Insert a few vectors
```sql
INSERT INTO items (title, embedding) VALUES
('doc about cats',  '[0.1, 0.2, 0.9]'),
('doc about dogs',  '[0.2, 0.1, 0.8]'),
('doc about cars',  '[0.9, 0.1, 0.1]'),
('doc about bikes', '[0.8, 0.2, 0.2]');
```

### 7.4 Run a similarity search (L2 distance)
Query vector is `[0.15, 0.15, 0.85]` (close to cats/dogs):

```sql
SELECT id, title, embedding,
       embedding <-> '[0.15, 0.15, 0.85]' AS l2_distance
FROM items
ORDER BY l2_distance
LIMIT 3;
```

✅ If you see cats/dogs at the top with smaller distances, pgvector is working.

---

## 8) (Optional but recommended) Create a vector index
For real RAG, you’ll store **hundreds/thousands/millions** of embeddings and want indexes.

### 8.1 Create an IVFFLAT index (good starter)
```sql
-- Choose cosine distance often used for embeddings
-- First, add an index using cosine ops:
CREATE INDEX IF NOT EXISTS items_embedding_ivfflat
ON items USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);
```

### 8.2 Use cosine distance operator
Cosine distance operator is `<=>`:

```sql
SELECT id, title,
       embedding <=> '[0.15, 0.15, 0.85]' AS cosine_distance
FROM items
ORDER BY cosine_distance
LIMIT 3;
```

---

## 9) Common commands students will use

### Stop containers (keeps data)
```bash
docker compose down
```

### Start again
```bash
docker compose up -d
```

### View logs
```bash
docker logs -f pgvector-db
```

### Reset everything (DELETES data)
⚠️ This removes the volume and all DB contents:

```bash
docker compose down -v
```

---

## 10) Troubleshooting

### 1) “Port 5432 is already in use”
Something else is using 5432 (maybe a local Postgres).

Fix options:
1. Stop local Postgres, OR
2. Change host port in compose:

```yaml
ports:
  - "5433:5432"
```

Then connect on port **5433** from your apps.

---

### 2) Container not healthy
Run:

```bash
docker compose ps
docker logs pgvector-db
```

If the password/user/db vars were changed after first run, wipe the volume:

```bash
docker compose down -v
docker compose up -d
```

---

### 3) “extension ‘vector’ is not available”
You likely used a plain `postgres` image.

Fix: ensure the image is:

```yaml
image: pgvector/pgvector:pg16
```

Then restart:

```bash
docker compose down
docker compose up -d
```

---

## 11) Quick checklist before class
Make sure you can do these:
1. `docker compose up -d` works
2. `docker exec -it pgvector-db psql -U raguser -d ragdb` opens psql
3. `CREATE EXTENSION vector;` succeeds
4. The similarity search query returns sensible results

If yes → you’re ready for RAG storage + retrieval tomorrow.
