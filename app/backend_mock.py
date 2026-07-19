from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models import Customer


class MockBackend:
    def __init__(self):
        self.customers = {
            "cust_123": Customer(id="cust_123", name="Anita Sharma", phone="+919****3210", email="anita@example.com", domain="healthcare"),
        }
        self.appointments = {
            "cust_123": []
        }
        self.providers = [
            {"name": "Dr. Sharma", "specialty": "Cardiology", "location": "Munger"},
            {"name": "Dr. Priya Rao", "specialty": "Dermatology", "location": "Patna"},
            {"name": "Dr. A. Khan", "specialty": "General Medicine", "location": "Munger"},
        ]

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)

    def book_appointment(self, customer_id: str, provider: Optional[str] = None, date: Optional[str] = None) -> str:
        if not provider:
            return "Which doctor or specialty would you like to book?"
        appt_time = self._suggest_slot(date)
        self.appointments[customer_id].append({"provider": provider, "time": appt_time})
        return f"Appointment booked with {provider} on {appt_time}. Please arrive 15 minutes early."

    def refill_prescription(self, customer_id: str, medication: Optional[str] = None) -> str:
        if not medication:
            return "Which medication would you like to refill?"
        return f"Refill request for {medication} submitted to your pharmacy. Pickup ready in 2-4 hours."

    def explain_billing(self, customer_id: str) -> str:
        return "Your upcoming visit copay is $25 based on your insurance plan. Deductible remaining: $150."

    def find_provider(self, specialty: Optional[str] = None, location: Optional[str] = None) -> str:
        matches = self.providers
        if specialty:
            matches = [p for p in matches if specialty.lower() in p["specialty"].lower()]
        if location:
            matches = [p for p in matches if location.lower() in p["location"].lower()]
        if not matches:
            return "No matching providers found. Try another specialty or location."
        return "Available providers:\n" + "\n".join([f"- {p['name']}, {p['specialty']}, {p['location']}" for p in matches[:5]])

    def _suggest_slot(self, date_hint: Optional[str]) -> str:
        base = datetime.now(timezone.utc) + timedelta(days=2)
        if date_hint and date_hint.lower() == "tomorrow":
            base = datetime.now(timezone.utc) + timedelta(days=1)
        return base.strftime("%Y-%m-%d at 10:00 AM")


BACKEND = MockBackend()
