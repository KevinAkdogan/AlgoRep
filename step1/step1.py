from mpi4py import MPI
from datetime import datetime
import random
import time


def generate_command(rk):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Commande de client {rk} à {timestamp}"


def write_log_to_file(rk, lg):
    filename = f"log_server_{rk}.txt"
    with open("step1/" + filename, "w") as f:
        f.write("\n".join(lg))
    print(f"Serveur {rk}: historique enregistré dans {filename}")


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N_CLIENTS = 4
N_SERVERS = size - N_CLIENTS
LEADER = N_CLIENTS

log = [] if rank >= N_CLIENTS else None

# Client
if rank < N_CLIENTS:
    time.sleep(random.uniform(0, 0.5))
    command = generate_command(rank)
    for server in range(N_CLIENTS, size):
        comm.send(command, dest=server, tag=0)

# Serveur
elif rank >= N_CLIENTS:
    for client in range(N_CLIENTS):
        command = comm.recv(source=client, tag=0)
        log.append(command)
        print(f"Serveur {rank} a ajouté la commande: {command}")

    if rank == LEADER:
        for other_server in range(N_CLIENTS, size):
            if other_server != LEADER:
                comm.send(log, dest=other_server, tag=1)
    else:
        leader_log = comm.recv(source=LEADER, tag=1)
        if leader_log == log:
            print(f"Serveur {rank}: Log cohérent avec le leader.")
        else:
            print(f"Serveur {rank}: Incohérence détectée avec le leader.")
        log = leader_log

    write_log_to_file(rank, log)
