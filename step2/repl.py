import time

# Ensemble pour suivre les processus en état de "CRASH"
crashed_processes = set()


# Fonction pour vérifier si une commande est valide
def is_valid_command(command):
    parts = command.split()  # Divise la commande en parties
    if len(parts) == 0:  # Si la commande est vide, elle est invalide
        return False
    if parts[0] == "START" and len(parts) == 1:  # La commande START doit être utilisée seule
        return True
    if parts[0] == "EXIT" and len(parts) == 1:  # La commande EXIT doit être utilisée seule
        return True
    if parts[0] == "CRASH":  # Vérifie les conditions pour une commande CRASH
        if len(parts) == 1:  # CRASH global
            return True
        elif len(parts) == 2 and parts[1].isdigit():  # CRASH spécifique à un processus
            return True
    if parts[0] == "SPEED":  # Vérifie les conditions pour une commande SPEED
        if len(parts) == 2 and parts[1].lower() in {"low", "medium", "high"}:  # SPEED global
            if "global" in crashed_processes:  # Si un crash global est actif, rejet de la commande
                print("REPL: Commande SPEED impossible après un CRASH global.")
                return False
            return True
        if len(parts) == 3 and parts[1].isdigit() and parts[2].lower() in {"low", "medium", "high"}:
            if int(parts[1]) in crashed_processes or "global" in crashed_processes:  # SPEED spécifique mais crashé
                print(f"REPL: Commande SPEED impossible pour le processus {parts[1]} en état de crash.")
                return False
            return True
    return False  # La commande ne correspond à aucune des conditions valides


# Fonction principale du REPL
def main():
    history_file = "step2/repl_history.txt"  # Fichier pour sauvegarder l'historique des commandes
    has_started = False
    while True:
        # Invite de commande pour entrer une commande
        command = input("REPL> ").strip()

        # Gestion de la commande EXIT
        if command == "EXIT":
            with open(history_file, "a") as history:
                history.write(command + "\n")  # Enregistre la commande dans l'historique
            print(f"REPL: Commande '{command}' écrite dans {history_file}.")
            break

        # Si START n'a pas été exécuté en premier, toutes les autres commandes sont interdites
        if not has_started and command != "START":
            print("REPL: Veuillez exécuter 'START' en premier.")
            continue

        # Gestion de la commande START
        if command == "START":
            if has_started:  # Empêche d'exécuter START plusieurs fois
                print("REPL: Commande 'START' impossible car déjà exécutée.")
                continue
            has_started = True

        # Vérifie si la commande est valide
        if not is_valid_command(command):
            print("REPL: Commande invalide.")  # Message d'erreur pour commande non conforme
            continue

        # Traitement des commandes spécifiques
        parts = command.split()
        if parts[0] == "CRASH":
            if len(parts) == 1:  # CRASH global
                crashed_processes.add("global")
                print("REPL: Crash global activé.")
            else:  # CRASH spécifique
                crashed_processes.add(int(parts[1]))
                print(f"REPL: Crash pour le processus {parts[1]} activé.")

        # Enregistre la commande dans l'historique
        with open(history_file, "a") as history:
            history.write(command + "\n")
        print(f"REPL: Commande '{command}' écrite dans {history_file}.")
        time.sleep(0.5)  # Petite pause pour simuler un délai


if __name__ == "__main__":
    main()
