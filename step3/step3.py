from mpi4py import MPI
from datetime import datetime
import time
import os


def read_client_commands(client_id):
    filename = f"step3/clients/client_{client_id}.txt"
    commands = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            commands = [line.strip() for line in f.readlines()]
    else:
        print(f"Client {client_id} : Fichier {filename} non trouvé.")
    return commands


def write_log_to_file(rk, lg):
    log_directory = "step3/logs"
    os.makedirs(log_directory, exist_ok=True)
    filename = f"{log_directory}/log_server_{rk}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(lg))
    print(f"Serveur {rk}: historique enregistré dans {filename}")


def read_last_command():
    filename = "step3/repl_history.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            commands = f.readlines()
            return commands[-1].strip() if commands else None
    return None


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N_CLIENTS = 2
N_SERVERS = size - N_CLIENTS

speed = "low"
is_crashed = False
has_started = False
last_command = None
client_commands = read_client_commands(rank) if rank < N_CLIENTS else None

# Client
if rank < N_CLIENTS:
    command_index = 0
    print(f"Client {rank} : Chargement des commandes depuis le fichier.")
    print(f"Client {rank} : Commandes lues : {client_commands}")

    while True:
        repl_command = read_last_command()
        if repl_command == "START" and not has_started:
            has_started = True
            print(f"Client {rank} : Démarrage autorisé.")

        if has_started and repl_command != last_command:
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
                    is_crashed = True
                    print(f"Client {rank}: En état de crash.")
            last_command = repl_command

        if has_started and not is_crashed and command_index < len(client_commands):
            current_command = client_commands[command_index]
            command_index += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_command = f"{current_command} de client {rank} à {timestamp}"

            for server in range(N_CLIENTS, N_CLIENTS + N_SERVERS):
                comm.send(full_command, dest=server, tag=rank)
            print(f"Client {rank} : Commande envoyée '{full_command}'")

            if speed == "low":
                time.sleep(10)
            elif speed == "medium":
                time.sleep(5)
            elif speed == "high":
                time.sleep(1)

        elif command_index >= len(client_commands):
            for server in range(N_CLIENTS, N_CLIENTS + N_SERVERS):
                comm.send("FINISHED", dest=server, tag=rank)
            print(f"Client {rank} : Toutes les commandes ont été envoyées.")
            break

# Serveur
elif rank >= N_CLIENTS:
    log = []
    finished_clients = 0

    while finished_clients < N_CLIENTS:
        repl_command = read_last_command()
        if repl_command and repl_command != last_command:
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
                    is_crashed = True
                    print(f"Serveur {rank}: En état de crash.")
            last_command = repl_command

        if not is_crashed:
            for client in range(N_CLIENTS):
                received_command = comm.recv(source=client, tag=client)
                if received_command == "FINISHED":
                    finished_clients += 1
                else:
                    log.append(received_command)

            if speed == "low":
                time.sleep(10)
            elif speed == "medium":
                time.sleep(5)
            elif speed == "high":
                time.sleep(1)

    write_log_to_file(rank, log)
