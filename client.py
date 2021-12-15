import requests  # type: ignore


def send(filename: str, figure_no: int) -> None:
    with open(filename, "rb") as f:
        response = requests.post(
            f"http://127.0.0.1:5000/addfig?fig={int(figure_no)}", data=f.read()
        )
        assert response.status_code == 200
