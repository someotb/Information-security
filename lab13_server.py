import argparse
import json
import math
import secrets
import socketserver
import threading
from pathlib import Path

from crypto_lib import rsa_generate_keys
from lab13_common import DEFAULT_HOST, DEFAULT_PORT


KEY_FILE = Path("lab13_server_keys.json")
STATE_FILE = Path("lab13_server_state.json")

CHOICES = {
    0: "Да",
    1: "Нет",
    2: "Воздержался",
}


def load_or_create_keys():
    if KEY_FILE.exists():
        try:
            data = json.loads(KEY_FILE.read_text(encoding="utf-8"))
            required = ("n", "e", "d")
            if all(isinstance(data.get(key), int) for key in required):
                return data
        except (OSError, json.JSONDecodeError):
            pass

    # Учебные параметры. Это не промышленная длина RSA-ключа.
    keys = rsa_generate_keys(bits=64)
    KEY_FILE.write_text(json.dumps(keys, indent=4), encoding="utf-8")
    return keys


def load_state():
    if not STATE_FILE.exists():
        return {"issued_voters": [], "ballots": []}

    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if not isinstance(state.get("issued_voters"), list):
            raise ValueError("Некорректный список избирателей.")
        if not isinstance(state.get("ballots"), list):
            raise ValueError("Некорректный список бюллетеней.")
        return state
    except (OSError, json.JSONDecodeError, ValueError):
        print("Предупреждение: файл состояния повреждён. Создаём новое состояние.")
        return {"issued_voters": [], "ballots": []}


class VotingState:
    def __init__(self):
        self.keys = load_or_create_keys()
        self.state = load_state()
        self.lock = threading.Lock()

        self.n = self.keys["n"]
        self.e = self.keys["e"]
        self.d = self.keys["d"]

        print("Сервер анонимного голосования запущен.")
        print(f"Открытый ключ: n={self.n}, e={self.e}")
        print("Закрытый показатель d хранится только на сервере.")

    def public_key(self):
        return {"n": self.n, "e": self.e}

    def blind_sign(self, voter_id, blinded_message):
        voter_id = str(voter_id).strip()
        if not voter_id:
            raise ValueError("Идентификатор избирателя не может быть пустым.")
        if not isinstance(blinded_message, int):
            raise ValueError("Ослеплённое сообщение должно быть целым числом.")
        if not 0 <= blinded_message < self.n:
            raise ValueError("Ослеплённое сообщение находится вне диапазона RSA.")

        with self.lock:
            issued = set(self.state["issued_voters"])
            if voter_id in issued:
                raise ValueError("Этому избирателю уже выдавалась подпись.")

            # Сервер подписывает ослеплённое сообщение:
            # s' = (m')^d mod n.
            blind_signature = pow(blinded_message, self.d, self.n)

            self.state["issued_voters"].append(voter_id)
            self.save()

        print(
            f"Выдана слепая подпись избирателю {voter_id!r}: "
            f"m'={blinded_message}, s'={blind_signature}"
        )
        return {"blinded_signature": blind_signature}

    def submit_ballot(self, message, signature):
        if not isinstance(message, int) or not isinstance(signature, int):
            raise ValueError("Сообщение и подпись должны быть целыми числами.")
        if not 0 < message < self.n:
            raise ValueError("Сообщение бюллетеня вне диапазона RSA.")
        if not 0 <= signature < self.n:
            raise ValueError("Подпись находится вне диапазона RSA.")

        # Проверка обычной RSA-подписи: s^e mod n должно равняться m.
        if pow(signature, self.e, self.n) != message:
            raise ValueError("Подпись бюллетеня недействительна.")

        # m = nonce * 3 + choice. Остаток определяет вариант ответа.
        choice_code = message % 3
        nonce = message // 3
        if nonce == 0:
            raise ValueError("Некорректный номер бюллетеня.")

        with self.lock:
            used_messages = {
                ballot["message"] for ballot in self.state["ballots"]
            }
            if message in used_messages:
                raise ValueError("Этот бюллетень уже был принят.")

            self.state["ballots"].append({
                "message": message,
                "choice": choice_code,
            })
            self.save()

        print(
            f"Принят анонимный бюллетень: message={message}, "
            f"choice={CHOICES[choice_code]!r}"
        )
        return {"choice": CHOICES[choice_code]}

    def results(self):
        with self.lock:
            counts = {name: 0 for name in CHOICES.values()}
            for ballot in self.state["ballots"]:
                choice = ballot.get("choice")
                if choice in CHOICES:
                    counts[CHOICES[choice]] += 1

            return {
                "counts": counts,
                "total": sum(counts.values()),
            }

    def save(self):
        STATE_FILE.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )


VOTING = VotingState()


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            raw = self.rfile.readline(1024 * 1024)
            if not raw:
                return

            request = json.loads(raw.decode("utf-8"))
            action = request.get("action")

            if action == "public_key":
                result = {"ok": True, **VOTING.public_key()}

            elif action == "blind_sign":
                data = VOTING.blind_sign(
                    request.get("voter_id", ""),
                    request.get("blinded_message")
                )
                result = {"ok": True, **data}

            elif action == "submit_ballot":
                data = VOTING.submit_ballot(
                    request.get("message"),
                    request.get("signature")
                )
                result = {"ok": True, **data}

            elif action == "results":
                result = {"ok": True, **VOTING.results()}

            else:
                result = {"ok": False, "error": "Неизвестная команда."}

        except Exception as error:
            result = {"ok": False, "error": str(error)}

        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


class ThreadedServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(
        description="Сервер лабораторной работы №13 — слепая RSA-подпись."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    with ThreadedServer((args.host, args.port), RequestHandler) as server:
        print(f"Ожидание клиентов на {args.host}:{args.port}")
        print("Для остановки нажмите Ctrl+C.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")


if __name__ == "__main__":
    main()
