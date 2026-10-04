"""
Sprint 5: OMOP CDM v5.4 Epidemiological Analytics & Safety Signal Detection.
Executes analytical SQL queries against cdm schema to generate presentation metrics.
"""
import os
import pandas as pd
from sqlalchemy import create_engine

DB_HOST = os.getenv("OMOP_DB_HOST", "localhost")
DB_PORT = os.getenv("OMOP_DB_PORT", "5433")
DB_NAME = os.getenv("OMOP_DB_NAME", "omop")
DB_USER = os.getenv("OMOP_DB_USER", "postgres")
DB_PASSWORD = os.getenv("OMOP_DB_PASSWORD", "postgres")

def run_analytics():
    # Use postgresql+psycopg2 explicitly
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    print("\n" + "=" * 70)
    print("QUERY 1: DOSE 1 TO DOSE 2 INTERVAL (DAYS) BY VACCINE BRAND")
    print("=" * 70)
    q1 = """
    WITH dose1 AS (
        SELECT person_id, drug_concept_id, drug_exposure_start_date AS d1_date
        FROM cdm.drug_exposure
        WHERE sig = 'Dose 1'
    ),
    dose2 AS (
        SELECT person_id, drug_concept_id, drug_exposure_start_date AS d2_date
        FROM cdm.drug_exposure
        WHERE sig = 'Dose 2'
    )
    SELECT 
        c.concept_name AS vaccine_name,
        COUNT(d2.person_id) AS completed_primary_cohort,
        ROUND(AVG(d2.d2_date - d1.d1_date), 1) AS avg_interval_days,
        MIN(d2.d2_date - d1.d1_date) AS min_interval_days,
        MAX(d2.d2_date - d1.d1_date) AS max_interval_days
    FROM dose1 d1
    JOIN dose2 d2 ON d1.person_id = d2.person_id AND d1.drug_concept_id = d2.drug_concept_id
    JOIN cdm.concept c ON d1.drug_concept_id = c.concept_id
    GROUP BY c.concept_name
    ORDER BY completed_primary_cohort DESC;
    """
    df1 = pd.read_sql(q1, engine)
    print(df1.to_string(index=False))

    print("\n" + "=" * 70)
    print("QUERY 2: ADVERSE EVENT SAFETY SIGNALS (PER 1,000 DOSES)")
    print("=" * 70)
    q2 = """
    SELECT 
        c_drug.concept_name AS vaccine_name,
        COUNT(DISTINCT de.drug_exposure_id) AS total_doses_administered,
        COUNT(DISTINCT o.observation_id) AS adverse_events_reported,
        ROUND((COUNT(DISTINCT o.observation_id)::numeric / COUNT(DISTINCT de.drug_exposure_id)::numeric) * 1000, 2) AS ae_rate_per_1k_doses
    FROM cdm.drug_exposure de
    JOIN cdm.concept c_drug ON de.drug_concept_id = c_drug.concept_id
    LEFT JOIN cdm.observation o ON de.drug_exposure_id = o.observation_event_id
    GROUP BY c_drug.concept_name
    ORDER BY ae_rate_per_1k_doses DESC;
    """
    df2 = pd.read_sql(q2, engine)
    print(df2.to_string(index=False))

    print("\n" + "=" * 70)
    print("QUERY 3: COHORT RETENTION & ATTRITION ANALYSIS")
    print("=" * 70)
    q3 = """
    SELECT 
        COUNT(DISTINCT person_id) AS total_cohort,
        COUNT(DISTINCT CASE WHEN sig = 'Dose 1' THEN person_id END) AS received_dose_1,
        COUNT(DISTINCT CASE WHEN sig = 'Dose 2' THEN person_id END) AS received_dose_2,
        COUNT(DISTINCT CASE WHEN sig = 'Dose 3' THEN person_id END) AS received_dose_3,
        ROUND((COUNT(DISTINCT CASE WHEN sig = 'Dose 2' THEN person_id END)::numeric / COUNT(DISTINCT person_id)::numeric) * 100, 1) AS primary_completion_rate_pct,
        ROUND((COUNT(DISTINCT CASE WHEN sig = 'Dose 3' THEN person_id END)::numeric / COUNT(DISTINCT person_id)::numeric) * 100, 1) AS booster_uptake_rate_pct
    FROM cdm.drug_exposure;
    """
    df3 = pd.read_sql(q3, engine)
    print(df3.to_string(index=False))

if __name__ == "__main__":
    run_analytics()
