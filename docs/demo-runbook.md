# Live demo runbook

End-to-end demonstration: offline data capture on a phone, synchronisation to DHIS2, transformation into the OMOP CDM.

**Duration:** about 6 minutes.
**Equipment:** laptop (DHIS2 + OMOP database + scripts), Android phone with the DHIS2 Capture app, internet for the laptop and the phone.

---

## The story we are showing

A health worker registers a vaccination in a village with no connectivity. The record is stored on the phone. When the phone is back online, the data reaches the DHIS2 server. From there our pipeline transforms it into the OMOP Common Data Model, where it can be analysed together with data from any other OMOP site.

---

## Before class

1. Start DHIS2 and the OMOP database:
   ```
   cd config/dhis2 && docker compose up -d
   docker compose -f docker-compose.omop.yml up -d
   ```
2. Confirm DHIS2 is reachable at http://localhost:8080 and that the immunization metadata is imported.
3. Make sure the admin password has been changed from the default.
4. Install the DHIS2 Capture app on the phone (Google Play).
5. Run through the whole script below once.

---

## Demo steps

### 1. Show the system (1 min)

Open DHIS2 in the browser. Show the Immunization Programme, the organisation unit hierarchy and the Vaccination visit stage.

Say: this is the source system. It is the same instance the phone will talk to.

### 2. Expose the instance and connect the phone (1 min)

Start the tunnel on the laptop:

```
cloudflared tunnel --url http://localhost:8080
```

It prints a public HTTPS URL. Open that URL in the browser to show it is the same DHIS2.

On the phone: open the Capture app and connect to that URL, then log in.

Note: a quick tunnel creates a new random URL each time it starts. The whole demo must stay inside one tunnel session, because the app ties its local data to the server it was connected to.

### 3. Capture offline (2 min)

Turn on airplane mode on the phone. Show that there is no connection.

In the app, register a new person in the Immunization Programme:
- first name, last name, date of birth, sex
- a Vaccination visit event: vaccine name, dose number, adverse event

Save. The record is now in the phone's local database only.

Say: this is the realistic case - a health worker in an area with no coverage.

### 4. Synchronise (1 min)

Turn airplane mode off. Trigger synchronisation in the app.

Refresh DHIS2 in the browser and show the new patient and the vaccination event.

### 5. Transform into OMOP (1-2 min)

On the laptop:

```
python scripts/etl_dhis2_to_omop.py
python scripts/load_omop_postgres.py
python scripts/validate_omop_quality.py
```

Show:
- the extracted record in the OMOP tables (`person`, `drug_exposure`)
- the validation output: standards conformance, referential integrity, clinical plausibility all passing

Optionally run one analytics query to show the new record included in the cohort numbers.

Say: the data captured on a phone without internet is now a standard OMOP record, queryable with the same SQL as any other OMOP database.

---

## Fallbacks

| Problem | Fallback |
|---|---|
| The tunnel will not start | Show the capture step on the phone and explain the sync; continue the pipeline part with existing data |
| The phone cannot connect | Create the record in the DHIS2 web interface and run the pipeline from there |
| The pipeline fails | Show the last successful validation output and the populated OMOP tables |

Keep a few screenshots of each step on the laptop as a last resort.
