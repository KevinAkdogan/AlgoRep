.PHONY: step1 step2 step3 step4 clean

# Variables
PYTHON=python3
MPIEXEC=mpirun
NPROCS=4 # Adjust this as needed

# Rules

step1:
	@echo "Running Step 1..."
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step1/step1.py

step2:
	@echo "Running Step 2..."
	@echo "You need to run this command on another terminal to send REPL commands : python3 step2/repl.py"
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step2/step2.py

step3:
	@echo "Running Step 3..."
	@echo "You need to run this command on another terminal to send REPL commands : python3 step3/repl.py"
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step3/step3.py

step4:
	@echo "Running Step 4..."
	@echo "You need to run this command on another terminal to send REPL commands : python3 step4/repl.py"
	$(MPIEXEC) -np $(NPROCS) $(PYTHON) step4/step4.py

clean:
	@echo "Cleaning up logs..."
	rm -f step1/log_server_*.txt step2/repl_history.txt step3/repl_history.txt step4/repl_history.txt
