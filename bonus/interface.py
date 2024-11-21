import tkinter as tk
from tkinter import messagebox

# Fonction appelée lorsqu'on clique sur "Envoyer Commande"
def envoyer_commande():
    commande = champ_commande.get().strip()  # Récupère et nettoie la commande saisie
    if est_commande_edition_valide(commande):  # Vérifie si la commande est valide
        # Enregistre la commande dans un fichier historique
        with open("bonus/log_commands.txt", "a") as history:
            history.write(commande + "\n")
        # Affiche une boîte de dialogue pour confirmer l'envoi
        messagebox.showinfo("Succès", "Commande envoyée : " + commande)
        champ_commande.delete(0, tk.END)  # Efface le champ de saisie
    else:
        # Affiche une boîte de dialogue d'erreur si la commande est invalide
        messagebox.showerror("Erreur", "Commande invalide.")

# Fonction pour valider si la commande saisie correspond aux commandes attendues
def est_commande_edition_valide(commande):
    parties = commande.split()  # Découpe la commande en parties
    if len(parties) == 0:  # Vérifie que la commande n'est pas vide
        return False
    if parties[0] in {"COLOR", "THICKNESS", "DRAW", "CLEAR"}:  # Vérifie les mots-clés valides
        return True
    return False

# Fonction déclenchée lorsque le champ de saisie obtient le focus
def focus_in(event):
    if champ_commande.get() == "Entrez votre commande ici...":  # Placeholder par défaut
        champ_commande.delete(0, tk.END)  # Efface le texte par défaut
        champ_commande.config(fg="white")  # Change la couleur du texte pour l'utilisateur

# Fonction déclenchée lorsque le champ de saisie perd le focus
def focus_out(event):
    if champ_commande.get() == "":  # Si aucun texte n'est saisi
        champ_commande.config(fg="grey")  # Change la couleur du texte pour indiquer le placeholder
        champ_commande.insert(0, "Entrez votre commande ici...")  # Remet le placeholder

# Création de la fenêtre principale de l'interface
fenetre = tk.Tk()
fenetre.title("Interface d'Édition MPI")  # Titre de la fenêtre

# Champ pour afficher une étiquette d'instruction (optionnel ici)
label_instruction = tk.Label(fenetre)
label_instruction.pack(pady=2)  # Ajoute un espacement vertical autour du widget

# Champ de saisie pour les commandes
champ_commande = tk.Entry(fenetre, width=50, fg="grey")  # Largeur et couleur initiale du texte
champ_commande.insert(0, "Entrez votre commande ici...")  # Placeholder initial
champ_commande.bind("<FocusIn>", focus_in)  # Associe l'événement focus_in
champ_commande.bind("<FocusOut>", focus_out)  # Associe l'événement focus_out
champ_commande.pack(pady=1, ipady=5)  # Espacement vertical et padding interne pour augmenter la hauteur

# Bouton pour envoyer la commande
bouton_envoyer = tk.Button(fenetre, text="Envoyer Commande", command=envoyer_commande)
bouton_envoyer.pack(pady=10)  # Espacement vertical pour séparer le bouton du champ de saisie

# Boucle principale de l'interface graphique
fenetre.mainloop()
