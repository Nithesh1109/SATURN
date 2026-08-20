from saturn.core.runtime import SaturnCore


def test_core_starts_online() -> None:
    core = SaturnCore()

    status = core.start()

    assert status.state == "online"
    assert status.started_at


def test_core_stops_offline() -> None:
    core = SaturnCore()
    core.start()

    status = core.stop()

    assert status.state == "offline"
