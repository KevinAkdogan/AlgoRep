from mpi4py import MPI
from datetime import datetime
import time
import os


# Fonction pour lire les commandes des clients à partir de fichiers
def read_client_commands(client_id):
    filename = f"step3/clients/client_{client_id}.txt"  # Nom du fichier spécifique au client
    commands = []
    if os.path.exists(filename):  # Vérifie si le fichier existe
        with open(filename, "r") as f:
            commands = [line.strip() for line in f.readlines()]  # Lit toutes les commandes
    else:
        print(f"Client {client_id} : Fichier {filename} non trouvé.")
    return commands


# Fonction pour écrire les logs des serveurs dans des fichiers
def write_log_to_file(rk, lg):
    log_directory = "step3/logs"  # Répertoire pour les logs
    os.makedirs(log_directory, exist_ok=True)  # Crée le répertoire s'il n'existe pas
    filename = f"{log_directory}/log_server_{rk}.txt"  # Nom du fichier log
    with open(filename, "w") as f:
        f.write("\n".join(lg))  # Écrit chaque ligne de log
    print(f"Serveur {rk}: historique enregistré dans {filename}")


# Fonction pour lire la dernière commande dans l'historique REPL
def read_last_command():
    filename = "step3/repl_history.txt"  # Fichier d'historique de la REPL
    if os.path.exists(filename):  # Vérifie si le fichier existe
        with open(filename, "r") as f:
            commands = f.readlines()
            return commands[-1].strip() if commands else None  # Retourne la dernière commande
    return None  # Aucune commande si le fichier n'existe pas


# Initialisation de MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Identifiant du processus
size = comm.Get_size()  # Nombre total de processus

# Définition des rôles
N_CLIENTS = 2  # Nombre de processus clients
N_SERVERS = size - N_CLIENTS  # Nombre de processus serveurs

# Variables globales
speed = "low"  # Vitesse par défaut
is_crashed = False  # Indicateur de crash
has_started = False  # Indicateur de démarrage
last_command = None  # Dernière commande traitée
client_commands = read_client_commands(rank) if rank < N_CLIENTS else None  # Commandes pour chaque client

# Client
if rank < N_CLIENTS:
    command_index = 0  # Index pour suivre les commandes
    print(f"Client {rank} : Chargement des commandes depuis le fichier.")
    print(f"Client {rank} : Commandes lues : {client_commands}")

    while True:
        # Lecture des commandes REPL
        repl_command = read_last_command()
        if repl_command == "START" and not has_started:
            has_started = True  # Active le démarrage des clients
            print(f"Client {rank} : Démarrage autorisé.")

        if has_started and repl_command != last_command:
            # Analyse de la commande REPL
            parts = repl_command.split()
            if parts[0] == "SPEED":
                if len(parts) == 2:
                    speed = parts[1]
                    print(f"Client {rank}: Vitesse mise à jour à {speed}")
                elif len(parts) == 3 and int(parts[1]) == rank:
                    speed = parts[2]
                    print(f"Client {rank}: Vitesse spécifique mise à jour à {speed}")
            elif parts[0] == "CRASH":
                if len(parts) == 1 or (len(parts) == 2 and int(parts[1]) == rank):
                    is_crashed = True  # Active l'état de crash
                    print(f"Client {rank}: En état de crash.")
            last_command = repl_command

        # Envoi des commandes si démarré et non en état de crash
        if has_started and not is_crashed and command_index < len(client_commands):
            current_command = client_commands[command_index]
            command_index += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_command = f"{current_command} de client {rank} à {timestamp}"

            # Envoi de la commande à tous les serveurs
            for server in range(N_CLIENTS, N_CLIENTS + N_SERVERS):
                comm.send(full_command, dest=server, tag=rank)
            print(f"Client {rank} : Commande envoyée '{full_command}'")

            # Pause selon la vitesse
            if speed == "low":
                time.sleep(10)
            elif speed == "medium":
                time.sleep(5)
            elif speed == "high":
                time.sleep(1)

        elif command_index >= len(client_commands):
            # Notifie les serveurs que toutes les commandes ont été envoyées
            for server in range(N_CLIENTS, N_CLIENTS + N_SERVERS):
                comm.send("FINISHED", dest=server, tag=rank)
            print(f"Client {rank} : Toutes les commandes ont été envoyées.")
            break

# Serveur
elif rank >= N_CLIENTS:
    log = []  # Liste pour stocker les commandes reçues
    finished_clients = 0  # Nombre de clients ayant terminé

    while finished_clients < N_CLIENTS:
        # Lecture des commandes REPL
        repl_command = read_last_command()
        if repl_command and repl_command != last_command:
            # Analyse de la commande REPL
            parts = repl_command.split()
            if parts[0] == "SPEED":
                if len(parts) == 2:
                    speed = parts[1]
                    print(f"Serveur {rank}: Vitesse définie à {speed}")
                elif len(parts) == 3 and int(parts[1]) == rank:
                    speed = parts[2]
                    print(f"Serveur {rank}: Vitesse spécifique définie à {speed}")
            elif parts[0] == "CRASH":
                if len(parts) == 1 or (len(parts) == 2 and int(parts[1]) == rank):
                    is_crashed = True  # Active l'état de crash
                    print(f"Serveur {rank}: En état de crash.")
            last_command = repl_command

        # Réception des commandes des clients
        if not is_crashed:
            for client in range(N_CLIENTS):
                received_command = comm.recv(source=client, tag=client)
                if received_command == "FINISHED":
                    finished_clients += 1  # Compte les clients terminés
                else:
                    log.append(received_command)

            # Pause selon la vitesse
            if speed == "low":
                time.sleep(10)
            elif speed == "medium":
                time.sleep(5)
            elif speed == "high":
                time.sleep(1)

    # Écrit le log final dans un fichier
    write_log_to_file(rank, log)
