from gevent.monkey import patch_all  # type: ignore

patch_all()

from gevent.pywsgi import WSGIServer  # type: ignore  # noqa: E402

from app import app  # noqa: E402

if __name__ == "__main__":
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()
