# DHIS2 setup and tracker program configuration

## 1. Start DHIS2

Requires Docker Desktop.

```bash
cd config/dhis2
docker compose pull
docker compose up -d
```

First start takes a few minutes while the database is initialised.
DHIS2 is then available at http://localhost:8080 — login `admin` / `district`.

Useful commands:

```bash
docker compose logs --follow    # watch the logs
docker compose stop             # stop
docker compose start            # resume
docker compose down --volumes   # remove everything, including the database
```

**Versions:** DHIS2 2.40.3, PostgreSQL with PostGIS 14.

## 2. Import the metadata

The full configuration of our use case is stored in
[`config/dhis2/immunization-metadata.json`](immunization-metadata.json).
Import it into a fresh instance in one of two ways.

**Import/Export app:** open http://localhost:8080/dhis-web-import-export/index.html →
Metadata import → upload the JSON file → Import.

**Or via the API:**

```bash
curl -u admin:district -H "Content-Type: application/json" \
  -d @immunization-metadata.json \
  "http://localhost:8080/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE"
```

After importing, assign the root organisation unit to your user
(Users app → admin → Organisation units → Austria), otherwise data capture apps show no data.

## 3. What the configuration contains

**Use case:** immunization tracking.

**Organisation unit hierarchy**

```
Austria (level 1)
└── Vienna (level 2)
    ├── Vienna Health Centre 1 (level 3)
    └── Vienna Health Centre 2 (level 3)
```

**Tracked entity type:** Person

| Attribute | Value type | Mandatory |
|---|---|---|
| First name | TEXT | yes |
| Last name | TEXT | yes |
| Date of birth | DATE | no |
| Sex | TEXT | no |

**Program:** Immunization Programme — type `WITH_REGISTRATION` (tracker program), enrol once per person, assigned to Vienna and both health centres.

**Program stage:** Vaccination visit — repeatable, one event per vaccination.

| Data element | Value type | Compulsory |
|---|---|---|
| Vaccine name | TEXT | yes |
| Dose number | INTEGER_POSITIVE | yes |
| Adverse event reported | BOOLEAN | no |

## 4. How this maps to OMOP (Sprint 3 preview)

| DHIS2 | OMOP CDM |
|---|---|
| Tracked entity (Person) + attributes | `person` |
| Enrollment | `observation_period` |
| Event (Vaccination visit) | `visit_occurrence` |
| Vaccine name / dose number | `drug_exposure` |
| Adverse event reported | `condition_occurrence` or `observation` |

The detailed source-to-target mapping is Sprint 3 work.
