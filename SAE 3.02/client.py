import customtkinter
from tkinter import filedialog, messagebox
import threading
import socket
import json
import webbrowser
import time
import hashlib

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

HASHED_PASSWORD = "e3afed0047b08059d0fada10f400c1e5"

class PasswordPrompt(customtkinter.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Authentification")
        self.geometry("300x150")
        self.resizable(False, False)

        self.label = customtkinter.CTkLabel(self, text="Veuillez entrer le mot de passe :")
        self.label.pack(pady=10)

        self.password_entry = customtkinter.CTkEntry(self, show="*", width=200)
        self.password_entry.pack(pady=5)

        self.login_button = customtkinter.CTkButton(self, text="Valider", command=self.valide_password)
        self.login_button.pack(pady=10)

    def valide_password(self):
        entered_password = self.password_entry.get()
        entered_hashed = hashlib.md5(entered_password.encode()).hexdigest()
        if entered_hashed == HASHED_PASSWORD:
            self.destroy()
            self.on_success()
        else:
            self.password_entry.delete(0, "end")
            
class Sae(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.client_socket = None
        self.is_connected = False 

        def fermer():
            if self.client_socket:
                self.client_socket.close()
                self.is_connected = False
                self.terminal.insert("0.0", "[*] Déconnexion du serveur.\n\n")
            self.destroy()

        def importer_fichier():
            lang = self.langage_prog.get()

            if lang == "Python":
                Ftype = [("Scripts Python", "*.py")]
            elif lang == "C++":
                Ftype = [("Fichiers C++", "*.cpp;*.cc")]
            elif lang == "C":
                Ftype = [("Fichiers C", "*.c")]
            elif lang == "Java":
                Ftype = [("Fichiers Java", "*.java")]
            else:
                Ftype = []

            fichier = filedialog.askopenfilename(filetypes=Ftype)

            if fichier:
                try:
                    with open(fichier, "r", encoding="utf-8") as file:
                        contenu = file.read()
                    self.programme_txt.delete("0.0", "end")
                    self.programme_txt.insert("0.0", contenu)
                    self.terminal.insert("0.0", f"[*] Fichier importé : {fichier}\n\n")
                except Exception as e:
                    self.terminal.insert("0.0", f"[*] Erreur lors de la lecture du fichier : {e}\n\n")

        def envoyer_txt():
            if self.client_socket and self.is_connected:
                try:
                    programme = self.programme_txt.get("0.0", "end").strip()
                    print(f"Contenu récupéré : {programme}")

                    if not programme:
                        self.terminal.insert("0.0", "[*] Le contenu du programme est vide. Rien à envoyer.\n\n")
                        return

                    lang = self.langage_prog.get()
                    if lang not in ["Python", "C++", "C", "Java"]:
                        self.terminal.insert("0.0", "[*] Aucune extension de fichier valide sélectionnée.\n\n")
                        return

                    payload = {
                        "type_de_fichier": lang,
                        "code": programme,
                    }
                    
                    message = json.dumps(payload)

                    
                    self.client_socket.sendall(message.encode("utf-8"))
                    self.terminal.insert("0.0", "[*] Programme envoyé au serveur avec succès.\n\n")

                except socket.error as e:
                    self.terminal.insert("0.0", f"[*] Erreur de socket lors de l'envoi : {e}\n\n")
                except json.JSONDecodeError as e:
                    self.terminal.insert("0.0", f"[*] Erreur de JSON : {e}\n\n")
                except Exception as e:
                    self.terminal.insert("0.0", f"[*] Autre erreur : {e}\n\n")
            else:
                self.terminal.insert("0.0", "[*] Vous devez d'abord vous connecter au serveur !\n\n")
        
        def ouvrir_github():
            url = "https://github.com/Link67000/SAE3.02"  
            webbrowser.open(url)

        def recevoir_reponse():
            if self.client_socket and self.is_connected:
                try:
                    while True: 
                        response = self.client_socket.recv(4096).decode()
                        if response:
                            
                            self.after(0, self.terminal.insert, "0.0", f"[*] Réponse reçue : {response}\n\n")
                        else:
                            break
                except Exception as e:
                    self.after(0, self.terminal.insert, "0.0", f"[*] Erreur lors de la réception de la réponse : {e}\n\n")
                    self.is_connected = False

        def connexion():
            try:
                self.client_socket = socket.socket()
                host = self.addr.get()
                port = int(self.port.get())
                self.terminal.insert("0.0", f"[*] Connexion au serveur {host}:{port}...\n\n")
                self.client_socket.connect((host, port))
                self.is_connected = True
                time.sleep(1)
                self.terminal.insert("0.0", "[*] Connecté au serveur avec succès.\n\n")

                self.client_socket.sendall("client".encode())

                threading.Thread(target=recevoir_reponse, daemon=True).start()

            except Exception as e:
                self.is_connected = False
                self.terminal.insert("0.0", f"[*] Erreur de connexion : {e}\n\n")

        def thread_connexion():
            threading.Thread(target=connexion).start()

        self.title('SAE Client')
        self.geometry('820x400')
        self.resizable(False, False)

        self.addr_txt = customtkinter.CTkLabel(self, width=100, height=30, text="adresse :")
        self.addr_txt.place(x=10, y=10)
        self.addr = customtkinter.CTkEntry(self, width=170, height=30, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, "192.168.y.x")

        self.port_txt = customtkinter.CTkLabel(self, width=100, height=30, text="port :")
        self.port_txt.place(x=10, y=50)
        self.port = customtkinter.CTkEntry(self, width=170, height=30, justify="center")
        self.port.place(x=120, y=50)
        self.port.insert(0, "1111")

        lang = ["Python", "C++", "C", "Java"]
        self.prog_txt = customtkinter.CTkLabel(self, width=100, height=30, text="Type de fichier :")
        self.prog_txt.place(x=200, y=360)
        self.langage_prog = customtkinter.CTkComboBox(self, state="readonly", values=lang, width=120, height=30, justify="center")
        self.langage_prog.set("Python")
        self.langage_prog.place(x=305, y=360)

        self.connexion = customtkinter.CTkButton(self, text="connexion", width=280, height=30, command=thread_connexion)
        self.connexion.place(x=10, y=90)

        self.envoyer = customtkinter.CTkButton(self, text="envoyer", width=120, height=30, command=envoyer_txt)
        self.envoyer.place(x=565, y=360)

        self.quitter = customtkinter.CTkButton(self, text="quitter", width=120, height=30, command=fermer)
        self.quitter.place(x=695, y=360)

        self.programme_txt = customtkinter.CTkTextbox(self, width=510, height=340)
        self.programme_txt.place(x=305, y=10)
        self.programme_txt.insert(0.0, "Zone d'insertion pour les programmes :")

        self.etat_txt = customtkinter.CTkLabel(self, width=100, height=30, text="Etat client et retour sur programme :")
        self.etat_txt.place(x=10, y=125)
        self.terminal = customtkinter.CTkTextbox(self, width=280, height=190)
        self.terminal.place(x=10, y=160)
        self.terminal.insert("0.0", "")

        self.aide_txt = customtkinter.CTkButton(self, text="?", width=30, height=30, command=ouvrir_github)
        self.aide_txt.place(x=10, y=360)

        self.bouton_importer = customtkinter.CTkButton(self, text="importer", width=120, height=30, command=importer_fichier)
        self.bouton_importer.place(x=435, y=360)

def main():
    def start_sae():
        app = Sae()
        app.mainloop()

    password_prompt = PasswordPrompt(on_success=start_sae)
    password_prompt.mainloop()

if __name__ == '__main__':
    main()
