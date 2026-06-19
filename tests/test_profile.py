from job_fit_agent.profile import CandidateProfile, load_profile


def test_profile_loads_and_validates():
    p = load_profile()
    assert isinstance(p, CandidateProfile)
    assert p.name
    assert p.skills


def test_prompt_context_is_nonempty_text():
    ctx = load_profile().to_prompt_context()
    assert isinstance(ctx, str)
    assert "AI Engineer" in ctx
