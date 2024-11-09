import time

crashed_processes = set()


def is_valid_command(command):
    parts = command.split()
    if len(parts) == 0:
        return False
    if parts[0] == "START" and len(parts) == 1:
        return True
    if parts[0] == "EXIT" and len(parts) == 1:
        return True
    if parts[0] == "CRASH":
        if len(parts) == 1:
            return True
        elif len(parts) == 2 and parts[1].isdigit():
            return True
    if parts[0] == "SPEED":
        if len(parts) == 2 and parts[1].lower() in {"low", "medium", "high"}:
            if "global" in crashed_processes:
                print("REPL: Commande SPEED impossible après un CRASH global.")
                return False
            return True
        if len(parts) == 3 and parts[1].isdigit() and parts[2].lower() in {"low", "medium", "high"}:
            if int(parts[1]) in crashed_processes or "global" in crashed_processes:
                print(f"REPL: Commande SPEED impossible pour le processus {parts[1]} en état de crash.")
                return False
            return True
    return False


def main():
    history_file = "step3/repl_history.txt"
    has_started = False
    while True:
        command = input("REPL> ").strip()

        if command == "EXIT":
            with open(history_file, "a") as history:
                history.write(command + "\n")
            print(f"REPL: Commande '{command}' écrite dans {history_file}.")
            break

        if not has_started and command != "START":
            print("REPL: Veuillez exécuter 'START' en premier.")
            continue

        if command == "START":
            if has_started:
                print("REPL: Commande 'START' impossible car déjà exécutée.")
                continue
            has_started = True

        if not is_valid_command(command):
            print("REPL: Commande invalide.")
            continue

        parts = command.split()
        if parts[0] == "CRASH":
            if len(parts) == 1:
                crashed_processes.add("global")
                print("REPL: Crash global activé.")
            else:
                crashed_processes.add(int(parts[1]))
                print(f"REPL: Crash pour le processus {parts[1]} activé.")

        with open(history_file, "a") as history:
            history.write(command + "\n")
        print(f"REPL: Commande '{command}' écrite dans {history_file}.")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
