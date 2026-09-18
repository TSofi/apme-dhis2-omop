# APME Project 2 — Public Health Data Pipeline (DHIS2 + OMOP CDM)

Course project for **Advanced Programming in Medicine**, FH Technikum Wien, WS2026.
Group 2: Sofia, Ahmer, [Member C], [Member D]

## Overview

We configure a DHIS2 tracker program for a public health use case (proposed: immunization), fill it with patient-level data, transform that data into the OMOP Common Data Model with an ETL pipeline, and run standardized analytics on the result.

```
DHIS2 (tracker program + sample data)
   → extraction (DHIS2 export / Web API)
   → ETL (source-to-OMOP mapping)
   → OMOP CDM database
   → analytics (SQL cohort queries / ATLAS)
```

## Standards and platforms

| Component | Choice |
|---|---|
| Source system | DHIS2 |
| Target data model | OMOP CDM (OHDSI) |
| Database | PostgreSQL |
| ETL | Python |
| Analytics | SQL cohort queries |

## Repository structure

```
docs/            project plan, sprint documentation, mapping documentation
etl/             ETL scripts (DHIS2 → OMOP)
sql/             OMOP schema and analytics queries
config/          DHIS2 metadata exports and setup files
```

## Documentation

- [Project plan and team roles](docs/PROJECT_PLAN.md)
- [Sprint 1 — Discovery](docs/sprint-1.md)

## Team

| Member | Main area |
|---|---|
| Sofia | Database & SQL, tracker program configuration, documentation |
| Ahmer | Python, data export and ETL pipeline |
| [Member C] | Setup & infrastructure |
| [Member D] | Mapping documentation, testing, final report |
