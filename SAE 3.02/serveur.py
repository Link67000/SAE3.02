import customtkinter
import threading
import subprocess
import socket
import os
import time

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class ServeurMaster(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Initialisation des variables
        self.server_socket = None
        self.server_thread = None
        self.en_fonctionnement = False
        self.clients = []
        self.max_clients = 5

        # Configuration de la fenêtre
        self.title('SAE Serveur Maître')
        self.geometry('400x500')
        self.resizable(False, False)

        # Récupère l'adresse IP de la VM
        self.local_ip = self.get_local_ip()

        # Champs de saisie et labels
        self.addr_txt = customtkinter.CTkLabel(self, text="Adresse :")
        self.addr_txt.place(x=10, y=10)
        self.addr = customtkinter.CTkEntry(self, width=150, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, self.local_ip)  # Définit l'adresse IP locale par défaut

        self.port_txt = customtkinter.CTkLabel(self, text="Port :")
        self.port_txt.place(x=10, y=50)
        self.port = customtkinter.CTkEntry(self, width=150, justify="center")
        self.port.place(x=120, y=50)
        self.port.insert(0, "1111")

        self.start_stop_button = customtkinter.CTkButton(self, text="Allumer", width=380, height=30, command=self.toggle_server)
        self.start_stop_button.place(x=10, y=130)

        self.etat_txt = customtkinter.CTkLabel(self, text="État serveur et suivi connexion :")
        self.etat_txt.place(x=10, y=170)
        self.suivi_txt = customtkinter.CTkTextbox(self, width=380, height=250)
        self.suivi_txt.place(x=10, y=200)

        self.protocol("WM_DELETE_WINDOW", self.fermer_proprement)

    def get_local_ip(self):
        """Récupère l'adresse IP locale de la machine."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # Essaie de se connecter à un hôte extérieur pour obtenir l'adresse IP
            s.connect(('10.254.254.254', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'  # Si cela échoue, on retourne l'IP localhost
        finally:
            s.close()
        return local_ip

    def log(self, message):
        """Ajoute un message dans la zone de suivi."""
        self.suivi_txt.insert("1.0", message + "\n")
        print(message)

    def toggle_server(self):
        """Démarre ou arrête le serveur."""
        if not self.en_fonctionnement:
            self.start_server()
            self.start_stop_button.configure(text="Éteindre")
        else:
            self.stop_server()
            self.start_stop_button.configure(text="Allumer")

    def start_server(self):
        """Démarre le serveur."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
            # Ajout de l'option SO_REUSEADDR
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            host = self.addr.get()
            port = int(self.port.get())
            self.server_socket.bind((host, port))
            self.server_socket.listen(self.max_clients)

            self.log(f"[*] Serveur lancé sur {host}:{port}")
            self.en_fonctionnement = True

            self.server_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.server_thread.start()
        except Exception as e:
            self.log(f"[!] Erreur : {e}")


    def stop_server(self):
        """Arrête le serveur."""
        if self.server_socket:
            for client in self.clients:
                client.close()
            self.server_socket.close()
        self.en_fonctionnement = False
        self.log("[*] Serveur arrêté proprement.")

    def handle_client(self, client_socket):
        try:
            while self.en_fonctionnement:
            # Réception des données
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break  # Le client a fermé la connexion

                # Affiche les données reçues
                self.log(f"[*] Programme reçu :\n{data}")

            # Exemple de traitement des données
                with open("programme_recu.txt", "w", encoding="utf-8") as file:
                    file.write(data)
                self.log("[*] Le programme a été enregistré avec succès.")
        except Exception as e:
            self.log(f"[*] Erreur lors du traitement des données : {e}")
        finally:
            client_socket.close()

    def accept_clients(self):
        """Accepte les connexions entrantes."""
        while self.en_fonctionnement:
            try:
                client_socket, addr = self.server_socket.accept()
                self.log(f"[*] Connexion acceptée depuis {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                self.log(f"[*] Erreur lors de l'acceptation d'un client : {e}")


    def fermer_proprement(self):
        """Ferme proprement la fenêtre et arrête le serveur."""
        self.stop_server()
        self.destroy()


if __name__ == "__main__":
    app = ServeurMaster()
    app.mainloop()
