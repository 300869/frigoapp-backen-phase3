from dotenv import load_dotenv

load_dotenv()
from freshkeeper.database import SessionLocal
from freshkeeper.services.alert_runner import run_alert_scan

s = SessionLocal()
print(run_alert_scan(s))
s.close()
