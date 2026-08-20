from saturn.core.api import CoreAPI


def test_api_starts_and_reports_health() -> None:
    api = CoreAPI()

    assert api.health()["state"] == "offline"

    status = api.start()

    assert status["state"] == "online"
    assert api.health()["state"] == "online"


def test_api_stops_core() -> None:
    api = CoreAPI()
    api.start()

    status = api.stop()

    assert status["state"] == "offline"


def test_api_runs_agent_task() -> None:
    api = CoreAPI()

    result = api.run_task("hello saturn")

    assert result["response"]["text"] == "hello saturn"
    assert result["success"] is True
