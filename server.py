import threading
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple

from flask import Flask, Response, jsonify, request
from sqlalchemy import BLOB, TIMESTAMP, Column, Integer, create_engine  # type: ignore
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore
from sqlalchemy.sql import func  # type: ignore

engine = create_engine("sqlite:///figview.db", echo=True, encoding="utf-8")
Base = declarative_base()


class Figure(Base):  # type: ignore
    __tablename__ = "figure"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    figure: int = Column(Integer, nullable=False)
    file: bytes = Column(BLOB, nullable=False)
    timestamp: datetime = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        return (
            f"<Figure(id={self.id}, figure={self.figure}, "
            f'timestamp="{self.timestamp}")>'
        )


Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
_sessions: Dict[int, Any] = {}


def get_session() -> Any:
    id = threading.get_ident()
    if id not in _sessions:
        _sessions[id] = Session()
    return _sessions[id]


def CORS(f: Callable[[], Response]) -> Callable[[], Response]:
    @wraps(f)
    def decorator() -> Response:
        response = f()
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    return decorator


app = Flask(__name__)


@app.route("/")
def index() -> str:
    with open("main.html", encoding="utf-8") as f:
        return f.read()


@app.route("/figure")
@CORS
def figure() -> Response:
    try:
        id = request.args["id"]
        (fig,) = get_session().query(Figure).filter_by(id=id).all()
        return Response(fig.file, mimetype="image/svg+xml")
    except BaseException as e:
        return Response(f"type={type(e)}, e={e}", status=404)


@app.route("/addfig", methods=["POST"])
@CORS
def addfig() -> Response:
    figure = request.args["fig"]
    fig = Figure(figure=figure, file=request.get_data())
    session = get_session()
    session.add(fig)
    session.commit()
    return Response()


@app.route("/listfig")
@CORS
def listfig() -> Response:
    figs: List[Figure] = get_session().query(Figure).all()
    res: Dict[int, List[Tuple[datetime, int]]] = {}
    for f in figs:
        if f.figure not in res:
            res[f.figure] = []
        res[f.figure].append((f.timestamp, f.id))

    def key(x: Tuple[datetime, int]) -> datetime:
        return x[0]

    return jsonify(
        [
            {
                "figure": fid,
                "name": f"figure-id{fid}",
                "id_list": [
                    {
                        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "id": id,
                        "src": f"figure?id={id}",
                    }
                    for time, id in sorted(figs, key=key, reverse=True)
                ],
            }
            for fid, figs in sorted(res.items(), key=lambda f: f[0])
        ]
    )


if __name__ == "__main__":
    app.run()
