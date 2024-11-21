.PHONY: step1 step2 step3 step4 clean

# Variables
PYTHON=python3
MPIEXEC=mpirun
NPROCS=4 # Possibilité d'ajustement si besoin

# Règles

step1:
	@echo "Step 1 en cours d'éxécution..."
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step1/step1.py

step2:
	@echo "Step 2 en cours d'éxécution..."
	@echo "Exécuter cette commande dans un autre terminal pour envoyer des commandes REPL : python3 step2/repl.py"
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step2/step2.py

step3:
	@echo "Step 3 en cours d'éxécution..."
	@echo "Exécuter cette commande dans un autre terminal pour envoyer des commandes REPL : python3 step3/repl.py"
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step3/step3.py

step4:
	@echo "Step 4 en cours d'éxécution..."
	@echo "Exécuter cette commande dans un autre terminal pour envoyer des commandes REPL : python3 step4/repl.py"
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step4/step4.py

interface:
	@echo "Interface en cours d'éxécution..."
	$(PYTHON) bonus/interface.py

clean:
	@echo "Effacement des logs"
	rm -f step1/log_server_*.txt step2/repl_history.txt step3/repl_history.txt step4/repl_history.txt step3/logs/log_server_2.txt step3/logs/log_server_3.txt step4/logs/log_server_2.txt step4/logs/log_server_3.txt bonus/log_commands.txt
