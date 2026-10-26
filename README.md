# DHIS2 to OMOP CDM Pipeline

A reproducible public health data pipeline that collects patient-level immunization data in DHIS2, transforms it into the OMOP Common Data Model v5.4, validates standards conformance, and runs cohort analytics on the result.

Built for **Advanced Programming in Medicine**, FH Technikum Wien, WS2026 (Group 2).

All patient data is synthetic. No real patient information is used anywhere in this project.

```
DHIS2 Tracker  ->  Python ETL  ->  PostgreSQL / OMOP CDM v5.4  ->  SQL analytics
```

---

## Why this project

Health systems collect data in their own structures and their own codes. Research needs one common structure. The OMOP Common Data Model, maintained by the OHDSI community, is the agreed target: fixed tables, fixed columns, and every value expressed as a concept from a standard vocabulary (SNOMED, RxNorm, LOINC). Once data is in OMOP shape, the same analytical query runs against any OMOP database in the world.

This project implements that bridge end to end for a COVID-19 immunization use case: a DHIS2 tracker program as the source of truth, a Python ETL as the transformation layer, and PostgreSQL holding the OMOP CDM as the analytical target.

---

## Architecture

```
apme-dhis2-omop/
├── config/dhis2/
│   ├── docker-compose.yml              # DHIS2 2.40.3 + PostgreSQL/PostGIS containers
│   └── immunization-metadata.json      # complete DHIS2 configuration, importable in one API call
├── docker-compose.omop.yml             # PostgreSQL 16 container for the OMOP CDM (port 5433)
├── sql/
│   ├── omop_cdm_v5_4_ddl.sql           # OMOP CDM v5.4 schema (cdm)
│   └── sprint5_analytics_queries.sql   # three cohort queries
├── scripts/
│   ├── generate_cohort.py              # synthetic patient generator (Faker, Austrian locale)
│   ├── ingest_cohort.py                # bulk POST to the DHIS2 tracker API
│   ├── etl_dhis2_to_omop.py            # extract from DHIS2, transform to OMOP CSVs
│   ├── load_vocabularies_subset.py     # seed cdm.concept with the vocabulary subset
│   ├── load_omop_postgres.py           # bulk COPY of the CSVs into PostgreSQL
│   ├── validate_omop_quality.py        # conformance, integrity and plausibility checks
│   ├── sprint5_analytics.py            # run the analytics and print the results
│   ├── verify_tracker.py               # connectivity check against the DHIS2 API
│   └── orchestrator.py                 # run stages 1-6 in order
├── docs/
│   ├── dhis2-setup.md                  # DHIS2 deployment and metadata import
│   ├── setup_and_replication.md        # OMOP database setup and pipeline execution
│   ├── mapping_document.md             # source-to-target mapping with concept ids
│   ├── demo-runbook.md                 # live demonstration script
│   ├── sprint-1.md                     # sprint 1 report
│   └── progress/                       # dated status summaries
└── requirements.txt
```

---

## Quick start

### Prerequisites

- Docker and Docker Compose
- Python 3.10 or later
- About 4 GB of free RAM for the two database containers

### 1. Install Python dependencies

```
pip install -r requirements.txt
```

### 2. Start DHIS2

```
cd config/dhis2
docker compose pull
docker compose up -d
```

First start takes a few minutes while the database initialises. DHIS2 is then available at
http://localhost:8080 with the default login `admin` / `district`.

### 3. Import the DHIS2 configuration

Either through the Import/Export app (Metadata import, upload the JSON file), or through the API:

```
curl -u admin:district -H "Content-Type: application/json" \
  -d @config/dhis2/immunization-metadata.json \
  "http://localhost:8080/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE"
```

Then assign the root organisation unit to your user (Users app -> admin -> Organisation units -> Austria),
otherwise the data capture apps show nothing.

### 4. Start the OMOP database and apply the schema

```
docker compose -f docker-compose.omop.yml up -d
```

Windows PowerShell:

```
Get-Content ./sql/omop_cdm_v5_4_ddl.sql -Raw | docker exec -i omop-postgres psql -U postgres -d omop
```

macOS / Linux:

```
docker exec -i omop-postgres psql -U postgres -d omop < sql/omop_cdm_v5_4_ddl.sql
```

### 5. Run the pipeline

```
python scripts/orchestrator.py
```

---

## What each stage does

| Stage | Script | Description |
|---|---|---|
| 1 | `generate_cohort.py` | Generates synthetic patients with Austrian names, dates of birth between 18 and 80 years ago, one to three doses of a single vaccine brand, and an adverse event in roughly 8 percent of events |
| 2 | `ingest_cohort.py` | Posts the cohort to `POST /api/tracker` as one batch and reports created, updated and ignored counts |
| 3 | `etl_dhis2_to_omop.py` | Reads `GET /api/tracker/trackedEntities`, walks enrollments and events, and writes OMOP tables as CSV files into `omop_output/` |
| 4 | `load_vocabularies_subset.py` | Creates `cdm.concept` and seeds the concepts the project uses, verified against Athena |
| 5 | `load_omop_postgres.py` | Loads the CSVs with `COPY` in dependency order: location, care_site, person, drug_exposure, observation |
| 6 | `validate_omop_quality.py` | Runs the three validation layers and prints a pass or fail line for each check |

