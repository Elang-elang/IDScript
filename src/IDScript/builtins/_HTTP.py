from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from typing import Any

from IDScript.maker import IDSFunction, IDSModule, unwrap_py_value


def _normalize_response(value: Any) -> tuple[int, dict[str, str], bytes]:
    value = unwrap_py_value(value)
    if isinstance(value, bytes):
        return 200, {"Content-Type": "application/octet-stream"}, value
    if isinstance(value, str):
        return 200, {"Content-Type": "text/plain; charset=utf-8"}, value.encode("utf-8")
    if isinstance(value, dict):
        status = int(value.get("status", 200))
        headers = {str(k): str(v) for k, v in dict(value.get("headers", {})).items()}
        body = value.get("body", "")
        if isinstance(body, bytes):
            data = body
        else:
            data = str(body).encode("utf-8")
        headers.setdefault("Content-Type", "text/plain; charset=utf-8")
        return status, headers, data
    return 200, {"Content-Type": "text/plain; charset=utf-8"}, str(value).encode("utf-8")


def _handler_for(routes: dict[str, Any]):
    normalized_routes = {str(path): unwrap_py_value(value) for path, value in routes.items()}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self._handle()

        def do_POST(self):
            self._handle()

        def do_PUT(self):
            self._handle()

        def do_PATCH(self):
            self._handle()

        def do_DELETE(self):
            self._handle()

        def log_message(self, _format, *args):
            return

        def _handle(self):
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                body = self.rfile.read(length) if length else b""
                route = normalized_routes.get(self.path.split("?", 1)[0])
                if route is None:
                    status, headers, data = 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not Found"
                else:
                    request = {
                        "method": self.command,
                        "path": self.path,
                        "headers": dict(self.headers),
                        "body": body.decode("utf-8", errors="replace"),
                    }
                    result = route(request) if callable(route) else route
                    status, headers, data = _normalize_response(result)
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except BaseException as error:
                data = str(error).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

    return Handler


@IDSFunction(name="buat_server", declare="public", arguments={"host": str, "port": int, "routes": dict}, annotation=Any)
def _buat_server(host: str, port: int, routes: dict) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, int(port)), _handler_for(dict(routes)))
    server.daemon_threads = True
    return server


@IDSFunction(name="jalankan", declare="public", arguments={"server": Any}, annotation=None)
def _jalankan(server: Any) -> None:
    unwrap_py_value(server).serve_forever()


@IDSFunction(name="jalankan_thread", declare="public", arguments={"server": Any}, annotation=Any)
def _jalankan_thread(server: Any) -> threading.Thread:
    server = unwrap_py_value(server)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


@IDSFunction(name="hentikan", declare="public", arguments={"server": Any}, annotation=None)
def _hentikan(server: Any) -> None:
    server = unwrap_py_value(server)
    server.shutdown()
    server.server_close()


@IDSFunction(name="respons", declare="public", arguments={"teks": str, "status": int, "headers": dict}, annotation=dict)
def _respons(teks: str, status: int, headers: dict) -> dict:
    return {"body": teks, "status": int(status), "headers": dict(headers)}


@IDSModule(name="_HTTP", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_buat_server, _jalankan, _jalankan_thread, _hentikan, _respons)
    if __name__ == "__main__":
        cls.write()
