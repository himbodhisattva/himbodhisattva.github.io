#!/usr/bin/env python3
"""Serve the local site with byte-range support for audio seeking."""
from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
import os
import re
from urllib.parse import urlsplit


def parse_byte_range(header: str, size: int) -> tuple[int, int]:
    """Return an inclusive byte range or raise ValueError."""
    if size <= 0 or not header.startswith("bytes="):
        raise ValueError("invalid byte range")
    value = header.removeprefix("bytes=")
    if "," in value or "-" not in value:
        raise ValueError("multiple or malformed ranges are unsupported")
    start_text, end_text = value.split("-", 1)
    if not start_text:
        suffix = int(end_text)
        if suffix <= 0:
            raise ValueError("invalid suffix range")
        return max(0, size - suffix), size - 1

    start = int(start_text)
    if start < 0 or start >= size:
        raise ValueError("range starts outside the file")
    end = size - 1 if not end_text else min(int(end_text), size - 1)
    if end < start:
        raise ValueError("range ends before it starts")
    return start, end


class RangeRequestHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with single-range GET and HEAD support."""

    byte_range: tuple[int, int] | None = None

    def end_headers(self) -> None:
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def records_shell_path(self) -> Path | None:
        """Resolve a source-preview song route through the records shell."""
        request_path = urlsplit(self.path).path
        parts = request_path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "records" or not re.fullmatch(r"[a-z0-9-]+", parts[1]):
            return None
        shell = Path(self.translate_path("/records/index.html"))
        return shell if shell.is_file() else None

    def send_records_shell(self, shell: Path):
        """Serve the records app at a nested song URL with a corrected base."""
        body = shell.read_bytes().replace(b'<base href="../">', b'<base href="../../">')
        stat = shell.stat()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
        self.end_headers()
        return BytesIO(body)

    def send_head(self):
        self.byte_range = None
        header = self.headers.get("Range")
        path = self.translate_path(self.path)
        shell = self.records_shell_path() if not os.path.exists(path) else None
        if shell:
            return self.send_records_shell(shell)
        if not header or os.path.isdir(path):
            return super().send_head()

        try:
            source = open(path, "rb")
        except OSError:
            return super().send_head()

        size = os.fstat(source.fileno()).st_size
        try:
            start, end = parse_byte_range(header, size)
        except (TypeError, ValueError):
            source.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        self.byte_range = (start, end)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(os.fstat(source.fileno()).st_mtime))
        self.end_headers()
        return source

    def copyfile(self, source, outputfile) -> None:
        if self.byte_range is None:
            return super().copyfile(source, outputfile)
        start, end = self.byte_range
        source.seek(start)
        remaining = end - start + 1
        while remaining:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            try:
                outputfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                break
            remaining -= len(chunk)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--directory", type=Path, default=Path.cwd())
    args = parser.parse_args()
    handler = partial(RangeRequestHandler, directory=str(args.directory))
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(f"Serving {args.directory} at http://{args.host}:{args.port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