`orchestrator.py` runs all six in sequence and stops immediately if any stage exits with an error.

---

## Data model mapping

| DHIS2 | OMOP CDM | Notes |
|---|---|---|
| Tracked entity (Person) + attributes | `person` | sex becomes `gender_concept_id`, the DHIS2 UID is kept in `person_source_value` |
| Enrollment | - | used to reach the events |
| Event (Vaccination visit) | `drug_exposure` | vaccine name becomes `drug_concept_id` (RxNorm), dose number goes into `sig` |
| Adverse event flag | `observation` | linked back to the exposure through `observation_event_id` |
| Organisation unit | `care_site` | place of service 8756 |
| Country and city | `location` | one shared row |

Concept ids used:

| Source value | Concept id | Name | Vocabulary |
|---|---|---|---|
| Male | 8507 | MALE | Gender |
| Female | 8532 | FEMALE | Gender |
| Comirnaty | 37003436 | SARS-CoV-2 vaccine, mRNA-BNT162b2 | RxNorm |
| Spikevax | 37003518 | SARS-CoV-2 vaccine, mRNA-1273 | RxNorm |
| Vaxzevria | 37003432 | SARS-CoV-2 vaccine, ChAdOx1 | RxNorm |
| Adverse event | 437663 | Fever | SNOMED |
| Health centre | 8756 | Outpatient Hospital | CMS Place of Service |
| Route | 4132161 | Intramuscular | SNOMED |
| Country | 4330442 | Austria | Country |

The full mapping with target fields is in [`docs/mapping_document.md`](docs/mapping_document.md).

---

## Validation

`validate_omop_quality.py` runs three layers and fails loudly:

**1. Standards conformance.** Every `concept_id` used in the data must exist in `cdm.concept` and sit in the expected domain: Gender for `person.gender_concept_id`, Drug for `drug_exposure.drug_concept_id`, Condition for `observation.observation_concept_id`.

**2. Referential integrity.** No drug exposure or observation without a person, no observation pointing at a missing drug exposure, no person pointing at a missing care site.

**3. Clinical plausibility.** No vaccination dated before the patient's date of birth.

The script then prints an epidemiological summary resolved through the vocabulary, so the output shows concept names rather than bare numbers.

---

## Analytics

```
python scripts/sprint5_analytics.py
```

Three cohort queries, also available as plain SQL in `sql/sprint5_analytics_queries.sql`:

1. **Dose interval by brand** - mean, minimum and maximum days between dose 1 and dose 2.
2. **Safety signal** - adverse events reported per 1000 doses administered, by brand.
3. **Cohort retention** - share of the cohort reaching dose 1, dose 2 and a booster.

---

## Mobile data capture

The DHIS2 Android Capture app connects to the instance, stores data locally, and synchronises when a connection is available. This covers the realistic field case: a health worker registers a vaccination with no connectivity, and the record reaches the server later.

For a demonstration, the local instance is exposed with a tunnel, the phone is connected to that URL, and the capture is performed in airplane mode. The full sequence is in [`docs/demo-runbook.md`](docs/demo-runbook.md).

---

## Useful commands

```
docker compose logs --follow          # watch DHIS2 logs
docker compose stop                   # stop the containers
docker compose start                  # resume
docker compose down --volumes         # remove everything including the database

python scripts/verify_tracker.py      # check API connectivity and read the data back
```

Port 8080 already in use: either free it, or change `published: 8080` to `published: 8081` in
`config/dhis2/docker-compose.yml` and use http://localhost:8081.

---

## Current limitations

- The vocabulary is a curated subset seeded from verified Athena definitions, not the full Athena download. Conformance checks therefore cover the concepts this project uses.
- Adverse events are stored in `OBSERVATION`. Concepts in the Condition domain conventionally belong in `CONDITION_OCCURRENCE`.
- The source data element for adverse events is a boolean, so individual symptoms are not differentiated.
- The system runs locally. Reproducibility comes from configuration and scripts in this repository rather than from a shared database.

---

## Roadmap

| Sprint | Scope | Status |
|---|---|---|
| 1 - Discovery | Project setup, stack selection, DHIS2 deployment, tracker configuration | done |
| 2 - Data collection | Synthetic cohort generation and ingestion through the API | done |
| 3 - ETL design | OMOP schema, vocabulary subset, source-to-target mapping | done |
| 4 - ETL build | Full pipeline with orchestration and automated validation | done |
| 5 - Analytics and demo | Cohort queries, mobile offline capture, live demonstration | in progress |

---

## Learning resources

- OMOP CDM v5.4 specification: https://ohdsi.github.io/CommonDataModel/
- Athena vocabulary browser: https://athena.ohdsi.org/
- DHIS2 developer documentation: https://developers.dhis2.org/
- DHIS2 Android Capture app: https://dhis2.org/android/
