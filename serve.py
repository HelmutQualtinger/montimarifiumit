"""
Static file server with pre-compressed gzip support.

If a .gz counterpart exists and the client accepts gzip encoding,
the compressed file is served transparently.

Usage: python3 serve.py [port]
"""
import gzip
import http.server
import os
import sys


class GzipStaticHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        gz_path = path + ".gz"
        accepts_gzip = "gzip" in self.headers.get(
            "Accept-Encoding", ""
        )

        if (
            accepts_gzip
            and os.path.isfile(gz_path)
            and not os.path.isdir(path)
        ):
            try:
                f = open(gz_path, "rb")
            except OSError:
                self.send_error(404, "File not found")
                return None

            stat = os.fstat(f.fileno())
            # Determine content type from original filename
            ctype = self.guess_type(path)
            self.send_response(200)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(stat.st_size))
            self.send_header(
                "Last-Modified",
                self.date_time_string(stat.st_mtime),
            )
            self.end_headers()
            return f

        return super().send_head()

    def log_message(self, fmt, *args):
        path = self.path
        gz_path = self.translate_path(path) + ".gz"
        accepts_gzip = "gzip" in self.headers.get(
            "Accept-Encoding", ""
        )
        suffix = (
            " [gz]"
            if accepts_gzip and os.path.isfile(gz_path)
            else ""
        )
        super().log_message(fmt + suffix, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = http.server.HTTPServer(
        ("", port), GzipStaticHandler
    )
    print(f"Serving on http://localhost:{port}")
    print("Pre-compressed .gz files will be served automatically.")
    server.serve_forever()


if __name__ == "__main__":
    main()
