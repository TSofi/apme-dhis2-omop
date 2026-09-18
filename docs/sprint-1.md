# Sprint 1 — Discovery

**Goal:** project setup, technology stack selection, DHIS2 installation and tracker program configuration.
**Due:** next lecture, 6 October 2026.

## Tasks

| Task | Owner | Status |
|---|---|---|
| Agree on the use case | All | in progress |
| Create the GitHub repository | Sofia | done |
| Set up the repository structure | Sofia | done |
| Install DHIS2 | [Member C] | to do |
| Configure the organisation units | Sofia | to do |
| Create the data elements and tracked entity attributes | Sofia | to do |
| Create the tracker program and its program stages | Sofia | to do |
| Explore how data can be exported from DHIS2 | Ahmer | to do |
| Read the OMOP CDM basics (key tables) | [Member D] | to do |

## Technology stack

| Layer | Choice | Reason |
|---|---|---|
| Source system | DHIS2 | Required by the project topic |
| Deployment | Docker | Reproducible setup across team machines |
| Target data model | OMOP CDM | Required by the project topic |
| Database | PostgreSQL | Standard choice for OMOP CDM implementations |
| ETL | Python | Team experience; suitable for data processing |
| Analytics | SQL | Cohort queries against the OMOP database |

## Results

*To be filled in as the sprint progresses.*

- **DHIS2 installation:** version, method, problems encountered
- **Tracker program:** name, org units, attributes, program stages, data elements
- **Data export:** available formats and endpoints

## Open questions for the lecturer

- Local DHIS2 installation or a shared instance?
- Which OMOP CDM version?
- Is a subset of OMOP tables enough?
- Is ATLAS required, or are SQL cohort queries enough?
