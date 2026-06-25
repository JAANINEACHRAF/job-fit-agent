from job_fit_agent.models import JobOffer

SAMPLE = {
    "id": "209QPYK",
    "intitule": "DATA SCIENTIST - RECHERCHE (H/F)",
    "description": "Analyse de données...",
    "entreprise": {"nom": "CHU Montpellier"},
    "lieuTravail": {"libelle": "34 - MONTPELLIER"},
    "typeContratLibelle": "CDD",
    "origineOffre": {"urlOrigine": "https://candidat.francetravail.fr/offres/209QPYK"},
}


def test_from_api_parses_core_fields():
    job = JobOffer.from_api(SAMPLE)
    assert job.id == "209QPYK"
    assert job.title == "DATA SCIENTIST - RECHERCHE (H/F)"
    assert job.company == "CHU Montpellier"
    assert job.location == "34 - MONTPELLIER"
    assert job.contract_type == "CDD"


def test_from_api_handles_missing_fields():
    job = JobOffer.from_api({"id": "X", "intitule": "Dev"})
    assert job.id == "X"
    assert job.company is None
    assert job.location is None


def test_from_api_handles_null_nested_objects():
    """France Travail can return nested objects as explicit null (e.g. anonymized
    offers with entreprise: null), which must not crash from_api."""
    raw = {
        "id": "Y",
        "intitule": "Data Scientist",
        "entreprise": None,
        "lieuTravail": None,
        "origineOffre": None,
    }
    job = JobOffer.from_api(raw)
    assert job.id == "Y"
    assert job.company is None
    assert job.location is None
    assert job.url is None
