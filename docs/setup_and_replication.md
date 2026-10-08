# Reproducibility and Replication Guide

## 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Install dependencies:
  `ash
  pip install -r requirements.txt
  `

## 2. Infrastructure Setup

### Option A: Using Docker Compose (Recommended)
`ash
docker compose -f docker-compose.omop.yml up -d
`

### Option B: Using Standalone Docker CLI
`ash
docker run -d --name omop-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=omop -p 5433:5432 --restart unless-stopped postgres:16-alpine
`

## 3. Apply OMOP CDM v5.4 Schema DDL

**Linux / macOS (Bash):**
`ash
cat sql/omop_cdm_v5_4_ddl.sql | docker exec -i omop-postgres psql -U postgres -d omop
`

**Windows (PowerShell):**
`powershell
Get-Content ./sql/omop_cdm_v5_4_ddl.sql -Raw | docker exec -i omop-postgres psql -U postgres -d omop
`

## 4. Run the Full Orchestrated Pipeline

Run the end-to-end pipeline in a single command:
`ash
python scripts/orchestrator.py
`
This automatically runs cohort generation, API ingestion, ETL conversion, vocabulary seeding, PostgreSQL loading, and data validation.
