# Sprint 1 — Discovery

**Goal:** project setup, technology stack selection, DHIS2 installation and tracker program configuration.
**Due:** next lecture, 6 October 2026.

## Tasks

| Task | Owner | Status |
|---|---|---|
| Agree on the use case (immunization) | All | done |
| Create the GitHub repository and structure | Sofia | done |
| Install DHIS2 (Docker, local instance) | Sofia | done |
| Configure the organisation units | Sofia | done |
| Create the data elements and tracked entity attributes | Sofia | done |
| Create the tracker program and its program stages | Sofia | done |
| Export the configuration as importable metadata | Sofia | done |
| Register test patients to verify the configuration | Sofia | in progress |
| Reproduce the setup locally and verify the instructions | [Member C] | to do |
| Explore how data can be exported from DHIS2 (Web API) | Ahmer | to do |
| Summarise the OMOP CDM core tables | [Member D] | to do |

Each team member runs their own local DHIS2 instance; there is no shared server in this project.

## Technology stack

| Layer | Choice | Reason |
|---|---|---|
| Source system | DHIS2 2.40.3 | Required by the project topic |
| Deployment | Docker Compose | Reproducible setup across team machines |
| Target data model | OMOP CDM | Required by the project topic |
| Database | PostgreSQL | Standard choice for OMOP CDM implementations |
| ETL | Python | Team experience; suitable for data processing |
| Analytics | SQL | Cohort queries against the OMOP database |

## Results

### DHIS2 installation

Local instance on Docker (DHIS2 2.40.3 + PostgreSQL/PostGIS), available at http://localhost:8080.
The compose file is in `config/dhis2/docker-compose.yml`; the full setup procedure is in
[`docs/dhis2-setup.md`](dhis2-setup.md).

### Tracker program configuration

Use case: **immunization tracking**.

- Organisation units: Austria → Vienna → Vienna Health Centre 1 / Vienna Health Centre 2
- Tracked entity type: Person (First name, Last name, Date of birth, Sex)
- Program: Immunization Programme (`WITH_REGISTRATION`, enrol once per person)
- Program stage: Vaccination visit, repeatable (Vaccine name, Dose number, Adverse event reported)

The configuration was applied through the DHIS2 Web API (`POST /api/metadata`) and exported to
`config/dhis2/immunization-metadata.json`, so any team member can reproduce the identical setup
with a single import.

### Verification

Test patients were registered in the Capture app and read back through the tracker API:

```
GET /api/tracker/trackedEntities?orgUnit=<root>&ouMode=DESCENDANTS&program=prgImmuniz1
    &fields=attributes[displayName,value],enrollments[enrollmentDate,orgUnitName,
            events[occurredAt,dataValues[dataElement,value]]]
```

The response contains the person attributes and the vaccination event data values, which confirms
that the data is available programmatically — this is the entry point for the ETL pipeline.

## Note on sharing work

Data lives in each developer's local database, so we do not exchange database dumps.
Everything that has to be reproducible is committed as **configuration or code**:

- metadata → `config/dhis2/immunization-metadata.json` (imported via the API or the Import/Export app)
- sample data → a generator script that creates the data through the API (Sprint 2)

## Open questions for the lecturer

- Which OMOP CDM version should we target?
- Is a subset of OMOP tables enough (person, visit_occurrence, drug_exposure, condition_occurrence)?
- Is ATLAS required, or are SQL cohort queries enough?
- Is the optional FHIR intermediate step expected?
