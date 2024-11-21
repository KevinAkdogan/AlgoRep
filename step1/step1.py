import os

from mpi4py import MPI
from datetime import datetime
import random
import time


# Génère une commande unique pour un client contenant son rang et un horodatage
def generate_command(rk):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Commande de client {rk} à {timestamp}"


# Écrit le journal (log) du serveur dans un fichier texte spécifique
def write_log_to_file(rk, lg):
    filename = f"log_server_{rk}.txt"
    # Enregistre le fichier dans le répertoire "step1/"
    with open("step1/" + filename, "w") as f:
        f.write("\n".join(lg))  # Écrit chaque entrée du journal sur une nouvelle ligne
    print(f"Serveur {rk}: historique enregistré dans {filename}")


# Lit la dernière commande stockée dans le fichier repl_history.txt
def read_last_command():
    filename = "repl_history.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            commands = f.readlines()
            return commands[-1].strip() if commands else None  # Retourne la dernière commande
    return None


# Initialisation de MPI
comm = MPI.COMM_WORLD  # Objet de communication pour interagir avec les processus
rank = comm.Get_rank()  # Identifiant unique du processus courant
size = comm.Get_size()  # Nombre total de processus dans la communication

# Définition des rôles
N_CLIENTS = 2  # Nombre de clients dans le système
N_SERVERS = size - N_CLIENTS  # Nombre de serveurs (le reste des processus)
LEADER = N_CLIENTS  # Définit le premier serveur comme leader

# Initialisation du journal pour les serveurs
log = [] if rank >= N_CLIENTS else None

# ------------------------------- Client -------------------------------
if rank < N_CLIENTS:
    # Attente d'un délai aléatoire pour simuler l'asynchronisme
    time.sleep(random.uniform(0, 0.5))

    # Génère une commande pour le client courant
    command = generate_command(rank)

    # Envoie la commande à tous les serveurs
    for server in range(N_CLIENTS, size):
        comm.send(command, dest=server, tag=0)  # Envoi avec une étiquette "0"

# ------------------------------- Serveur -------------------------------
elif rank >= N_CLIENTS:
    # Réception des commandes des clients
    for client in range(N_CLIENTS):
        command = comm.recv(source=client, tag=0)  # Réception avec une étiquette "0"
        log.append(command)  # Ajout de la commande reçue au journal
        print(f"Serveur {rank} a ajouté la commande: {command}")

    # Synchronisation du journal avec le leader
    if rank == LEADER:
        # Le leader envoie son journal à tous les autres serveurs
        for other_server in range(N_CLIENTS, size):
            if other_server != LEADER:  # Le leader ne s'envoie pas à lui-même
                comm.send(log, dest=other_server, tag=1)  # Envoi avec une étiquette "1"
    else:
        # Les autres serveurs reçoivent le journal du leader
        leader_log = comm.recv(source=LEADER, tag=1)
        # Vérification de la cohérence avec le journal local
        if leader_log == log:
            print(f"Serveur {rank}: Log cohérent avec le leader.")
        else:
            print(f"Serveur {rank}: Incohérence détectée avec le leader.")
        # Mise à jour du journal local avec celui du leader
        log = leader_log

    # Écriture du journal dans un fichier
    write_log_to_file(rank, log)
