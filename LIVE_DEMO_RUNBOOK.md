# Live Demo Runbook

## Setup (Before the Demo)
Generate and ingest the 30 synthetic patients a few days in advance, and run the full pipeline once so the OMOP database already holds that population:
```powershell
$env:DHIS2_PASSWORD = "<YOUR_DHIS2_PASSWORD>"
python .\scripts\orchestrator.py
```

---

## Live Demo Quick Start
1. Start tunnel: `.\scripts\run_tunnel.ps1`
2. Connect phone USB and start mirror: `.\scripts\run_mirror.ps1`
3. App Login:
   - Username: `admin`
   - Password: `$env:DHIS2_PASSWORD`
4. Disconnect Wi-Fi / enable Airplane mode, create only one patient live on the phone, reconnect, tap Sync.
5. Run OMOP processing for the newly captured record:
```powershell
$env:DHIS2_PASSWORD = "<YOUR_DHIS2_PASSWORD>"
python scripts/etl_dhis2_to_omop.py
python scripts/load_omop_postgres.py
python scripts/validate_omop_quality.py
```
