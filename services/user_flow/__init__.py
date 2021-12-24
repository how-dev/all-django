from rest_framework import status


class GenericErrors:
    messages = {
        "failure": {"data": {"status": status.HTTP_401_UNAUTHORIZED, "result": "Some field is incorrect"}, "status": status.HTTP_401_UNAUTHORIZED},
        "success": {"data": {"status": status.HTTP_200_OK, "result": None}, "status": status.HTTP_200_OK}
    }

    def failure_result(self):
        return self.messages["failure"]

    def success_result(self, result):
        message = self.messages["success"]
        message["data"]["result"] = result

        return message
