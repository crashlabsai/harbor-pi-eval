"""Loopback-only isolation. Static: every family whose environment compose
declares main network_mode: none must attach its sidecars via service:main.
Behavioural: a self-contained compose mirroring that pattern is loopback-only
(no egress, no DNS). Behavioural probe skipped if Docker is unavailable."""
import shutil
import subprocess
import textwrap
import uuid
from pathlib import Path

import pytest
import yaml

from conftest import SOURCES, families, family_ids


def _compose(family):
    p = SOURCES / family / "shared" / "environment" / "docker-compose.yaml"
    return yaml.safe_load(p.read_text()) if p.exists() else None


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_loopback_only_topology(family, spec, src):
    doc = _compose(family)
    if not doc:
        pytest.skip(f"{family} has no docker-compose.yaml")
    services = doc.get("services", {})
    main = services.get("main", {})
    if main.get("network_mode") != "none":
        pytest.skip(f"{family} main is not network_mode: none")
    # Every other service must join main's namespace (no independent network).
    for name, cfg in services.items():
        if name == "main":
            continue
        assert (cfg or {}).get("network_mode") == "service:main", \
            f"{family}: sidecar {name!r} must use network_mode: service:main"


docker = shutil.which("docker")


@pytest.mark.skipif(not docker, reason="docker not available")
def test_loopback_only_behaviour(tmp_path):
    project = f"pi-netcheck-{uuid.uuid4().hex[:8]}"
    (tmp_path / "sink.py").write_text(textwrap.dedent("""
        import http.server, socketserver
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
            def log_message(self, *a): pass
        socketserver.TCPServer(("0.0.0.0", 8080), H).serve_forever()
    """))
    (tmp_path / "docker-compose.yaml").write_text(textwrap.dedent("""
        services:
          main:
            image: python:3.12-slim
            network_mode: none
            command: ["sh", "-c", "sleep 300"]
          sink:
            image: python:3.12-slim
            network_mode: "service:main"
            volumes: ["./sink.py:/sink.py:ro"]
            command: ["sh", "-c", "python3 /sink.py"]
    """))

    def compose(*args):
        return subprocess.run(["docker", "compose", "-p", project, *args],
                              cwd=tmp_path, capture_output=True, text=True)

    try:
        up = compose("up", "-d")
        assert up.returncode == 0, up.stderr

        def exec_main(script):
            return compose("exec", "-T", "main", "python3", "-c", script)

        import time
        reach = None
        for _ in range(15):
            reach = exec_main("import urllib.request;"
                              "print(urllib.request.urlopen('http://127.0.0.1:8080/',timeout=3).read().decode())")
            if reach.returncode == 0:
                break
            time.sleep(1)
        assert reach.returncode == 0 and "ok" in reach.stdout, reach.stderr
        assert exec_main("import os;print(sorted(os.listdir('/sys/class/net')))").stdout.strip() == "['lo']"
        egress = exec_main("import socket;s=socket.socket();s.settimeout(4)\n"
                           "try:\n s.connect(('1.1.1.1',80));print('OPEN')\n"
                           "except Exception:\n print('BLOCKED')")
        assert "BLOCKED" in egress.stdout, egress.stdout
        dns = exec_main("import socket\n"
                        "try:\n socket.gethostbyname('example.com');print('RESOLVED')\n"
                        "except Exception:\n print('NODNS')")
        assert "NODNS" in dns.stdout, dns.stdout
    finally:
        compose("down", "-v")
