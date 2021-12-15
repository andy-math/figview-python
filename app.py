import threading
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from flask import Flask, Response, jsonify, request
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy import BLOB, TIMESTAMP, Column, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore
from sqlalchemy.sql import func  # type: ignore

engine = create_engine("sqlite:///figview.db", encoding="utf-8")
Base = declarative_base()


class Blobs(Base):  # type: ignore
    __tablename__ = "blobs"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    blob: bytes = Column(BLOB, nullable=False)


class Figure(Base):  # type: ignore
    __tablename__ = "figure"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    figure: int = Column(Integer, nullable=False)
    fileid: int = Column(
        Integer,
        ForeignKey("blobs.id", onupdate="restrict", ondelete="restrict"),
        nullable=False,
    )
    timestamp: datetime = Column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )

    def __repr__(self) -> str:
        return (
            f"<Figure(id={self.id}, "
            f"figure={self.figure}, "
            f"fileid={self.fileid}, "
            f'timestamp="{self.timestamp}")>'
        )


Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
_sessions: Dict[int, sessionmaker] = {}


def get_session() -> sessionmaker:
    id = threading.get_ident()
    if id not in _sessions:
        _sessions[id] = Session()
        print(f"add {_sessions[id]}")
    return _sessions[id]


app = Flask(__name__)


@app.route("/")
def index() -> str:
    with open("index.html", encoding="utf-8") as f:
        return f.read()


@app.route("/figure")
def figure() -> Response:
    try:
        id = request.args["id"]
        (fig,) = get_session().query(Blobs).filter_by(id=id).all()
        return Response(fig.blob, mimetype="image/svg+xml")
    except BaseException as e:
        return Response(f"type={type(e)}, e={e}", status=404)


@app.route("/addfig", methods=["POST"])
def addfig() -> Response:
    figure = request.args["fig"]
    session = get_session()
    blob = Blobs(blob=request.get_data())
    session.add(blob)
    session.commit()
    fig = Figure(figure=figure, fileid=blob.id)
    session.add(fig)
    session.commit()
    return Response()


@app.route("/listfig")
def listfig() -> Response:
    figs: List[Figure] = get_session().query(Figure).all()
    res: Dict[int, List[Tuple[datetime, int]]] = {}
    for f in figs:
        if f.figure not in res:
            res[f.figure] = []
        res[f.figure].append(
            (f.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None), f.fileid)
        )

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
