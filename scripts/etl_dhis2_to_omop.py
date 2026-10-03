"""
DHIS2 Tracker to OMOP CDM v5.4 ETL Pipeline (Sprint 2).
Extracts immunization cohort data via /api/tracker/trackedEntities
and transforms it into OMOP CDM tables:
  - PERSON
  - DRUG_EXPOSURE
  - OBSERVATION
  - CARE_SITE
  - LOCATION
"""
import os
import sys
from datetime import datetime
import requests
import pandas as pd

BASE_URL = os.getenv("DHIS2_BASE_URL", "http://localhost:8080")
AUTH = (os.getenv("DHIS2_USER", "admin"), os.getenv("DHIS2_PASSWORD", "district"))

ROOT_ORG_UNIT = "sp0vGb7cQBw"
PROGRAM_ID = "prgImmuniz1"
OUTPUT_DIR = "omop_output"

# OMOP Concept Mappings
GENDER_MAP = {
    "Male": 8507,
    "Female": 8532
}

VACCINE_MAP = {
    "Comirnaty": 37003436,
    "Spikevax": 37003518,
    "Vaxzevria": 37003432
}

CARE_SITES_METADATA = {
    "vieHC1aaaa1": {"id": 1, "name": "Vienna Health Centre 1"},
    "vieHC2aaaa2": {"id": 2, "name": "Vienna Health Centre 2"}
}


def extract_tracked_entities():
    """Extract all tracked entity instances under the root org unit."""
    url = f"{BASE_URL}/api/tracker/trackedEntities"
    params = {
        "program": PROGRAM_ID,
        "orgUnit": ROOT_ORG_UNIT,
        "ouMode": "DESCENDANTS",
        "fields": "trackedEntity,orgUnit,attributes[attribute,value],enrollments[enrollment,enrolledAt,status,events[event,programStage,occurredAt,status,dataValues[dataElement,value]]]"
    }
    
    res = requests.get(url, params=params, auth=AUTH, timeout=60)
    if res.status_code != 200:
        print(f"[FAIL] Extraction failed: HTTP {res.status_code}\n{res.text}")
        sys.exit(1)
        
    instances = res.json().get("instances", [])
    print(f"[OK] Extracted {len(instances)} tracked entities from DHIS2.")
    return instances


