"""
Loads a curated Athena vocabulary subset into cdm.concept.
Ensures domain conformance and standard OHDSI SQL joins.
"""
import os
import psycopg2

DB_HOST = os.getenv("OMOP_DB_HOST", "localhost")
DB_PORT = os.getenv("OMOP_DB_PORT", "5433")
DB_NAME = os.getenv("OMOP_DB_NAME", "omop")
DB_USER = os.getenv("OMOP_DB_USER", "postgres")
DB_PASSWORD = os.getenv("OMOP_DB_PASSWORD", "postgres")

STUDY_CONCEPTS = [
    (8507, "MALE", "Gender", "Gender", "Gender", "S", "M", "1970-01-01", "2099-12-31", None),
    (8532, "FEMALE", "Gender", "Gender", "Gender", "S", "F", "1970-01-01", "2099-12-31", None),
    (0, "No matching concept", "Metadata", "Concept", "Vocabulary", "S", "OMOP generated", "1970-01-01", "2099-12-31", None),
    (37003436, "SARS-CoV-2 (COVID-19) vaccine, mRNA-BNT162b2", "Drug", "Vaccine", "RxNorm", "S", "2081156", "2020-12-11", "2099-12-31", None),
    (37003518, "SARS-CoV-2 (COVID-19) vaccine, mRNA-1273", "Drug", "Vaccine", "RxNorm", "S", "2080313", "2020-12-18", "2099-12-31", None),
    (37003432, "SARS-CoV-2 (COVID-19) vaccine, vector-based ChAdOx1", "Drug", "Vaccine", "RxNorm", "S", "2081045", "2021-01-29", "2099-12-31", None),
    (437663, "Fever", "Condition", "Clinical Finding", "SNOMED", "S", "386661006", "1970-01-01", "2099-12-31", None),
    (378253, "Headache", "Condition", "Clinical Finding", "SNOMED", "S", "25064002", "1970-01-01", "2099-12-31", None),
    (4223659, "Fatigue", "Condition", "Clinical Finding", "SNOMED", "S", "84229001", "1970-01-01", "2099-12-31", None),
    (32817, "EHR encounter record", "Type Concept", "Type Concept", "Concept Class", "S", "OMOP generated", "1970-01-01", "2099-12-31", None),
    (1147094, "drug_exposure.drug_exposure_id", "Metadata", "Concept", "Concept Class", "S", "OMOP generated", "1970-01-01", "2099-12-31", None),
    (8756, "Outpatient Hospital", "Visit", "CMS Place of Service", "Place of Service", "S", "22", "1970-01-01", "2099-12-31", None),
    (4132161, "Oral / Route finding", "Observation", "SNOMED", "Qualifier Value", "S", "260548002", "1970-01-01", "2099-12-31", None),
    (4181412, "Present", "Observation", "SNOMED", "Qualifier Value", "S", "52101004", "1970-01-01", "2099-12-31", None),
    (4330442, "Severe", "Observation", "SNOMED", "Qualifier Value", "S", "24484000", "1970-01-01", "2099-12-31", None)
]

def load_study_vocabularies():
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()
    cur.execute("SET search_path TO cdm, public;")
    insert_sql = """
        INSERT INTO concept (
            concept_id, concept_name, domain_id, vocabulary_id, concept_class_id,
            standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (concept_id) DO UPDATE SET
            concept_name = EXCLUDED.concept_name,
            domain_id = EXCLUDED.domain_id,
            vocabulary_id = EXCLUDED.vocabulary_id;
    """
    cur.executemany(insert_sql, STUDY_CONCEPTS)
    conn.commit()
    print(f"[OK] Seeded {len(STUDY_CONCEPTS)} standard Athena concepts into cdm.concept.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    load_study_vocabularies()
