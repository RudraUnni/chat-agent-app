import os
import asyncio
import subprocess
import time
import socket
import pytest


def _is_port_open(host: str, port: int, timeout: float = 0.2) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False


@pytest.fixture(scope="session", autouse=True)
def start_backend_server():
    # Use SQLite for tests to avoid requiring Postgres
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

    # Start uvicorn in background
    proc = subprocess.Popen(
        [
            os.path.join("backend", ".venv", "bin", "uvicorn")
            if os.path.exists(os.path.join("backend", ".venv", "bin", "uvicorn"))
            else os.path.join(".venv", "bin", "uvicorn"),
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--app-dir",
            "backend",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait until port is open
    for _ in range(100):
        if _is_port_open("localhost", 8000):
            break
        time.sleep(0.1)
    else:
        try:
            proc.kill()
        finally:
            raise RuntimeError("Failed to start backend server for tests")

    yield

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def user_id():
    # Default user id will be created automatically on first WS connect, but tests expect fixture
    import requests
    resp = requests.post("http://localhost:8000/api/v1/users/dummy")
    resp.raise_for_status()
    return resp.json()["id"]


@pytest.fixture
def conversation_id():
    # Generate a random conversation id for test cases
    import uuid
    return str(uuid.uuid4())

