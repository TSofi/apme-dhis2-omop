# Group 2 — Project Status Summary

**Project:** Public Health Data Pipeline - DHIS2 + OMOP CDM
**Course:** Advanced Programming in Medicine, FH Technikum Wien, WS2026
**Repository:** https://github.com/TSofi/apme-dhis2-omop
**Date:** 8 October 2026

## Goal

Collect patient-level immunization data in DHIS2, transform it into the OMOP Common Data Model, and run standardized analytics on the result.

```
DHIS2 Tracker -> Python ETL -> PostgreSQL / OMOP CDM v5.4 -> SQL analytics
```

Use case: COVID-19 immunization in Vienna. All patient data is synthetic.

## What is in place

**DHIS2.** Version 2.40.3, deployed with Docker together with PostgreSQL and PostGIS. Configured as a tracker program: organisation units Austria - Vienna - two health centres, tracked entity type Person with four attributes, Immunization Programme with a repeatable Vaccination visit stage, and three data elements (vaccine name, dose number, adverse event). The complete configuration is exported as JSON and can be imported into a fresh instance with one API call.

**Data.** A generator creates synthetic patients with multi-dose vaccination histories. They are loaded into DHIS2 through the tracker API.

**ETL.** A Python pipeline extracts the data through the DHIS2 Web API and maps it to OMOP CDM v5.4: person, drug_exposure, observation, care_site and location. A curated vocabulary subset is seeded into the concept table, with concepts verified against Athena (gender, RxNorm vaccines, SNOMED findings, route, place of service, country).

**Database.** OMOP CDM v5.4 in PostgreSQL, created from a DDL script and loaded in dependency order.

**Validation.** Three automated layers run on every execution: standards conformance (every concept exists and sits in the expected domain), referential integrity (no orphan records), and clinical plausibility (no vaccination before the date of birth).

**Analytics.** Three cohort queries: interval between dose 1 and dose 2 by vaccine brand, adverse events per 1000 doses, and cohort retention from the first dose to the booster.

**Automation.** The whole pipeline runs with a single command through an orchestrator script.

**Documentation in the repository.** DHIS2 setup guide, replication guide, source-to-OMOP mapping document, and the Sprint 1 report.

## Reproducing the system

1. `docker compose up -d` for DHIS2, then import the metadata JSON.
2. `docker compose -f docker-compose.omop.yml up -d` for the OMOP database, then apply the DDL.
3. `python scripts/orchestrator.py`.

No database dumps are exchanged. Everything is reproduced from configuration and code in the repository.

## Known limitations

- The vocabulary is a curated subset rather than the full Athena download.
- Adverse events are stored in OBSERVATION; Condition-domain concepts conventionally belong in CONDITION_OCCURRENCE.
- The source field for adverse events is a boolean, so individual symptoms are not differentiated.
- The system currently runs locally; there is no hosted instance.

## Next steps

1. Deploy DHIS2 on a hosted server so it is reachable from outside the local machine.
2. Enable mobile, offline-capable data capture against that instance and demonstrate synchronisation.
3. Extend the documentation into a full step-by-step installation and process guide.
4. Live demonstration of the complete system at the next sprint review.
