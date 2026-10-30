#!/usr/bin/env python3
"""The local preview server must support audio byte ranges for seeking."""
from functools import partial
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
spec = spec_from_file_location("serve", ROOT / "tools" / "serve.py")
module = module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)


class QuietRangeRequestHandler(module.RangeRequestHandler):
    def log_message(self, format, *args):
        pass


class ClosedOutput:
    def write(self, _chunk):
        raise BrokenPipeError


class PartialResponse:
    byte_range = (0, 9)


module.RangeRequestHandler.copyfile(PartialResponse(), BytesIO(b"0123456789"), ClosedOutput())


with TemporaryDirectory() as directory:
    root = Path(directory)
    (root / "sample.mp3").write_bytes(b"0123456789")
    (root / "records").mkdir()
    (root / "records" / "index.html").write_text('<base href="../">records shell')
    handler = partial(QuietRangeRequestHandler, directory=directory)
    server = module.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}/sample.mp3"
    try:
        with urlopen(Request(base, headers={"Range": "bytes=3-6"})) as response:
            assert response.status == 206
            assert response.headers["Content-Range"] == "bytes 3-6/10"
            assert response.headers["Accept-Ranges"] == "bytes"
            assert response.read() == b"3456"

        with urlopen(Request(base, headers={"Range": "bytes=-3"})) as response:
            assert response.status == 206
            assert response.read() == b"789"

        try:
            urlopen(Request(base, headers={"Range": "bytes=20-30"}))
        except HTTPError as error:
            assert error.code == 416
            assert error.headers["Content-Range"] == "bytes */10"
        else:
            raise AssertionError("out-of-range requests should return 416")

        with urlopen(f"http://127.0.0.1:{server.server_port}/records/my-art-machine-01/") as response:
            assert response.status == 200
            assert response.read() == b'<base href="../../">records shell'

        with urlopen(f"http://127.0.0.1:{server.server_port}/records/my-art-machine/") as response:
            assert response.status == 200
            assert response.read() == b'<base href="../../">records shell'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

print("PASS: local preview server supports audio byte ranges and direct record routes.")
