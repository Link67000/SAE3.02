import socket
import threading
import json
import subprocess
import os
import uuid
import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class ApplicationEsclave(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.socket_client = None
        self.en_cours = False
        self.verrou = threading.Lock()

        self.title("Esclave")
        self.geometry("500x340")
        self.resizable(False, False)

        self.master_addr_txt = customtkinter.CTkLabel(self, text="Adresse du Master :")
        self.master_addr_txt.place(x=10, y=10)
        self.adresse_master = customtkinter.CTkEntry(self, width=150, justify="center")
        self.adresse_master.place(x=175, y=10)
        self.adresse_master.insert(0, "192.168.x.y")

        self.master_port_txt = customtkinter.CTkLabel(self, text="Port du Master :")
        self.master_port_txt.place(x=10, y=50)
        self.port_master = customtkinter.CTkEntry(self, width=150, justify="center")
        self.port_master.place(x=175, y=50)
        self.port_master.insert(0, "1111")

        self.bouton_demarrer_arreter = customtkinter.CTkButton(self, text="Démarrer", width=480, height=30, command=self.basculer_connexion)
        self.bouton_demarrer_arreter.place(x=10, y=90)

        self.boite_log = customtkinter.CTkTextbox(self, width=480, height=200)
        self.boite_log.place(x=10, y=130)

        self.protocol("WM_DELETE_WINDOW", self.fermer_proprement)

    def log(self, message):
        self.boite_log.insert("1.0", message + "\n\n")
        print(message)

    def basculer_connexion(self):
        if not self.en_cours:
            self.demarrer_client()
            self.bouton_demarrer_arreter.configure(text="Arrêter")
        else:
            self.arreter_client()
            self.bouton_demarrer_arreter.configure(text="Démarrer")

    def demarrer_client(self):
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect((self.adresse_master.get(), int(self.port_master.get())))
            self.en_cours = True
            self.log("[*] Connecté au Master.")

            role = "C/C++"
            self.socket_client.sendall(role.encode("utf-8"))

            threading.Thread(target=self.ecouter_master, daemon=True).start()
        except Exception as e:
            self.log(f"[!] Erreur : {e}")

    def arreter_client(self):
        self.en_cours = False
        if self.socket_client:
            self.socket_client.close()
            self.socket_client = None
        self.log("[*] Déconnecté du Master.")

    def ecouter_master(self):
        while self.en_cours:
            try:
                message = self.socket_client.recv(4096).decode("utf-8")
                if not message:
                    break

                try:
                    donnees = json.loads(message)
                    type_fichier = donnees.get("type_de_fichier", "Inconnu")
                    code_programme = donnees.get("code", "")
                    self.log(f"[*] Tâche reçue : {type_fichier}\n[*] Programme: {code_programme}")

                    threading.Thread(target=self.traiter, args=(type_fichier, code_programme)).start()

                except json.JSONDecodeError:
                    self.log("[!] Erreur : données non valides reçues.")
            except Exception as e:
                self.log(f"[!] Erreur de réception : {e}")
                break

    def traiter(self, type_fichier, code_programme):
        try:
            nom_fichier = f"/tmp/temp_{uuid.uuid4().hex}.c" if type_fichier == "C" else f"/tmp/temp_{uuid.uuid4().hex}.cpp"
            executable = f"/tmp/temp_{uuid.uuid4().hex}"

            compilateur = "gcc" if type_fichier == "C" else "g++" if type_fichier == "C++" else None
            if not compilateur:
                self.log(f"[!] Type de fichier inconnu : {type_fichier}")
                return

            with open(nom_fichier, "w") as f:
                f.write(code_programme)

            commande_compilation = [compilateur, nom_fichier, "-o", executable]
            processus_compilation = subprocess.run(commande_compilation, capture_output=True, text=True)

            if processus_compilation.returncode != 0:
                self.log(f"[!] Erreur de compilation : {processus_compilation.stderr}")
                reponse = json.dumps({"erreur": processus_compilation.stderr})
                self.socket_client.sendall(reponse.encode("utf-8"))
                return

            subprocess.run(["chmod", "+x", executable])

            processus_execution = subprocess.run([executable], capture_output=True, text=True)

            if processus_execution.returncode != 0:
                self.log(f"[!] Erreur d'exécution : {processus_execution.stderr}")
                reponse = json.dumps({"erreur": processus_execution.stderr})
            else:
                self.log(f"[*] Résultat : {processus_execution.stdout}")
                reponse = json.dumps({"resultat": processus_execution.stdout})

            self.socket_client.sendall(reponse.encode("utf-8"))

        except Exception as e:
            self.log(f"[!] Erreur : {e}")
        finally:
            if os.path.exists(nom_fichier):
                os.remove(nom_fichier)
            if os.path.exists(executable):
                os.remove(executable)

    def fermer_proprement(self):
        self.arreter_client()
        self.destroy()


def main():
    app = ApplicationEsclave()
    app.mainloop()


if __name__ == "__main__":
    main()
