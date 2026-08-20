"""Run the SATURN core."""

from .runtime import SaturnCore


def main() -> None:
    core = SaturnCore()
    status = core.start()
    print(f"SATURN CORE: {status.state.upper()}")
    print(f"Started: {status.started_at}")


if __name__ == "__main__":
    main()
