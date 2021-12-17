from gevent.monkey import patch_all  # type: ignore

patch_all()

import socket  # noqa: E402

import psutil  # type: ignore  # noqa: E402
from gevent.pywsgi import WSGIServer  # type: ignore  # noqa: E402

from app import app  # noqa: E402

if __name__ == "__main__":
    for key, v in psutil.net_if_addrs().items():
        ipv4 = tuple(x.address for x in v if x.family == socket.AF_INET)
        ipv6 = tuple(x.address for x in v if x.family == socket.AF_INET6)
        print(f"{key}:")
        for name, list in {"IP v4": ipv4, "IP v6": ipv6}.items():
            if len(list):
                print(f"\t{name}:")
                for x in list:
                    print(f"\t\t{x}")
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()
