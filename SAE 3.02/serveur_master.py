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
        self.slave_task_count = {
            "C/C++": [],
            "JAVA/Python": []
        }
        self.max_tasks = 0

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

            self.max_tasks = int(self.nb_max.get())
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
            role = client_socket.recv(4096).decode("utf-8").strip()
            self.log(f"Rôle reçu : {role}")

            if role == "client":
                self.log("[*] Client connecté.")
                self.wait_for_program_from_client(client_socket)
            elif role in self.slaves:
                self.slaves[role].append(client_socket)
                self.slave_task_count[role].append(0)
                self.log(f"[*] Slave {role} ajouté.")
        except Exception as e:
            self.log(f"[!] Erreur lors du traitement du client : {e}")

    def wait_for_program_from_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(4096).decode("utf-8")
                if message:
                    try:
                        program_data = json.loads(message)
                    except json.JSONDecodeError:
                        self.log("[!] Erreur : Format JSON invalide.")
                        client_socket.sendall("Erreur : Format JSON invalide.".encode("utf-8"))
                        continue

                    program_type = program_data.get("type_de_fichier")
                    program_code = program_data.get("code")

                    if not program_type or not program_code:
                        self.log("[!] Erreur : JSON incomplet. Champs 'type_de_fichier' et 'code' nécessaires.")
                        client_socket.sendall("Erreur : Champs 'type_de_fichier' et 'code' nécessaires.".encode("utf-8"))
                        continue

                    if program_type in ["C", "C++"]:
                        slave_role = "C/C++"
                    elif program_type in ["Java", "Python"]:
                        slave_role = "JAVA/Python"
                    else:
                        self.log(f"[!] Type de programme non supporté : {program_type}.")
                        client_socket.sendall(f"Erreur : Type de programme non supporté.".encode("utf-8"))
                        continue

                    slave_index = self.get_least_busy_slave(slave_role)
                    if slave_index is not None:
                        self.send_program_to_slave(client_socket, slave_role, slave_index, program_data)
                    else:
                        self.log(f"[!] Aucun slave disponible pour {slave_role}.")
                        client_socket.sendall("Erreur : Aucun slave disponible.".encode("utf-8"))
            except Exception as e:
                self.log(f"[!] Erreur lors de la réception du programme : {e}")
                break

    def get_least_busy_slave(self, program_type):
        tasks = self.slave_task_count[program_type]
        for i, count in enumerate(tasks):
            if count < self.max_tasks:
                return i
        return None

    def send_program_to_slave(self, client_socket, program_type, slave_index, program_data):
        try:
            slave_socket = self.slaves[program_type][slave_index]
            self.slave_task_count[program_type][slave_index] += 1

            slave_socket.sendall(json.dumps(program_data).encode("utf-8"))
            self.log(f"[>] Programme envoyé au slave {program_type} (index {slave_index}).")

            response = slave_socket.recv(4096).decode("utf-8")
            self.slave_task_count[program_type][slave_index] -= 1
            client_socket.sendall(response.encode("utf-8"))
            self.log(f"[<] Réponse reçue du slave {program_type} et envoyée au client.")
        except Exception as e:
            self.log(f"[!] Erreur lors de l'envoi au slave ou au client : {e}")

    def fermer_proprement(self):
        self.stop_server()
        self.destroy()

def main():
    app = MasterApp()
    app.mainloop()

if __name__ == "__main__":
    main()
