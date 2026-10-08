"""
Synthetic Cohort Generator for DHIS2 Tracker API (Sprint 2).
Generates realistic patient immunization histories adhering strictly to
DHIS2 2.40 Tracker schema and metadata constraints.
"""
import random
from datetime import datetime, timedelta
from faker import Faker
import requests

fake = Faker("de_AT")  # Austrian locale for Vienna context

# DHIS2 Identifiers from metadata
PROGRAM_ID = "prgImmuniz1"
STAGE_ID = "psVaccinat1"
TET_PERSON = "tetPersonn1"

FACILITIES = [
    "vieHC1aaaa1",  # Vienna Health Centre 1
    "vieHC2aaaa2"   # Vienna Health Centre 2
]

VACCINES = ["Comirnaty", "Spikevax", "Vaxzevria"]


def generate_patient(facility_id=None):
    """Generate a single patient with realistic attributes and multi-dose vaccination history."""
    if not facility_id:
        facility_id = random.choice(FACILITIES)

    # 1. Demographics
    sex = random.choice(["Male", "Female"])
    first_name = fake.first_name_male() if sex == "Male" else fake.first_name_female()
    last_name = fake.last_name()
    
    # Age between 18 and 80 years old
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()

    attributes = [
        {"attribute": "attFirstNam", "value": first_name},
        {"attribute": "attLastName", "value": last_name},
        {"attribute": "attBirthDat", "value": birth_date},
        {"attribute": "attSexxxxx1", "value": sex}
    ]

    # 2. Timing: First dose between Jan 2025 and May 2026
    start_epoch = datetime(2025, 1, 15, 9, 0, 0)
    dose1_date = start_epoch + timedelta(days=random.randint(0, 450), hours=random.randint(0, 7))
    enrolled_at_str = dose1_date.strftime("%Y-%m-%dT%H:%M:%S.000")

    # 3. Events: 1 to 3 doses
    num_doses = random.choices([1, 2, 3], weights=[0.2, 0.5, 0.3])[0]
    vaccine_brand = random.choice(VACCINES)
    events = []

    current_dose_date = dose1_date
    for dose_num in range(1, num_doses + 1):
        has_adverse_event = "true" if random.random() < 0.08 else "false"

        event = {
            "program": PROGRAM_ID,
            "programStage": STAGE_ID,
            "orgUnit": facility_id,
            "occurredAt": current_dose_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "status": "COMPLETED",
            "dataValues": [
                {"dataElement": "deVaccineNm", "value": vaccine_brand},
                {"dataElement": "deDoseNumbr", "value": str(dose_num)},
                {"dataElement": "deAdverseEv", "value": has_adverse_event}
            ]
        }
        events.append(event)

        # Spacing for subsequent doses: 21-84 days later
        current_dose_date = current_dose_date + timedelta(days=random.randint(21, 84))

    # 4. Construct Full Tracked Entity Payload
    tracked_entity = {
        "trackedEntityType": TET_PERSON,
        "orgUnit": facility_id,
        "attributes": attributes,
        "enrollments": [
            {
                "program": PROGRAM_ID,
                "orgUnit": facility_id,
                "enrolledAt": enrolled_at_str,
                "occurredAt": enrolled_at_str,
                "status": "ACTIVE",
                "attributes": attributes,
                "events": events
            }
        ]
    }
    return tracked_entity


def generate_cohort(size=25):
    """Generate a batch cohort of tracked entities."""
    return [generate_patient() for _ in range(size)]


if __name__ == "__main__":
    import json
    sample = generate_cohort(size=2)
    print(f"Generated test batch of {len(sample)} patients.")
    print("Sample patient preview:")
    print(json.dumps(sample[0], indent=2))
