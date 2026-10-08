"""
Verification script for DHIS2 2.40 Tracker API ingestion & extraction.
Used in Sprint 1 setup for the DHIS2 -> OMOP CDM pipeline.
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8080"
AUTH = ("admin", "district")

def verify_extraction():
    url = f"{BASE_URL}/api/tracker/trackedEntities"
    params = {
        "program": "prgImmuniz1",
        "orgUnit": "sp0vGb7cQBw",
        "ouMode": "DESCENDANTS",
        "fields": "trackedEntity,orgUnit,attributes[attribute,value],enrollments[enrollment,enrolledAt,status,events[event,programStage,occurredAt,status,dataValues[dataElement,value]]]"
    }
    
    response = requests.get(url, params=params, auth=AUTH)
    if response.status_code != 200:
        print(f"Extraction failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
        
    data = response.json()
    instances = data.get("instances", [])
    print(f"Extracted {len(instances)} tracked entity instance(s).")
    if instances:
        print("Sample patient payload verified:")
        print(json.dumps(instances[0], indent=2))

if __name__ == "__main__":
    verify_extraction()
