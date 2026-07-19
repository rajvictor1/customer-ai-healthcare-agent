import pytest
from app.classifier import IntentClassifier


@pytest.fixture
def classifier():
    return IntentClassifier(use_llm=False)


def test_refill(classifier):
    intent, conf = classifier.classify("Refill my Lisinopril")
    assert intent == "HC_REFILL"
    assert conf >= 0.8


def test_appointment(classifier):
    intent, conf = classifier.classify("Book appointment with Dr. Sharma")
    assert intent == "HC_APPOINTMENT"


def test_entities(classifier):
    entities = classifier.extract_entities("Refill my Lisinopril tomorrow")
    assert entities.get("medication") == "Lisinopril"
