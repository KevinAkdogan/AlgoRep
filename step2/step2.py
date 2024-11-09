from mpi4py import MPI
from datetime import datetime
import time
import os


def generate_command(rk):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Commande de client {rk} à {timestamp}"


def write_log_to_file(rk, lg):
    filename = f"log_server_{rk}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(lg))
    print(f"Serveur {rk}: historique enregistré dans {filename}")


def read_last_command():
    filename = "step2/repl_history.txt"
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

# Client
if rank < N_CLIENTS:
    while True:
        command = read_last_command()
        if command == "START" and not has_started:
            has_started = True
            print(f"Client {rank} : Démarrage autorisé.")

        if has_started and command != last_command:
            parts = command.split()
            if parts[0] == "SPEED":
                if len(parts) == 2:
                    speed = parts[1]
                    print(f"Client {rank}: Vitesse mise à jour à {speed}")
                elif len(parts) == 3 and int(parts[1]) == rank:
                    speed = parts[2]
                    print(f"Client {rank}: Vitesse spécifique mise à jour à {speed}")
            elif parts[0] == "CRASH":
                if len(parts) == 1:
                    is_crashed = True
                    print(f"Client {rank}: En état de crash global.")
                elif len(parts) == 2 and int(parts[1]) == rank:
                    is_crashed = True
                    print(f"Client {rank}: En état de crash spécifique.")
            last_command = command

        if has_started and not is_crashed:
            generated_command = generate_command(rank)
            for server in range(N_CLIENTS, N_CLIENTS + N_SERVERS):
                comm.send(generated_command, dest=server, tag=0)
            print(f"Client {rank} : Commande envoyée '{generated_command}'")

            if speed == "low":
                time.sleep(10)
            elif speed == "medium":
                time.sleep(2)
            elif speed == "high":
                time.sleep(0.5)

# Serveur
elif rank >= N_CLIENTS:
    log = []
    while True:
        command = read_last_command()
        if command and command != last_command:
            parts = command.split()
            if parts[0] == "SPEED":
                if len(parts) == 2:
                    speed = parts[1]
                    print(f"Serveur {rank}: Vitesse définie à {speed}")
                elif len(parts) == 3 and int(parts[1]) == rank:
                    speed = parts[2]
                    print(f"Serveur {rank}: Vitesse spécifique définie à {speed}")
            elif parts[0] == "CRASH":
                if len(parts) == 1:
                    is_crashed = True
                    print(f"Serveur {rank}: En état de crash global.")
                elif len(parts) == 2 and int(parts[1]) == rank:
                    is_crashed = True
                    print(f"Serveur {rank}: En état de crash spécifique.")
            last_command = command

        if not is_crashed and has_started:
            for client in range(N_CLIENTS):
                received_command = comm.recv(source=client, tag=0)
                log.append(received_command)
                print(f"Serveur {rank} a reçu la commande: {received_command}")

        if has_started and len(log) >= N_CLIENTS:
            break

    write_log_to_file(rank, log)
