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
    (43054909, "Pyrexia", "Condition", "Clinical Finding", "SNOMED", "S", "386661006", "2013-01-31", "2099-12-31", None),
    (378253, "Headache", "Condition", "Clinical Finding", "SNOMED", "S", "25064002", "1970-01-01", "2099-12-31", None),
    (4223659, "Fatigue", "Condition", "Clinical Finding", "SNOMED", "S", "84229001", "1970-01-01", "2099-12-31", None),
    (32817, "EHR encounter record", "Type Concept", "Drug Type", "Concept Class", "S", "OMOP generated", "1970-01-01", "2099-12-31", None),
    (8756, "Outpatient Hospital", "Care Site", "Place of Service", "CMS Place of Service", "S", "19", "1970-01-01", "2099-12-31", None),
    (1147094, "drug_exposure.drug_exposure_id", "Metadata", "Relationship", "Domain", "S", "OMOP generated", "1970-01-01", "2099-12-31", None)
]

def load():
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SET search_path TO cdm, public;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cdm.concept (
                concept_id integer NOT NULL,
                concept_name varchar(255) NOT NULL,
                domain_id varchar(20) NOT NULL,
                vocabulary_id varchar(20) NOT NULL,
                concept_class_id varchar(20) NOT NULL,
                standard_concept varchar(1),
                concept_code varchar(50) NOT NULL,
                valid_start_date date NOT NULL,
                valid_end_date date NOT NULL,
                invalid_reason varchar(1),
                CONSTRAINT xpk_concept PRIMARY KEY (concept_id)
            );
        """)
        cur.executemany("""
            INSERT INTO cdm.concept (
                concept_id, concept_name, domain_id, vocabulary_id,
                concept_class_id, standard_concept, concept_code,
                valid_start_date, valid_end_date, invalid_reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (concept_id) DO UPDATE SET
                concept_name = EXCLUDED.concept_name,
                vocabulary_id = EXCLUDED.vocabulary_id;
        """, STUDY_CONCEPTS)
        conn.commit()
    conn.close()
    print("[OK] CDM Concept table populated successfully.")

if __name__ == "__main__":
    load()