def transform_to_omop(instances):
    """Transform DHIS2 JSON records into OMOP CDM DataFrames."""
    persons = []
    drug_exposures = []
    observations = []

    # Reference static tables
    locations = [{
        "location_id": 1,
        "address_1": None,
        "city": "Vienna",
        "state": "Vienna",
        "zip": None,
        "county": None,
        "location_source_value": "Vienna, Austria",
        "country_concept_id": 4330442,
        "country_source_value": "Austria"
    }]

    care_sites = [
        {
            "care_site_id": meta["id"],
            "care_site_name": meta["name"],
            "place_of_service_concept_id": 38004207,  # Outpatient Healthcare Facility
            "location_id": 1,
            "care_site_source_value": uid,
            "place_of_service_source_value": "Health Centre"
        }
        for uid, meta in CARE_SITES_METADATA.items()
    ]

    person_id_seq = 1
    drug_exp_id_seq = 1
    obs_id_seq = 1

    for inst in instances:
        te_uid = inst.get("trackedEntity")
        facility_uid = inst.get("orgUnit")
        care_site_id = CARE_SITES_METADATA.get(facility_uid, {}).get("id", 1)

        # Parse attributes
        attr_map = {a.get("attribute"): a.get("value") for a in inst.get("attributes", [])}
        sex_str = attr_map.get("attSexxxxx1", "Unknown")
        dob_str = attr_map.get("attBirthDat")

        dob = None
        year_of_birth = month_of_birth = day_of_birth = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                year_of_birth = dob.year
                month_of_birth = dob.month
                day_of_birth = dob.day
            except ValueError:
                pass

        person_entry = {
            "person_id": person_id_seq,
            "gender_concept_id": GENDER_MAP.get(sex_str, 0),
            "year_of_birth": year_of_birth,
            "month_of_birth": month_of_birth,
            "day_of_birth": day_of_birth,
            "birth_datetime": f"{dob_str}T00:00:00" if dob_str else None,
            "race_concept_id": 0,
            "ethnicity_concept_id": 0,
            "location_id": 1,
            "provider_id": None,
            "care_site_id": care_site_id,
            "person_source_value": te_uid,
            "gender_source_value": sex_str,
            "gender_source_concept_id": 0,
            "race_source_value": None,
            "race_source_concept_id": 0,
            "ethnicity_source_value": None,
            "ethnicity_source_concept_id": 0
        }
        persons.append(person_entry)

        # Parse enrollments and events
        for enrollment in inst.get("enrollments", []):
            for event in enrollment.get("events", []):
                occurred_at_raw = event.get("occurredAt")
                if not occurred_at_raw:
                    continue
                
                event_date = occurred_at_raw.split("T")[0]
                event_datetime = occurred_at_raw.replace(".000", "")

                dv_map = {dv.get("dataElement"): dv.get("value") for dv in event.get("dataValues", [])}
                vaccine_name = dv_map.get("deVaccineNm")
                dose_number = dv_map.get("deDoseNumbr")
                adverse_ev = dv_map.get("deAdverseEv")

                # DRUG_EXPOSURE entry
                drug_concept_id = VACCINE_MAP.get(vaccine_name, 0)
                drug_entry = {
                    "drug_exposure_id": drug_exp_id_seq,
                    "person_id": person_id_seq,
                    "drug_concept_id": drug_concept_id,
                    "drug_exposure_start_date": event_date,
                    "drug_exposure_start_datetime": event_datetime,
                    "drug_exposure_end_date": event_date,
                    "drug_exposure_end_datetime": event_datetime,
                    "verbatim_end_date": None,
                    "drug_type_concept_id": 32817,  # EHR record
                    "stop_reason": None,
                    "refills": 0,
                    "quantity": 1,
                    "days_supply": 1,
                    "sig": f"Dose {dose_number}",
                    "route_concept_id": 4132161,  # Intramuscular injection
                    "lot_number": None,
                    "provider_id": None,
                    "visit_occurrence_id": None,
                    "visit_detail_id": None,
                    "drug_source_value": vaccine_name,
                    "drug_source_concept_id": 0,
                    "route_source_value": "IM",
                    "dose_unit_source_value": f"Dose {dose_number}"
                }
                drug_exposures.append(drug_entry)
                drug_exp_id_seq += 1

                # OBSERVATION entry (only when an adverse event occurred)
                if adverse_ev == "true":
                    obs_entry = {
                        "observation_id": obs_id_seq,
                        "person_id": person_id_seq,
                        "observation_concept_id": 43054909,  # Adverse event following immunization
                        "observation_date": event_date,
                        "observation_datetime": event_datetime,
                        "observation_type_concept_id": 32817,  # EHR
                        "value_as_number": None,
                        "value_as_string": "Adverse event documented",
                        "value_as_concept_id": 4181412,  # Present
                        "qualifier_concept_id": 0,
                        "unit_concept_id": 0,
                        "provider_id": None,
                        "visit_occurrence_id": None,
                        "visit_detail_id": None,
                        "observation_source_value": f"deAdverseEv=true (Vaccine: {vaccine_name}, Dose {dose_number})",
                        "observation_source_concept_id": 0,
                        "unit_source_value": None,
                        "qualifier_source_value": None,
                        "value_source_value": "true",
                        "observation_event_id": drug_entry["drug_exposure_id"],
                        "obs_event_field_concept_id": 1147094  # drug_exposure.drug_exposure_id
                    }
                    observations.append(obs_entry)
                    obs_id_seq += 1

        person_id_seq += 1

    return {
        "person": pd.DataFrame(persons),
        "drug_exposure": pd.DataFrame(drug_exposures),
        "observation": pd.DataFrame(observations),
        "care_site": pd.DataFrame(care_sites),
        "location": pd.DataFrame(locations)
    }


def run_etl():
    print("Starting DHIS2 -> OMOP CDM ETL Pipeline...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    instances = extract_tracked_entities()
    if not instances:
        print("[FAIL] No instances found. Ingestion may not have run.")
        sys.exit(1)

    tables = transform_to_omop(instances)

    print("\n--- OMOP CDM Transformation Summary ---")
    for table_name, df in tables.items():
        out_csv = os.path.join(OUTPUT_DIR, f"{table_name}.csv")
        df.to_csv(out_csv, index=False)
        print(f"  * {table_name.upper():<15} -> {len(df):>4} rows written to {out_csv}")

    print("\n[OK] ETL process completed successfully.")


if __name__ == "__main__":
    run_etl()
