# APME Project 2 — Public Health Data Pipeline (DHIS2 + OMOP CDM)

**Course:** Advanced Programming in Medicine, FH Technikum Wien, WS2026
**Lecturer:** Dr Prabath Jayathissa
**Group 2:** Sofia, Ahmer, [Member C], [Member D]

## 1. Project goal

We configure a DHIS2 tracker program for a public health use case, fill it with patient-level data, transform that data into the OMOP Common Data Model with an ETL pipeline, and run standardized analytics on the result.

**Use case (proposed):** Immunization tracking.

**Pipeline:**

```
DHIS2 (tracker program + sample data)
   → extraction (DHIS2 export / Web API)
   → ETL (source-to-OMOP mapping)
   → OMOP CDM database
   → analytics (SQL cohort queries / ATLAS)
```

## 2. Team roles

| Member | Main area | Responsible for |
|---|---|---|
| **Sofia** | Database & SQL | Tracker program configuration (Sprint 1), OMOP CDM schema and vocabularies (Sprint 3), SQL cohort queries and analytics (Sprint 5), GitHub repository and documentation |
| **Ahmer** | Python & data analysis | Exploring the DHIS2 data export (Sprint 1), sample data generation (Sprint 2), ETL pipeline implementation (Sprint 4) |
| **[Member C]** | Setup & infrastructure | DHIS2 installation (Sprint 1), shared environment and reproducible setup instructions, support for OMOP database setup (Sprint 3) |
| **[Member D]** | Mapping & reporting | Source-to-OMOP mapping documentation (Sprint 3), testing and validating the ETL output (Sprint 4), final report and demo preparation (Sprint 5) |

Everyone reviews each other's work before a sprint review, and everyone contributes a section on their own part to the final report.

## 3. Sprint plan

| Sprint | Goal | Lead | Deliverable |
|---|---|---|---|
| 1 — Discovery | Install DHIS2, configure a tracker program | Member C, Sofia | Running DHIS2 + configured program |
| 2 — Data collection | Populate / simulate patient-level event data | Ahmer | Sample data in DHIS2 |
| 3 — ETL design | Source-to-OMOP mapping, OMOP schema + vocabularies | Sofia, Member D | Mapping document, empty OMOP database |
| 4 — ETL build | Implement the transformation pipeline | Ahmer, Member D | ETL code, populated OMOP database |
| 5 — Analytics & demo | Cohort query, results, presentation | Sofia, all | Analytics report, live demo |

## 4. Sprint 1 — Discovery

**Goal (from the course brief):** Install DHIS2 and configure a tracker program for the chosen use case.

| Task | Owner |
|---|---|
| Agree on the use case | All |
| Create the GitHub repository | Sofia |
| Install DHIS2 | Member C |
| Configure the organisation units | Sofia |
| Create the data elements and tracked entity attributes | Sofia |
| Create the tracker program and its program stages | Sofia |
| Explore how data can be exported from DHIS2 | Ahmer |
| Read the OMOP CDM basics (key tables) | Member D |
