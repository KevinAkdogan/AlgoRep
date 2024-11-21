from mpi4py import MPI
from datetime import datetime
import time
import os


# Génère une commande unique pour un client, incluant son rang et un horodatage
def generate_command(rk):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Commande de client {rk} à {timestamp}"


# Écrit le journal (log) du serveur dans un fichier texte
def write_log_to_file(rk, lg):
    filename = f"log_server_{rk}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(lg))  # Écrit chaque entrée du journal sur une nouvelle ligne
    print(f"Serveur {rk}: historique enregistré dans {filename}")


# Lit la dernière commande stockée dans le fichier repl_history.txt
def read_last_command():
    filename = "step2/repl_history.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            commands = f.readlines()
            return commands[-1].strip() if commands else None  # Retourne la dernière commande si disponible
    return None


# Initialisation de MPI
comm = MPI.COMM_WORLD  # Objet de communication pour interagir avec les processus
rank = comm.Get_rank()  # Identifiant unique du processus courant
size = comm.Get_size()  # Nombre total de processus dans le système

# Définition des rôles
N_CLIENTS = 2  # Nombre de clients
N_SERVERS = size - N_CLIENTS  # Nombre de serveurs

# Variables de contrôle globales
speed = "low"  # Vitesse par défaut
is_crashed = False  # État de crash
has_started = False  # Indicateur de démarrage
last_command = None  # Dernière commande exécutée

# ------------------------------- Client -------------------------------
if rank < N_CLIENTS:
    while True:
        # Lit la dernière commande issue du fichier REPL
        command = read_last_command()
        # Vérifie si la commande START a été exécutée
        if command == "START" and not has_started:
            has_started = True
            print(f"Client {rank} : Démarrage autorisé.")

        # Traite les commandes issues du REPL
        if has_started and command != last_command:
            parts = command.split()
            if parts[0] == "SPEED":  # Commande pour changer la vitesse
                if len(parts) == 2:
                    speed = parts[1]
                    print(f"Client {rank}: Vitesse mise à jour à {speed}")
                elif len(parts) == 3 and int(parts[1]) == rank:  # Vitesse spécifique pour un client
                    speed = parts[2]
                    print(f"Client {rank}: Vitesse spécifique mise à jour à {speed}")
            elif parts[0] == "CRASH":  # Commande pour simuler un crash
                if len(parts) == 1:  # Crash global
                    is_crashed = True
                    print(f"Client {rank}: En état de crash global.")
                elif len(parts) == 2 and int(parts[1]) == rank:  # Crash spécifique
                    is_crashed = True
                    print(f"Client {rank}: En état de crash spécifique.")
            last_command = command

        # Envoie les commandes aux serveurs si le client est actif
        if has_started and not is_crashed:
            generated_command = generate_command(rank)
            for server in range(N_CLIENTS, N_CLIENTS + N_SERVERS):
                comm.send(generated_command, dest=server, tag=0)  # Envoi de la commande
            print(f"Client {rank} : Commande envoyée '{generated_command}'")

            # Applique un délai basé sur la vitesse
            if speed == "low":
                time.sleep(10)
            elif speed == "medium":
                time.sleep(2)
            elif speed == "high":
                time.sleep(0.5)

# ------------------------------- Serveur -------------------------------
elif rank >= N_CLIENTS:
    log = []  # Initialise le journal local
    while True:
        # Lit la dernière commande issue du fichier REPL
        command = read_last_command()
        if command and command != last_command:
            parts = command.split()
            if parts[0] == "SPEED":  # Commande pour changer la vitesse
                if len(parts) == 2:
                    speed = parts[1]
                    print(f"Serveur {rank}: Vitesse définie à {speed}")
                elif len(parts) == 3 and int(parts[1]) == rank:  # Vitesse spécifique pour un serveur
                    speed = parts[2]
                    print(f"Serveur {rank}: Vitesse spécifique définie à {speed}")
            elif parts[0] == "CRASH":  # Commande pour simuler un crash
                if len(parts) == 1:  # Crash global
                    is_crashed = True
                    print(f"Serveur {rank}: En état de crash global.")
                elif len(parts) == 2 and int(parts[1]) == rank:  # Crash spécifique
                    is_crashed = True
                    print(f"Serveur {rank}: En état de crash spécifique.")
            last_command = command

        # Si le serveur n'est pas en état de crash et que le calcul a commencé
        if not is_crashed and has_started:
            for client in range(N_CLIENTS):
                received_command = comm.recv(source=client, tag=0)  # Reçoit les commandes des clients
                log.append(received_command)  # Ajoute la commande au journal
                print(f"Serveur {rank} a reçu la commande: {received_command}")

        # Arrête la boucle si toutes les commandes ont été reçues
        if has_started and len(log) >= N_CLIENTS:
            break

    # Écrit le journal dans un fichier texte
    write_log_to_file(rank, log)
