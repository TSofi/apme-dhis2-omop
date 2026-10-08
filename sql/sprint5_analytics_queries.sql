-- =====================================================================
-- Sprint 5: Analytics & Demo Presentation SQL Queries
-- Target Schema: cdm (OMOP CDM v5.4)
-- =====================================================================

-- Query 1: Dose Interval Distribution by Vaccine Brand
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

-- Query 2: Pharmacovigilance & Safety Signals (AE Rate per 1k Doses)
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

-- Query 3: Cohort Retention and Booster Attrition
SELECT 
    COUNT(DISTINCT person_id) AS total_cohort,
    COUNT(DISTINCT CASE WHEN sig = 'Dose 1' THEN person_id END) AS received_dose_1,
    COUNT(DISTINCT CASE WHEN sig = 'Dose 2' THEN person_id END) AS received_dose_2,
    COUNT(DISTINCT CASE WHEN sig = 'Dose 3' THEN person_id END) AS received_dose_3,
    ROUND((COUNT(DISTINCT CASE WHEN sig = 'Dose 2' THEN person_id END)::numeric / COUNT(DISTINCT person_id)::numeric) * 100, 1) AS primary_completion_rate_pct,
    ROUND((COUNT(DISTINCT CASE WHEN sig = 'Dose 3' THEN person_id END)::numeric / COUNT(DISTINCT person_id)::numeric) * 100, 1) AS booster_uptake_rate_pct
FROM cdm.drug_exposure;
