from requests import PreparedRequest, Response


class Monitor:

    def success(self, service: str, request: PreparedRequest, response: Response):
        pass

    def failure(self, service: str, request: PreparedRequest, response: Response):
        pass

    def trip(self, service: str):
        pass

    def reset(self, service: str):
        pass
