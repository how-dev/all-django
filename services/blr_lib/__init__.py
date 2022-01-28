import requests


class BRL:
    def __init__(self):
        pass

    @staticmethod
    def convert_to_cents(coin: float) -> int:
        return int(coin * 100)

    @staticmethod
    def convert_to_real(cents: int) -> float:
        return float(cents / 100)

    def actual_dollar(self, cents: bool = False):
        response = requests.get("https://economia.awesomeapi.com.br/json/last/USD")
        dollar = response.json()["USDBRL"]["high"]
        dollar = float(dollar)

        if cents is True:
            return self.convert_to_cents(dollar)

        return dollar

    def convert_coin(
        self, coin: float, cents: bool = False, real_to_dollar: bool = True
    ) -> dict:
        actual_dollar = self.actual_dollar()
        total_dollar = (
            coin / actual_dollar if real_to_dollar is True else coin * actual_dollar
        )
        coin_type = f'{"USD" if real_to_dollar is True else "BRL"}{" cents" if cents is True else ""}'

        output = {
            "coin_type": coin_type,
            "result": total_dollar,
            "converted_from": {
                "coin_type": "BRL" if real_to_dollar is True else "USD",
                "value": coin,
            },
        }

        if cents is True:
            output["value"] = self.convert_to_cents(total_dollar)

        return output
