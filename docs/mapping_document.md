# Source-to-OMOP CDM v5.4 Semantic Mapping Document

## 1. Demographic Mapping (PERSON)

| Source Field | DHIS2 Source Value | Target CDM Field | Target Concept ID | Standard Concept Name | Target Domain | Standard Vocabulary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gender` | `MALE` | `gender_concept_id` | **8507** | Male | Gender | Gender |
| `gender` | `FEMALE` | `gender_concept_id` | **8532** | Female | Gender | Gender |
| `birth_date` | `YYYY-MM-DD` | `year_of_birth`, `month_of_birth`, `day_of_birth` | — | Extracted Year/Month/Day | Demographics | Standard CDM |
| `tei_uid` | Text UID | `person_source_value` | — | Verbatim DHIS2 Tracked Entity UID | Metadata | Source Value |

*Note: Race and Ethnicity are assigned standard concept `0` (Unknown/No matching concept).*

---

## 2. Vaccine Exposure Mapping (DRUG_EXPOSURE)

| DHIS2 Data Element | DHIS2 Source Option | Target Concept ID | Standard Concept Name | Vocabulary | OMOP Domain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vaccine_name` | `Comirnaty` | **37003436** | SARS-CoV-2 (COVID-19) vaccine, mRNA-BNT162b2 | RxNorm | Drug |
| `vaccine_name` | `Spikevax` | **37003518** | SARS-CoV-2 (COVID-19) vaccine, mRNA-1273 | RxNorm | Drug |
| `vaccine_name` | `Vaxzevria` | **37003432** | SARS-CoV-2 (COVID-19) vaccine, vector-based ChAdOx1 | RxNorm | Drug |
| *Type* | Derived | **32817** | EHR encounter record | Type Concept | Drug Type |

* **Exposure Dates**: DHIS2 event `executionDate` maps to both `drug_exposure_start_date` and `drug_exposure_end_date`.
* **Dose Number**: DHIS2 `dose_number` (1, 2, 3) maps to `sig`.

---

## 3. Adverse Event Mapping (OBSERVATION)

| DHIS2 Data Element | DHIS2 Source Option | Target Concept ID | Standard Concept Name | Vocabulary | OMOP Domain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `adverse_event` | `Fever` | **437663** | Fever / Pyrexia | SNOMED | Condition |
| `adverse_event` | `Headache` | **378253** | Headache | SNOMED | Condition |
| `adverse_event` | `Fatigue` | **4223659** | Fatigue | SNOMED | Condition |
| *Type* | Derived | **32817** | EHR encounter record | Type Concept | Observation Type |

* **Event Linkage**: `observation_event_id` stores foreign key reference to `drug_exposure_id`.
* **Field Concept**: `obs_event_field_concept_id` is populated with `1147094` (`drug_exposure.drug_exposure_id`).

---

## 4. Organizational Structure (CARE_SITE & LOCATION)

| DHIS2 Source Level | Source Name | Target Table | Target Primary Key | Target Mapping |
| :--- | :--- | :--- | :--- | :--- |
| Country / City | Vienna, Austria | `LOCATION` | `1` | `city = 'Vienna'`, `country_source_value = 'Austria'` |
| Org Unit 1 | Vienna Health Centre 1 | `CARE_SITE` | `1` | `place_of_service_concept_id = 8756` (Outpatient Hospital) |
| Org Unit 2 | Vienna Health Centre 2 | `CARE_SITE` | `2` | `place_of_service_concept_id = 8756` (Outpatient Hospital) |
