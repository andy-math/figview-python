import traceback

import requests  # type: ignore


def send(filename: str, figure_no: int) -> bool:
    with open(filename, "rb") as f:
        try:
            assert (
                200
                == requests.post(
                    f"http://127.0.0.1:5000/addfig?fig={int(figure_no)}", data=f.read()
                ).status_code
            )
            return True
        except BaseException as e:
            print(f"\n\n异常！type(e) = {type(e)}, e = {e}\n\n", end="")
            traceback.print_exc(chain=False)
            return False
