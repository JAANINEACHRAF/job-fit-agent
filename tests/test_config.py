from job_fit_agent.config import Settings


def test_settings_have_defaults():
    s = Settings()
    assert s.ft_token_url.startswith("https://")
    assert s.ft_api_base.startswith("https://")
