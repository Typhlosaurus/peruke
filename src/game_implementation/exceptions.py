class DiscStateException(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IllegalMoveException(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
