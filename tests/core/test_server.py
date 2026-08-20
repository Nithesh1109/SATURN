import json
from http.client import HTTPConnection
from threading import Thread
from http.server import ThreadingHTTPServer

from saturn.core.server import CoreRequestHandler


def test_health_endpoint() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), CoreRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/health")
        response = connection.getresponse()
        payload = json.loads(response.read())

        assert response.status == 200
        assert payload["state"] == "offline"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_agent_run_endpoint() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), CoreRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request(
            "POST",
            "/agent/run",
            body=json.dumps({"goal": "ping"}),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        payload = json.loads(response.read())

        assert response.status == 200
        assert payload["response"]["text"] == "ping"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
