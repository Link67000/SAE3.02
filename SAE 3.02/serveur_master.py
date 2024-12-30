import socket
import threading
import json
import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class ApplicationMaitre(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.socket_serveur = None
        self.threads_clients = []
        self.clients_connectes = {}
        self.esclaves = {
            "C/C++": [],
            "JAVA/Python": []
        }
        self.taches_par_esclave = {
            "C/C++": [],
            "JAVA/Python": []
        }
        self.taches_max = 0

        self.title("Maître")
        self.geometry("500x520")
        self.resizable(False, False)

        self.label_addr = customtkinter.CTkLabel(self, text="Adresse :")
        self.label_addr.place(x=10, y=10)
        self.champ_adresse = customtkinter.CTkEntry(self, width=150, justify="center")
        self.champ_adresse.place(x=175, y=10)
        self.champ_adresse.insert(0, "192.168.x.y")

        self.label_charge = customtkinter.CTkLabel(self, text="Charge Max :")
        self.label_charge.place(x=10, y=90)
        self.champ_taches_max = customtkinter.CTkEntry(self, width=150, justify="center")
        self.champ_taches_max.place(x=175, y=90)
        self.champ_taches_max.insert(0, "5")

        self.label_port = customtkinter.CTkLabel(self, text="Port :")
        self.label_port.place(x=10, y=50)
        self.champ_port = customtkinter.CTkEntry(self, width=150, justify="center")
        self.champ_port.place(x=175, y=50)
        self.champ_port.insert(0, "1111")

        self.bouton_lancer_serveur = customtkinter.CTkButton(self, text="Démarrer", width=480, height=30, command=self.on_off)
        self.bouton_lancer_serveur.place(x=10, y=130)

        self.etiquette_etat = customtkinter.CTkLabel(self, text="Suivi les échanges (log) : ")
        self.etiquette_etat.place(x=10, y=170)
        self.zone_suivi = customtkinter.CTkTextbox(self, width=480, height=300)
        self.zone_suivi.place(x=10, y=210)

        self.protocol("WM_DELETE_WINDOW", self.fermer_proprement)

    def log(self, message):
        self.zone_suivi.insert("1.0", message + "\n\n")

    def on_off(self):
        if self.socket_serveur is None:
            self.demarrer_serveur()
            self.bouton_lancer_serveur.configure(text="Arrêter")
        else:
            self.arreter_serveur()
            self.bouton_lancer_serveur.configure(text="Démarrer")

    def demarrer_serveur(self):
        try:
            self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_serveur.bind((self.champ_adresse.get(), int(self.champ_port.get())))
            self.socket_serveur.listen(7)

            self.taches_max = int(self.champ_taches_max.get())
            self.log("[*] Serveur Maître démarré.")
            threading.Thread(target=self.accepter_clients, daemon=True).start()
        except Exception as e:
            self.log(f"[!] Erreur : {e}")

    def arreter_serveur(self):
        if self.socket_serveur:
            self.socket_serveur.close()
            self.socket_serveur = None
        self.log("[*] Serveur arrêté proprement.")

    def accepter_clients(self):
        while self.socket_serveur:
            try:
                socket_client, adresse = self.socket_serveur.accept()
                self.log(f"[*] Connexion depuis {adresse}")

                thread = threading.Thread(target=self.gerer_client, args=(socket_client,), daemon=True)
                self.threads_clients.append(thread)
                thread.start()
            except Exception as e:
                self.log(f"[!] Erreur : {e}")

    def gerer_client(self, socket_client):
        try:
            role = socket_client.recv(4096).decode("utf-8").strip()
            self.log(f"Rôle reçu : {role}")

            if role == "client":
                self.log("[*] Client connecté.")
                self.attendre_programme_client(socket_client)
            elif role in self.esclaves:
                self.esclaves[role].append(socket_client)
                self.taches_par_esclave[role].append(0)
                self.log(f"[*] Esclave {role} ajouté.")
        except Exception as e:
            self.log(f"[!] Erreur lors du traitement du client : {e}")

    def attendre_programme_client(self, socket_client):
        while True:
            try:
                message = socket_client.recv(4096).decode("utf-8")
                if message:
                    try:
                        programme = json.loads(message)
                    except json.JSONDecodeError:
                        self.log("[!] Erreur : Format JSON invalide.")
                        socket_client.sendall("Erreur : Format JSON invalide.".encode("utf-8"))
                        continue

                    type_programme = programme.get("type_de_fichier")
                    code_programme = programme.get("code")

                    if not type_programme or not code_programme:
                        self.log("[!] Erreur : JSON incomplet. Champs 'type_de_fichier' et 'code' nécessaires.")
                        socket_client.sendall("Erreur : Champs 'type_de_fichier' et 'code' nécessaires.".encode("utf-8"))
                        continue

                    if type_programme in ["C", "C++"]:
                        role_esclave = "C/C++"
                    elif type_programme in ["Java", "Python"]:
                        role_esclave = "JAVA/Python"
                    else:
                        self.log(f"[!] Type de programme non supporté : {type_programme}.")
                        socket_client.sendall(f"Erreur : Type de programme non supporté.".encode("utf-8"))
                        continue

                    index_esclave = self.trouver_esclave_disponible(role_esclave)
                    if index_esclave is not None:
                        self.envoyer_programme(socket_client, role_esclave, index_esclave, programme)
                    else:
                        self.log(f"[!] Aucun esclave disponible pour {role_esclave}.")
                        socket_client.sendall("Erreur : Aucun esclave disponible.".encode("utf-8"))
            except Exception as e:
                self.log(f"[!] Erreur lors de la réception du programme : {e}")
                break

    def trouver_esclave_disponible(self, type_programme):
        taches = self.taches_par_esclave[type_programme]
        for i, nombre in enumerate(taches):
            if nombre < self.taches_max:
                return i
        return None

    def envoyer_programme(self, socket_client, type_programme, index_esclave, programme):
        try:
            socket_esclave = self.esclaves[type_programme][index_esclave]
            self.taches_par_esclave[type_programme][index_esclave] += 1

            socket_esclave.sendall(json.dumps(programme).encode("utf-8"))
            self.log(f"[>] Programme envoyé à l'esclave {type_programme} (index {index_esclave}).")

            reponse = socket_esclave.recv(4096).decode("utf-8")
            self.taches_par_esclave[type_programme][index_esclave] -= 1
            socket_client.sendall(reponse.encode("utf-8"))
            self.log(f"[<] Réponse reçue de l'esclave {type_programme} et envoyée au client.")
        except Exception as e:
            self.log(f"[!] Erreur lors de l'envoi à l'esclave ou au client : {e}")

    def fermer_proprement(self):
        self.arreter_serveur()
        self.destroy()


def main():
    app = ApplicationMaitre()
    app.mainloop()


if __name__ == "__main__":
    main()
