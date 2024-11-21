import time

# Ensemble pour suivre les processus en état de crash
crashed_processes = set()


# Fonction pour valider une commande entrée par l'utilisateur
def is_valid_command(command):
    parts = command.split()  # Découpe la commande en parties
    if len(parts) == 0:  # Vérifie que la commande n'est pas vide
        return False
    if parts[0] == "START" and len(parts) == 1:  # Commande 'START' valide sans arguments supplémentaires
        return True
    if parts[0] == "EXIT" and len(parts) == 1:  # Commande 'EXIT' valide sans arguments supplémentaires
        return True
    if parts[0] == "CRASH":  # Commande 'CRASH'
        if len(parts) == 1:  # Crash global
            return True
        elif len(parts) == 2 and parts[1].isdigit():  # Crash pour un processus spécifique
            return True
    if parts[0] == "SPEED":  # Commande 'SPEED'
        if len(parts) == 2 and parts[1].lower() in {"low", "medium", "high"}:  # Vitesse globale
            if "global" in crashed_processes:  # Refus si un crash global est actif
                print("REPL: Commande SPEED impossible après un CRASH global.")
                return False
            return True
        if len(parts) == 3 and parts[1].isdigit() and parts[2].lower() in {"low", "medium", "high"}:  # Vitesse pour un processus spécifique
            if int(parts[1]) in crashed_processes or "global" in crashed_processes:  # Refus si le processus est en crash
                print(f"REPL: Commande SPEED impossible pour le processus {parts[1]} en état de crash.")
                return False
            return True
    return False  # Commande invalide


# Fonction principale de la REPL
def main():
    history_file = "step3/repl_history.txt"  # Fichier pour stocker l'historique des commandes
    has_started = False  # Indicateur pour vérifier si 'START' a été exécuté

    while True:  # Boucle REPL
        command = input("REPL> ").strip()  # Demande une commande utilisateur

        if command == "EXIT":  # Arrête la REPL
            with open(history_file, "a") as history:
                history.write(command + "\n")  # Sauvegarde la commande dans le fichier historique
            print(f"REPL: Commande '{command}' écrite dans {history_file}.")
            break  # Sortie de la boucle REPL

        if not has_started and command != "START":  # Bloque toute commande avant 'START'
            print("REPL: Veuillez exécuter 'START' en premier.")
            continue

        if command == "START":  # Active le système pour la première fois
            if has_started:  # Empêche d'exécuter 'START' plusieurs fois
                print("REPL: Commande 'START' impossible car déjà exécutée.")
                continue
            has_started = True

        if not is_valid_command(command):  # Vérifie si la commande est valide
            print("REPL: Commande invalide.")
            continue

        # Analyse et traitement des commandes spécifiques
        parts = command.split()
        if parts[0] == "CRASH":  # Gestion de la commande 'CRASH'
            if len(parts) == 1:  # Crash global
                crashed_processes.add("global")  # Ajoute un indicateur de crash global
                print("REPL: Crash global activé.")
            else:  # Crash pour un processus spécifique
                crashed_processes.add(int(parts[1]))
                print(f"REPL: Crash pour le processus {parts[1]} activé.")

        # Enregistre la commande valide dans le fichier historique
        with open(history_file, "a") as history:
            history.write(command + "\n")
        print(f"REPL: Commande '{command}' écrite dans {history_file}.")
        time.sleep(0.5)  # Légère pause pour éviter les conflits d'accès


# Lancement de la REPL si le script est exécuté directement
if __name__ == "__main__":
    main()
