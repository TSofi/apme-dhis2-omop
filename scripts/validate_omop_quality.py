"""
OMOP CDM v5.4 Data Quality, Standards Conformance & Epidemiological Analysis.
Verifies referential integrity, Athena concept/domain conformance,
and epidemiological plausibility.
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("OMOP_DB_HOST", "localhost")
DB_PORT = os.getenv("OMOP_DB_PORT", "5433")
DB_NAME = os.getenv("OMOP_DB_NAME", "omop")
DB_USER = os.getenv("OMOP_DB_USER", "postgres")
DB_PASSWORD = os.getenv("OMOP_DB_PASSWORD", "postgres")


def run_checks():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SET search_path TO cdm, public;")

        print("=" * 65)
        print("1. OMOP VOCABULARY & DOMAIN CONFORMANCE AUDIT")
        print("=" * 65)

        # 1.1 Verify Sex/Gender concepts in concept table with domain 'Gender'
        cur.execute("""
            SELECT p.person_id, p.gender_concept_id, c.concept_name, c.domain_id
            FROM person p
            LEFT JOIN concept c ON p.gender_concept_id = c.concept_id
            WHERE c.concept_id IS NULL OR c.domain_id != 'Gender';
        """)
        invalid_genders = cur.fetchall()
        print(f"  * Non-conforming Gender concepts (must exist with domain='Gender'): {len(invalid_genders)} -> {'PASS' if len(invalid_genders) == 0 else 'FAIL'}")

        # 1.2 Verify Drug concepts in concept table with domain 'Drug'
        cur.execute("""
            SELECT de.drug_exposure_id, de.drug_concept_id, c.concept_name, c.domain_id
            FROM drug_exposure de
            LEFT JOIN concept c ON de.drug_concept_id = c.concept_id
            WHERE c.concept_id IS NULL OR c.domain_id != 'Drug';
        """)
        invalid_drugs = cur.fetchall()
        print(f"  * Non-conforming Vaccine concepts (must exist with domain='Drug'): {len(invalid_drugs)} -> {'PASS' if len(invalid_drugs) == 0 else 'FAIL'}")

        # 1.3 Verify Adverse Event Observation concepts with domain 'Condition'
        cur.execute("""
            SELECT o.observation_id, o.observation_concept_id, c.concept_name, c.domain_id
            FROM observation o
            LEFT JOIN concept c ON o.observation_concept_id = c.concept_id
            WHERE c.concept_id IS NULL OR c.domain_id != 'Condition';
        """)
        invalid_obs = cur.fetchall()
        print(f"  * Non-conforming Adverse Event concepts (must exist with domain='Condition'): {len(invalid_obs)} -> {'PASS' if len(invalid_obs) == 0 else 'FAIL'}")

        assert len(invalid_genders) == 0 and len(invalid_drugs) == 0 and len(invalid_obs) == 0, "Standards conformance failed!"

        print("\n" + "=" * 65)
        print("2. REFERENTIAL INTEGRITY AUDIT")
        print("=" * 65)

        cur.execute("""
            SELECT COUNT(*) AS count
            FROM drug_exposure de
            LEFT JOIN person p ON de.person_id = p.person_id
            WHERE p.person_id IS NULL;
        """)
        orphan_drugs = cur.fetchone()["count"]
        print(f"  * Orphan DRUG_EXPOSURE rows (missing PERSON): {orphan_drugs} -> {'PASS' if orphan_drugs == 0 else 'FAIL'}")

        cur.execute("""
            SELECT COUNT(*) AS count
            FROM observation o
            LEFT JOIN person p ON o.person_id = p.person_id
            WHERE p.person_id IS NULL;
        """)
        orphan_obs = cur.fetchone()["count"]
        print(f"  * Orphan OBSERVATION rows (missing PERSON): {orphan_obs} -> {'PASS' if orphan_obs == 0 else 'FAIL'}")

        cur.execute("""
            SELECT COUNT(*) AS count
            FROM observation o
            LEFT JOIN drug_exposure de ON o.observation_event_id = de.drug_exposure_id
            WHERE o.observation_event_id IS NOT NULL AND de.drug_exposure_id IS NULL;
        """)
        orphan_links = cur.fetchone()["count"]
        print(f"  * Orphan OBSERVATION -> DRUG_EXPOSURE links: {orphan_links} -> {'PASS' if orphan_links == 0 else 'FAIL'}")

        cur.execute("""
            SELECT COUNT(*) AS count
            FROM person p
            LEFT JOIN care_site cs ON p.care_site_id = cs.care_site_id
            WHERE p.care_site_id IS NOT NULL AND cs.care_site_id IS NULL;
        """)
        orphan_cs = cur.fetchone()["count"]
        print(f"  * Invalid CARE_SITE references in PERSON: {orphan_cs} -> {'PASS' if orphan_cs == 0 else 'FAIL'}")

        assert orphan_drugs == 0 and orphan_obs == 0 and orphan_links == 0 and orphan_cs == 0, "Referential integrity failed!"

        print("\n" + "=" * 65)
        print("3. CLINICAL PLAUSIBILITY ASSERTIONS")
        print("=" * 65)

        cur.execute("""
            SELECT COUNT(*) AS count
            FROM drug_exposure de
            JOIN person p ON de.person_id = p.person_id
            WHERE de.drug_exposure_start_date < p.birth_datetime::date;
        """)
        exposure_before_birth = cur.fetchone()["count"]
        print(f"  * Vaccinations occurring before birth: {exposure_before_birth} -> {'PASS' if exposure_before_birth == 0 else 'FAIL'}")

        assert exposure_before_birth == 0, "Clinical plausibility check failed!"

        print("\n" + "=" * 65)
        print("4. EPIDEMIOLOGICAL SUMMARY (OHDSI VOCABULARY RESOLVED)")
        print("=" * 65)

        cur.execute("""
            SELECT c.concept_name AS vaccine_name,
                   c.concept_code AS rxnorm_code,
                   COUNT(de.drug_exposure_id) AS total_doses
            FROM drug_exposure de
            JOIN concept c ON de.drug_concept_id = c.concept_id
            GROUP BY c.concept_name, c.concept_code
            ORDER BY total_doses DESC;
        """)
        for row in cur.fetchall():
            print(f"    - {row['vaccine_name']} (RxNorm: {row['rxnorm_code']}): {row['total_doses']} doses")

    conn.close()
    print("\n" + "=" * 65)
    print("[SUCCESS] All Standards Conformance, Integrity & Quality Checks Passed!")
    print("=" * 65)


if __name__ == "__main__":
    run_checks()
