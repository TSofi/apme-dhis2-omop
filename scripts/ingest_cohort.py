"""
Batch Ingestion Script for DHIS2 Tracker API (Sprint 2).
Generates a synthetic cohort of patients and posts them in bulk to DHIS2.
"""
import sys
import json
import requests
from generate_cohort import generate_cohort

BASE_URL = "http://localhost:8080"
AUTH = ("admin", "district")


def ingest_batch(cohort_size=30):
    print(f"Generating synthetic cohort of {cohort_size} patients...")
    cohort = generate_cohort(size=cohort_size)

    payload = {
        "trackedEntities": cohort
    }

    url = f"{BASE_URL}/api/tracker?async=false"
    print(f"Posting batch of {cohort_size} patients to {url}...")

    res = requests.post(url, json=payload, auth=AUTH, timeout=120)

    if res.status_code not in (200, 201):
        print(f"[FAIL] HTTP Error {res.status_code}:")
        print(res.text)
        sys.exit(1)

    result = res.json()
    stats = result.get("stats", {})
    status = result.get("status")

    print("\n--- Ingestion Summary ---")
    print(f"Status: {status}")
    print(f"Created: {stats.get('created', 0)}")
    print(f"Updated: {stats.get('updated', 0)}")
    print(f"Ignored: {stats.get('ignored', 0)}")
    print(f"Deleted: {stats.get('deleted', 0)}")

    if stats.get("ignored", 0) > 0:
        print("\n[WARNING] Validation errors encountered:")
        print(json.dumps(result.get("validationReport", {}), indent=2))
        sys.exit(1)

    print(f"\n[OK] Successfully ingested {cohort_size} patients into DHIS2 Tracker!")


if __name__ == "__main__":
    ingest_batch(cohort_size=30)
