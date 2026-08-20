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
