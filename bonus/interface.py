import tkinter as tk
from tkinter import messagebox


def envoyer_commande():
    commande = champ_commande.get().strip()
    if est_commande_edition_valide(commande):
        with open("log_commands.txt", "a") as history:
            history.write(commande + "\n")
        messagebox.showinfo("Succès", "Commande envoyée : " + commande)
        champ_commande.delete(0, tk.END)
    else:
        messagebox.showerror("Erreur", "Commande invalide.")


def est_commande_edition_valide(commande):
    parties = commande.split()
    if len(parties) == 0:
        return False
    if parties[0] in {"COLOR", "THICKNESS", "DRAW", "CLEAR"}:
        return True
    return False


def focus_in(event):
    if champ_commande.get() == "Entrez votre commande ici...":
        champ_commande.delete(0, tk.END)
        champ_commande.config(fg="white")


def focus_out(event):
    if champ_commande.get() == "":
        champ_commande.config(fg="grey")
        champ_commande.insert(0, "Entrez votre commande ici...")


fenetre = tk.Tk()
fenetre.title("Interface d'Édition MPI")

label_instruction = tk.Label(fenetre)
label_instruction.pack(pady=2)

champ_commande = tk.Entry(fenetre, width=50, fg="grey")
champ_commande.insert(0, "Entrez votre commande ici...")
champ_commande.bind("<FocusIn>", focus_in)
champ_commande.bind("<FocusOut>", focus_out)
champ_commande.pack(pady=1, ipady=5)

bouton_envoyer = tk.Button(fenetre, text="Envoyer Commande", command=envoyer_commande)
bouton_envoyer.pack(pady=10)

fenetre.mainloop()
