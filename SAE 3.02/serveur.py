import socket
import threading
import json
import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class MasterApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.server_socket = None
        self.client_threads = []
        self.clients = {}
        self.slaves = {
            "C/C++": [],
            "JAVA/Python": []
        }
        self.load_balance_counter = 0

        self.title("Master")
        self.geometry("500x600")

        # Interface utilisateur
        self.addr_txt = customtkinter.CTkLabel(self, text="Adresse :")
        self.addr_txt.place(x=10, y=10)
        self.addr = customtkinter.CTkEntry(self, width=150, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, "192.168.1.80")
        
        self.loadB = customtkinter.CTkLabel(self, text="loadB :")
        self.loadB.place(x=10, y=90)
        self.nb_max = customtkinter.CTkEntry(self, width=150, justify="center")
        self.nb_max.place(x=120, y=90)
        self.nb_max.insert(0, "5")

        self.port_txt = customtkinter.CTkLabel(self, text="Port :")
        self.port_txt.place(x=10, y=50)
        self.port = customtkinter.CTkEntry(self, width=150, justify="center")
        self.port.place(x=120, y=50)
        self.port.insert(0, "1111")

        self.start_stop_button = customtkinter.CTkButton(self, text="Démarrer", width=380, height=30, command=self.toggle_server)
        self.start_stop_button.place(x=10, y=140)

        self.etat_txt = customtkinter.CTkLabel(self, text="État :")
        self.etat_txt.place(x=10, y=150)
        self.suivi_txt = customtkinter.CTkTextbox(self, width=480, height=300)
        self.suivi_txt.place(x=10, y=180)

        self.protocol("WM_DELETE_WINDOW", self.fermer_proprement)

    def log(self, message):
        self.suivi_txt.insert("1.0", message + "\n")
        print(message)

    def toggle_server(self):
        if self.server_socket is None:
            self.start_server()
            self.start_stop_button.configure(text="Arrêter")
        else:
            self.stop_server()
            self.start_stop_button.configure(text="Démarrer")

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.addr.get(), int(self.port.get())))
            self.server_socket.listen(7)

            self.log("[*] Serveur Master démarré.")
            threading.Thread(target=self.accept_clients, daemon=True).start()
        except Exception as e:
            self.log(f"[!] Erreur : {e}")

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        self.log("[*] Serveur arrêté proprement.")

    def accept_clients(self):
        while self.server_socket:
            try:
                client_socket, addr = self.server_socket.accept()
                self.log(f"[*] Connexion depuis {addr}")

                thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
                self.client_threads.append(thread)
                thread.start()
            except Exception as e:
                self.log(f"[!] Erreur : {e}")

    def handle_client(self, client_socket):
        try:
            # Réception initiale du rôle du client
            role = client_socket.recv(4096).decode("utf-8").strip()
            self.log(f"Rôle reçu : {role}")

            # Si le rôle est "client", on l'ajoute dans le dictionnaire des clients
            if role == "client":
                self.log("[*] Le client a été connecté.")
                if role not in self.clients:
                    self.clients[role] = client_socket  # Ajouter le client
                # Attendre un programme d'un client et envoyer à un slave si besoin
                self.wait_for_program_from_client(client_socket)
                return

            # Si le rôle est "slave", on l'ajoute dans le dictionnaire des slaves
            if role not in self.slaves:
                self.slaves[role] = []

            self.slaves[role].append(client_socket)
            self.log(f"[*] Le slave {role} a été ajouté aux slaves.")

            # Attente de la réception d'un programme d'un client et gestion de l'envoi au slave approprié
            self.wait_for_program_from_client(client_socket)

        except Exception as e:
            self.log(f"[!] Erreur lors du traitement du client : {e}")
            client_socket.sendall(f"Erreur lors du traitement : {e}".encode('utf-8'))


    def wait_for_program_from_client(self, client_socket):
        """Attends un programme d'un client et l'envoie au slave correspondant."""
        while True:
            # Réception du programme envoyé par le client (format JSON attendu)
            message = client_socket.recv(4096).decode("utf-8")

            if message:
                try:
                    # Supposons que le message est un JSON avec un champ 'type' pour identifier le programme
                    program_data = json.loads(message)
                    program_type = program_data.get("type_de_fichier", "")

                    # Vérifie si un slave correspondant au type du programme est connecté
                    if program_type in ["C", "C++"]:
                        # Recherche d'un slave pour "C/C++"
                        if self.slaves.get("C/C++"):
                            self.log(f"[*] Envoi du programme {program_type} au slave C/C++.")
                            slave_socket = self.slaves["C/C++"][0]  # Utilisation du premier slave disponible
                            self.send_program_to_slave(client_socket, slave_socket, program_data)
                        else:
                            self.log(f"[!] Aucun slave C/C++ disponible.")
                            client_socket.sendall("Erreur : Aucun slave C/C++ disponible.".encode("utf-8"))
                    elif program_type in ["JAVA", "Python"]:
                        # Recherche d'un slave pour "JAVA/Python"
                        if self.slaves.get("JAVA/Python"):
                            self.log(f"[*] Envoi du programme {program_type} au slave JAVA/Python.")
                            slave_socket = self.slaves["JAVA/Python"][0]  # Utilisation du premier slave disponible
                            self.send_program_to_slave(client_socket, slave_socket, program_data)
                        else:
                            self.log(f"[!] Aucun slave JAVA/Python disponible.")
                            client_socket.sendall("Erreur : Aucun slave JAVA/Python disponible.".encode("utf-8"))
                    else:
                        self.log(f"[!] Type de programme non supporté : {program_type}.")
                        client_socket.sendall(f"Erreur : Type de programme non supporté.".encode("utf-8"))

                except json.JSONDecodeError:
                    self.log("[!] Erreur de décodage JSON.")
                    client_socket.sendall("Erreur : Programme mal formé.".encode("utf-8"))
                except Exception as e:
                    self.log(f"[!] Erreur lors du traitement du programme : {e}")
                    client_socket.sendall(f"Erreur lors du traitement du programme : {e}".encode("utf-8"))


    def send_program_to_slave(self, client_socket, slave_socket, program_data):
        """Envoie le programme du client au slave approprié."""
        try:
            # Envoie du programme au slave
            slave_socket.sendall(json.dumps(program_data).encode("utf-8"))
            self.log(f"[>] Programme envoyé au slave.")

            # Attendre la réponse du slave et l'envoyer au client
            response = slave_socket.recv(4096).decode("utf-8")
            client_socket.sendall(response.encode("utf-8"))
            self.log(f"[<] Réponse envoyée au client.")
        except Exception as e:
            self.log(f"[!] Erreur lors de l'envoi au slave ou au client : {e}")


    def fermer_proprement(self):
        """Ferme proprement le serveur."""
        self.stop_server()
        self.destroy()


def main():
    app = MasterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
