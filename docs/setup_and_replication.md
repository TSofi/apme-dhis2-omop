# Reproducibility and Replication Guide

## 1. Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Dependencies: pip install pandas psycopg2-binary faker requests sqlalchemy

## 2. Infrastructure Setup
Run the OMOP PostgreSQL container:
docker run -d --name omop-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=omop -p 5433:5432 --restart unless-stopped postgres:16-alpine

Apply OMOP CDM v5.4 Schema DDL:
Get-Content ./sql/omop_cdm_v5_4_ddl.sql -Raw | docker exec -i omop-postgres psql -U postgres -d omop

## 3. Running the Pipeline
Run the end-to-end automated orchestrator:
python scripts/orchestrator.py
