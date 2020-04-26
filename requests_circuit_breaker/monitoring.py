from requests import PreparedRequest, Response


class Monitor:

    def success(self, service: str, request: PreparedRequest, response: Response, elapsed: int):
        pass

    def failure(self, service: str, request: PreparedRequest, response: Response, elapsed: int):
        pass

    def trip(self, service: str):
        pass

    def reset(self, service: str):
        pass
