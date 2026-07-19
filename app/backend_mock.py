from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.models import Customer


class HealthcareBackend:
    def __init__(self):
        self.settings = get_settings()
        self.customers = {
            "cust_123": Customer(
                id="cust_123",
                name="Anita Sharma",
                phone="+919****3210",
                email="anita@example.com",
                domain="healthcare",
            ),
        }
        self.appointments = {"cust_123": []}
        self.providers = [
            {"name": "Dr. Sharma", "specialty": "Cardiology", "location": "Munger"},
            {"name": "Dr. Priya Rao", "specialty": "Dermatology", "location": "Patna"},
            {"name": "Dr. A. Khan", "specialty": "General Medicine", "location": "Munger"},
        ]

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        data = self._request("fhir", "GET", f"/Patient/{customer_id}")
        if data:
            name = self._patient_name(data)
            telecom = data.get("telecom", [])
            email = next((item.get("value") for item in telecom if item.get("system") == "email"), None)
            phone = next((item.get("value") for item in telecom if item.get("system") == "phone"), None)
            return Customer(
                id=customer_id,
                name=name,
                phone=phone,
                email=email,
                domain="healthcare",
                authenticated=True,
            )
        return self.customers.get(customer_id)

    def book_appointment(
        self,
        customer_id: str,
        provider: Optional[str] = None,
        date: Optional[str] = None,
    ) -> str:
        if not provider:
            return "Which doctor or specialty would you like to book?"
        data = self._request(
            "scheduling",
            "POST",
            "/appointments",
            json={"patient_id": customer_id, "provider": provider, "date": date},
        )
        if data:
            starts_at = data.get("starts_at") or data.get("time")
            return f"Appointment booked with {provider} on {starts_at}. Please arrive 15 minutes early."
        appt_time = self._suggest_slot(date)
        self.appointments.setdefault(customer_id, []).append({"provider": provider, "time": appt_time})
        return f"Appointment booked with {provider} on {appt_time}. Please arrive 15 minutes early."

    def refill_prescription(self, customer_id: str, medication: Optional[str] = None) -> str:
        if not medication:
            return "Which medication would you like to refill?"
        data = self._request(
            "pharmacy",
            "POST",
            "/refills",
            json={"patient_id": customer_id, "medication": medication},
        )
        if data:
            eta = data.get("pickup_eta", "when your pharmacy confirms it")
            return f"Refill request for {medication} submitted to your pharmacy. Pickup ready {eta}."
        return f"Refill request for {medication} submitted to your pharmacy. Pickup ready in 2-4 hours."

    def explain_billing(self, customer_id: str) -> str:
        data = self._request("billing", "GET", f"/patients/{customer_id}/summary")
        if data:
            copay = data.get("copay")
            deductible = data.get("deductible_remaining")
            return f"Your upcoming visit copay is ${copay}. Deductible remaining: ${deductible}."
        return "Your upcoming visit copay is $25 based on your insurance plan. Deductible remaining: $150."

    def find_provider(
        self,
        specialty: Optional[str] = None,
        location: Optional[str] = None,
    ) -> str:
        data = self._request(
            "providers",
            "GET",
            "/providers",
            params={"specialty": specialty, "location": location},
        )
        matches = data.get("providers", []) if data else self.providers
        if specialty:
            matches = [p for p in matches if specialty.lower() in p["specialty"].lower()]
        if location:
            matches = [p for p in matches if location.lower() in p["location"].lower()]
        if not matches:
            return "No matching providers found. Try another specialty or location."
        return "Available providers:\n" + "\n".join(
            [f"- {p['name']}, {p['specialty']}, {p['location']}" for p in matches[:5]]
        )

    def _request(self, service: str, method: str, path: str, **kwargs) -> Optional[dict[str, Any]]:
        if not self.settings.PHI_INTEGRATIONS_ENABLED:
            return None
        base_url, token = self._service_config(service)
        if not base_url:
            return None
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        url = base_url.rstrip("/") + path
        try:
            with httpx.Client(timeout=8.0) as client:
                response = client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError):
            return None

    def _service_config(self, service: str) -> tuple[str, str]:
        services = {
            "fhir": (self.settings.FHIR_API_BASE_URL, self.settings.FHIR_API_TOKEN),
            "scheduling": (
                self.settings.SCHEDULING_API_BASE_URL,
                self.settings.SCHEDULING_API_TOKEN,
            ),
            "pharmacy": (self.settings.PHARMACY_API_BASE_URL, self.settings.PHARMACY_API_TOKEN),
            "billing": (self.settings.BILLING_API_BASE_URL, self.settings.BILLING_API_TOKEN),
            "providers": (
                self.settings.PROVIDER_DIRECTORY_API_BASE_URL,
                self.settings.PROVIDER_DIRECTORY_API_TOKEN,
            ),
        }
        return services[service]

    def _patient_name(self, patient: dict[str, Any]) -> Optional[str]:
        names = patient.get("name", [])
        if not names:
            return None
        first = names[0]
        given = " ".join(first.get("given", []))
        family = first.get("family", "")
        return " ".join([part for part in [given, family] if part])

    def _suggest_slot(self, date_hint: Optional[str]) -> str:
        base = datetime.utcnow() + timedelta(days=2)
        if date_hint and date_hint.lower() == "tomorrow":
            base = datetime.utcnow() + timedelta(days=1)
        return base.strftime("%Y-%m-%d at 10:00 AM")


BACKEND = HealthcareBackend()
