# Progress report - 26 October 2026

Status of the DHIS2 to OMOP CDM pipeline against the course requirements.

Repository: https://github.com/TSofi/apme-dhis2-omop

---

## 1. Completed

| Area | What exists | Where |
|---|---|---|
| Source system | DHIS2 2.40.3 deployed with Docker, immunization tracker program configured (organisation units, Person entity with four attributes, repeatable Vaccination visit stage, three data elements) | `config/dhis2/docker-compose.yml` |
| Reproducible configuration | The full DHIS2 configuration exported as metadata, importable into a fresh instance with one API call | `config/dhis2/immunization-metadata.json` |
| Synthetic data | Generator producing patients with multi-dose vaccination histories, and batch ingestion through the tracker API | `scripts/generate_cohort.py`, `scripts/ingest_cohort.py` |
| ETL | Extraction from the DHIS2 Web API and transformation into OMOP CDM v5.4 tables (person, drug_exposure, observation, care_site, location) | `scripts/etl_dhis2_to_omop.py` |
| Target database | OMOP CDM v5.4 schema in PostgreSQL, bulk loading in dependency order | `sql/omop_cdm_v5_4_ddl.sql`, `docker-compose.omop.yml`, `scripts/load_omop_postgres.py` |
| Vocabulary | Curated concept subset seeded into `cdm.concept`, verified against Athena definitions | `scripts/load_vocabularies_subset.py` |
| Validation | Three automated layers: standards conformance, referential integrity, clinical plausibility | `scripts/validate_omop_quality.py` |
| Analytics | Three cohort queries: dose interval by brand, adverse events per 1000 doses, cohort retention | `scripts/sprint5_analytics.py`, `sql/sprint5_analytics_queries.sql` |
| Automation | Single-command execution of all six pipeline stages | `scripts/orchestrator.py` |
| Documentation | Full project documentation, DHIS2 setup guide, replication guide, source-to-target mapping, demo runbook, sprint 1 report | `README.md`, `docs/` |
| Mobile capture | Offline data capture with the DHIS2 Android Capture app tested successfully against the instance exposed through a tunnel | tested, not yet in the repository |

---

## 2. Outstanding work

Mapped to the assessment criteria: 40 percent working implementation, 25 percent documentation and report, 20 percent demo, 15 percent standards conformance and validation evidence.

| # | Item | Why it is needed | Owner |
|---|---|---|---|
| 1 | **Validation evidence.** Run the pipeline and commit the actual output of the validation script as a report file. | The repository currently contains the checks but no recorded result of running them. This is the 15 percent criterion. | Sofiia |
| 2 | **Final technical report**, including a reflection on the interoperability challenges encountered. | Required final deliverable for every project in the course brief. | Sofiia |
| 3 | **Mobile capture documentation.** Tunnel setup, phone connection, screen mirroring, and screenshots of the offline capture and synchronisation. | The mobile part exists only as a successful local test; nothing is in the repository. | Irshad |
| 4 | **Demo rehearsal.** One complete run through the demo runbook before the session. | The demonstration is 20 percent of the assessment and is performed live. | Sofiia, Irshad |
| 5 | **Optional: move adverse events to `CONDITION_OCCURRENCE`.** | Currently documented as a known limitation. Resolving it strengthens the conformance criterion. | open |

---

## 3. Known limitations

1. The vocabulary is a curated subset seeded from verified Athena definitions, not the full Athena download. Conformance checks therefore cover the concepts this project uses.
2. Adverse events are stored in `OBSERVATION`; Condition-domain concepts conventionally belong in `CONDITION_OCCURRENCE`.
3. The source data element for adverse events is a boolean, so individual symptoms are not differentiated.
4. The system runs locally. Reproducibility comes from configuration and code in the repository rather than from a shared instance.

---

## 4. Assessment

The implementation is essentially complete and runs end to end, from a phone without connectivity to a validated OMOP record. What remains is evidence and reporting rather than new functionality: recording a validation run, writing the final report, and documenting the mobile part.
