import math
import secrets
import tkinter as tk
from tkinter import ttk, messagebox


# Учебная модель ментального покера.
# 65537 — простое число. Для каждого игрока выбирается показатель e,
# взаимно простой с p - 1. Поэтому существует обратный показатель d.
P = 65537
SUITS = ("♠", "♥", "♦", "♣")
RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")


def make_player_key():
    """Создаёт пару показателей e и d для коммутативного преобразования."""
    while True:
        e = secrets.randbelow(P - 3) + 2
        if math.gcd(e, P - 1) == 1:
            d = pow(e, -1, P - 1)
            return e, d


def card_name(value):
    """Преобразует число 1..52 в название карты."""
    card_id = value - 1
    rank = RANKS[card_id % 13]
    suit = SUITS[card_id // 13]
    return f"{rank}{suit}"


class MentalPokerApp:
    def __init__(self, root):
        self.root = root
        style = ttk.Style()
        style.theme_use("clam")

        self.root.configure(bg="#f0f0f0")

        style.configure(
            ".",
            font=("Arial", 11),
            foreground="#222222"
        )

        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", foreground="#222222")
        style.configure(
            "TLabelframe",
            background="#f0f0f0",
            foreground="#222222"
        )
        style.configure(
            "TLabelframe.Label",
            background="#f0f0f0",
            foreground="#222222"
        )
        style.configure("TButton", padding=6)
        self.root.title("Лабораторная работа №12 — Ментальный покер")
        self.root.geometry("980x720")
        self.root.minsize(820, 600)

        self.player_count = tk.IntVar(value=4)
        self.selected_player = tk.IntVar(value=1)

        self.keys = []
        self.deck = []
        self.hands = []
        self.board = []
        self.board_revealed = 0
        self.started = False

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Количество игроков (2–10):").pack(side="left")
        self.count_box = ttk.Spinbox(
            top, from_=2, to=10, width=5, textvariable=self.player_count
        )
        self.count_box.pack(side="left", padx=(8, 16))

        ttk.Button(top, text="Новая раздача", command=self.new_hand).pack(side="left")

        self.players_frame = ttk.LabelFrame(
            self.root, text="Карты игроков", padding=10
        )
        self.players_frame.pack(fill="x", padx=10, pady=5)

        private_frame = ttk.LabelFrame(
            self.root, text="Просмотр закрытых карт", padding=10
        )
        private_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(private_frame, text="Показать карты игрока:").pack(side="left")
        self.player_box = ttk.Combobox(
            private_frame, state="readonly", width=12
        )
        self.player_box.pack(side="left", padx=8)
        ttk.Button(
            private_frame, text="Открыть карты", command=self.show_player_cards
        ).pack(side="left")

        board_frame = ttk.LabelFrame(
            self.root, text="Общие карты стола", padding=10
        )
        board_frame.pack(fill="x", padx=10, pady=5)

        self.board_label = ttk.Label(
            board_frame, text="Раздача ещё не начата", font=("Arial", 16)
        )
        self.board_label.pack(anchor="w", pady=5)

        self.next_board_button = ttk.Button(
            board_frame, text="Открыть следующие общие карты",
            command=self.reveal_next_board, state="disabled"
        )
        self.next_board_button.pack(anchor="w")

        log_frame = ttk.LabelFrame(
            self.root, text="Ход криптографического протокола", padding=8
        )
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log = tk.Text(log_frame, height=15, wrap="word", state="disabled")
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        scrollbar.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scrollbar.set)

        self.status = ttk.Label(self.root, text="Готово к новой раздаче", padding=8)
        self.status.pack(fill="x")

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def encrypt_and_shuffle_deck(self, player_count):
        # Изначально в колоде числа 1..52. Ноль не используется:
        # ноль при возведении в степень остался бы нулём.
        deck = list(range(1, 53))
        keys = []

        for player in range(player_count):
            e, d = make_player_key()
            keys.append((e, d))

            # Коммутативный слой шифрования игрока.
            deck = [pow(card, e, P) for card in deck]

            # Игрок перемешивает всю зашифрованную колоду.
            secrets.SystemRandom().shuffle(deck)

            self.write_log(
                f"Игрок {player + 1}: зашифровал колоду своим слоем "
                f"(e={e}) и перемешал её."
            )

        return deck, keys

    def decrypt_card(self, encrypted_card, owner=None):
        """
        Снимает все слои шифрования.
        Для закрытой карты владелец снимает свой слой последним.
        Для общей карты слои снимаются всеми игроками.
        """
        order = [i for i in range(len(self.keys)) if i != owner]
        if owner is not None:
            order.append(owner)

        value = encrypted_card
        for player in order:
            e, d = self.keys[player]
            value = pow(value, d, P)

        return value

    def new_hand(self):
        try:
            count = int(self.player_count.get())
        except (ValueError, tk.TclError):
            messagebox.showerror("Ошибка", "Введите количество игроков от 2 до 10.")
            return

        if not 2 <= count <= 10:
            messagebox.showerror("Ошибка", "Количество игроков должно быть от 2 до 10.")
            return

        self.clear_log()
        self.write_log(f"Открытый параметр протокола: p = {P}.")
        self.write_log("Создаём колоду из 52 карт и начинаем шифрование.")

        self.deck, self.keys = self.encrypt_and_shuffle_deck(count)
        self.hands = [[] for _ in range(count)]
        self.board = []
        self.board_revealed = 0

        position = 0

        # Две закрытые карты каждому игроку, по одной за круг.
        for _ in range(2):
            for player in range(count):
                self.hands[player].append(self.deck[position])
                position += 1

        # Сжигаем по одной карте перед флопом, тёрном и ривером.
        position += 1
        self.board = self.deck[position:position + 3]
        position += 3
        position += 1
        self.board.append(self.deck[position])
        position += 1
        position += 1
        self.board.append(self.deck[position])

        self.started = True
        self.player_box["values"] = [
            f"Игрок {i + 1}" for i in range(count)
        ]
        self.player_box.current(0)

        for child in self.players_frame.winfo_children():
            child.destroy()

        for i in range(count):
            ttk.Label(
                self.players_frame,
                text=f"Игрок {i + 1}: две закрытые карты",
                padding=4
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=8)

        self.board_label.configure(text="Общие карты пока закрыты")
        self.next_board_button.configure(state="normal")
        self.status.configure(text=f"Раздача начата: {count} игроков.")
        self.write_log(
            "Карты розданы в зашифрованном виде. "
            "Пока ни одна карта не раскрыта."
        )
        self.write_log(
            "Чтобы посмотреть закрытые карты, выберите игрока. "
            "Общие карты открываются по этапам: флоп, тёрн, ривер."
        )

    def show_player_cards(self):
        if not self.started:
            messagebox.showinfo("Информация", "Сначала начните новую раздачу.")
            return

        index = self.player_box.current()
        if index < 0:
            return

        cards = [
            card_name(self.decrypt_card(card, owner=index))
            for card in self.hands[index]
        ]
        self.write_log(
            f"Игрок {index + 1} получает свои карты. "
            "Слои остальных игроков снимаются первыми, "
            "слой владельца — последним."
        )
        messagebox.showinfo(
            f"Закрытые карты игрока {index + 1}",
            " ".join(cards)
        )

    def reveal_next_board(self):
        if not self.started:
            return

        if self.board_revealed == 0:
            count = 3
            stage = "Флоп"
        elif self.board_revealed < 5:
            count = 1
            stage = "Тёрн" if self.board_revealed == 3 else "Ривер"
        else:
            self.status.configure(text="Все общие карты уже открыты.")
            return

        start = self.board_revealed
        end = min(start + count, 5)
        revealed = [
            card_name(self.decrypt_card(card, owner=None))
            for card in self.board[start:end]
        ]
        self.board_revealed = end

        current = [
            card_name(self.decrypt_card(card, owner=None))
            for card in self.board[:self.board_revealed]
        ]
        self.board_label.configure(text="   ".join(current))
        self.write_log(
            f"{stage}: все игроки последовательно снимают свои слои. "
            f"Открыты карты: {' '.join(revealed)}."
        )

        if self.board_revealed == 5:
            self.next_board_button.configure(state="disabled")
            self.status.configure(text="Все пять общих карт открыты.")
        else:
            self.status.configure(
                text=f"Открыт этап «{stage}». Можно продолжить."
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = MentalPokerApp(root)
    root.mainloop()
