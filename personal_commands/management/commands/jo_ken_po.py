from django.core.management.base import BaseCommand
import random
import time


class Command(BaseCommand):
    start = """
      _____             ______                    ______
-----/ __  |      -----/ _____)_______      -----/ __  |_______
      (__| |)                 ________)              | |________)
 1    (__|_|)        2        __________)      3     |_|__________)
____  (_____)     ____        ________)     ____  (_____)
    \_(____)          \____________)            \_(____)
    """

    jo = """
      _____ 
-----/ __  |
      (__| |)
      (__|_|)
____  (_____)
    \_(____)
    """

    ken = """
      ______
-----/ _____)_______
            ________)
            __________)
____        ________)
    \____________)
    """

    po = """
      ______
-----/ __  |_______
         | |________)
         |_|__________)
____  (_____)
    \_(____)
    """
    options = ["jo", "ken", "po"]

    banners = {
        "jo": jo,
        "ken": ken,
        "po": po
    }

    translated = {
        "jo": "Pedra",
        "ken": "Papel",
        "po": "Tesoura"
    }

    valid_options = ("1", "2", "3")

    def play_bot(self):
        random_option = self.options[random.randrange(0, len(self.options))]
        return random_option

    def is_winner(self, bot_move: str, user_move: str) -> int:
        if user_move not in self.valid_options:
            return 2

        user_move = int(user_move)
        user_move = self.options[user_move - 1]

        print(f"O computador escolheu: {self.translated[bot_move]}")
        print(self.banners[bot_move])
        time.sleep(1)
        print(f"Você escolheu: {self.translated[user_move]}")
        print(self.banners[user_move])
        time.sleep(1)
        print(10 * "=")

        if bot_move == "jo" and user_move == "po":
            return -1

        if bot_move == "ken" and user_move == "jo":
            return -1

        if bot_move == "po" and user_move == "ken":
            return -1

        if bot_move == user_move:
            return 0

        return 1

    def cat_banner(self, move):
        return self.banners[move]

    def handle(self, *_, **__):

        while True:
            print(self.start)
            time.sleep(1)
            print("Escolha um número de 1 a 3 de acordo com a imagem acima.")
            time.sleep(0.5)
            user_move = input("Escolha sua jogada: ")
            print(10 * "=")
            bot_move = self.play_bot()

            is_winner = self.is_winner(bot_move=bot_move, user_move=user_move)

            if is_winner == 1:
                print(f"{10 * '=~'}Você ganhou!{10 * '=~'}")
                time.sleep(1)
            if is_winner == -1:
                print(f"{10 * '=~'}O computador ganhou!{10 * '=~'}")
                time.sleep(1)
            if is_winner == 0:
                print(f"{10 * '=~'}Deu empate!{10 * '=~'}")
                time.sleep(1)
            if is_winner == 2:
                print(f"{10 * '=~'}Opção inválida, tente de novo!{10 * '=~'}")
                time.sleep(1)