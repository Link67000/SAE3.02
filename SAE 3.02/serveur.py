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
                # Appeler la fonction qui écoute les messages du client
                self.listen_to_client_messages(client_socket)
                return

            # Si le rôle est "slave", on l'ajoute dans le dictionnaire des slaves
            if role not in self.slaves:
                self.slaves[role] = []

            self.slaves[role].append(client_socket)
            self.log(f"[*] Le slave {role} a été ajouté aux slaves.")

        except Exception as e:
            self.log(f"[!] Erreur lors du traitement du client : {e}")
            client_socket.sendall(f"Erreur lors du traitement : {e}".encode('utf-8'))

    def listen_to_client_messages(self, client_socket):
        """Fonction dédiée pour écouter et traiter les messages envoyés par le client."""
        try:
            while True:
                message = client_socket.recv(4096).decode("utf-8")
                if not message:
                    self.log("[!] Le client a fermé la connexion.")
                    break

                self.log(f"[+] Message reçu : {message}")

                try:
                    # Décodage du message en JSON
                    data = json.loads(message)
                    file_type = data.get("type_de_fichier", "Unknown")
                    code = data.get("code", "")
                    programme = data.get("programme", "")

                    # Affichage des informations reçues pour vérification
                    self.log(f"Type de fichier : {file_type}")
                    self.log(f"Code reçu : {code}")
                    self.log(f"Programme reçu : {programme}")

                    # Décider du Slave en fonction du type de fichier
                    target_slave = self.get_target_slave(file_type)
                    if target_slave:
                        self.forward_to_slave(target_slave, file_type, code, programme, client_socket)
                    else:
                        self.log(f"[!] Aucun Slave disponible pour le type : {file_type}")
                        client_socket.sendall("Erreur: Aucun Slave disponible.".encode('utf-8'))

                except json.JSONDecodeError:
                    self.log("[!] Erreur : données non valides reçues.")
                    client_socket.sendall("Erreur: Données invalides.".encode('utf-8'))

        except Exception as e:
            self.log(f"[!] Erreur lors de l'écoute des messages du client : {e}")
            client_socket.sendall(f"Erreur lors de l'écoute des messages : {e}".encode('utf-8'))

    def get_target_slave(self, file_type):
        """Retourne un socket de Slave correspondant au rôle."""
        if file_type in self.slaves and self.slaves[file_type]:
            # Load balancing simple : prendre le premier Slave disponible
            return self.slaves[file_type][0]
        return None

    def forward_to_slave(self, slave_socket, file_type, code, programme, client_socket):
        """Envoie le fichier au Slave sélectionné et attend la réponse à renvoyer au client."""
        try:
            # Ajouter le programme dans le message envoyé au slave
            message = json.dumps({"type_de_fichier": file_type, "code": code, "programme": programme})
            slave_socket.sendall(message.encode("utf-8"))
            self.log(f"[>] Envoyé au Slave : {file_type}, {programme}")

            # Attente de la réponse du slave
            response = slave_socket.recv(4096).decode("utf-8")
            self.log(f"[<] Réponse du Slave : {response}")

            # Renvoyer la réponse au client
            client_socket.sendall(response.encode("utf-8"))
            self.log(f"[<] Réponse envoyée au client.")
        except Exception as e:
            self.log(f"[!] Erreur d'envoi au Slave ou au client : {e}")

    def fermer_proprement(self):
        """Ferme proprement le serveur."""
        self.stop_server()
        self.destroy()

def main():
    app = MasterApp()
    app.mainloop()

if __name__ == "__main__":
    main()
