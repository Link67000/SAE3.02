import customtkinter
from tkinter import filedialog
import threading
import socket

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class Sae(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.client_socket = None
        
        def fermer():
            if self.client_socket:
                self.client_socket.close()
                self.destroy()
            else:
                print("[*] Vous avez fermé le programme client ! ")
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
                except Exception as e:
                    print(f"[*] Erreur lors de la lecture du fichier : {e}")


        def envoyer_txt():
            if self.client_socket:
                try:
                    programme = self.programme_txt.get("0.0", "end").strip()
                    self.client_socket.send(f"{programme}\n".encode())
                except Exception as e:
                    self.terminal.delete("0.0", "end")
                    self.terminal.insert("0.0",f"vous n'êtes pas connecté ")
            else:
                self.terminal.delete("0.0", "end")
                self.terminal.insert("0.0","[*] Vous devez vous connecter !\n\n")

        def connexion():
            try:
                self.client_socket = socket.socket()
                host = self.addr.get()
                port = int(self.port.get())
                self.client_socket.connect((host, port))
                message = "client connecté"
                self.client_socket.send(f"{message}\n".encode())
                message = self.client_socket.recv(1024).decode()
                self.terminal.delete("0.0", "end")
                self.terminal.insert("0.0", f"[*] Réponse du serveur : {message}")
            except Exception as e:
                self.terminal.delete("0.0", "end")
                self.terminal.insert("0.0", f"[*] Erreur de connexion : {e}")


        def thread_connexion():
            threading.Thread(target=connexion).start()

        self.title('SAE Client')
        self.geometry('820x400')
        self.resizable(False, False)

    # Champ adresse
        self.addr_txt = customtkinter.CTkLabel(self, width=100, height=30, text="adresse :")
        self.addr_txt.place(x=10, y=10)
        self.addr = customtkinter.CTkEntry(self, width=170, height=30, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, "127.0.0.1")

    # Champ port
        self.port_txt = customtkinter.CTkLabel(self, width=100, height=30, text="port :")
        self.port_txt.place(x=10, y=50)
        self.port = customtkinter.CTkEntry(self, width=170, height=30, justify="center")
        self.port.place(x=120, y=50)
        self.port.insert(0, "10000")

    # champ Langage de prog
        lang = ["Python", "C++", "C", "Java"]
        self.prog_txt = customtkinter.CTkLabel(self, width=100, height=30, text="Type de fichier :")
        self.prog_txt.place(x=200, y=360)
        self.langage_prog = customtkinter.CTkComboBox(self,state="readonly", values=lang, width=120, height=30, justify="center")
        self.langage_prog.set("Python")
        self.langage_prog.place(x=305, y=360)

    # champ connexion
        self.connexion = customtkinter.CTkButton(self, text="connexion", width=280, height=30, command=thread_connexion)
        self.connexion.place(x=10, y=90)

    # Bouton envoyer
        self.envoyer = customtkinter.CTkButton(self, text="envoyer", width=120, height=30, command=envoyer_txt)
        self.envoyer.place(x=565, y=360)

    # Bouton quitter
        self.quitter = customtkinter.CTkButton(self, text="quitter", width=120, height=30, command=fermer)
        self.quitter.place(x=695, y=360)

    # Champ programme
        self.programme_txt = customtkinter.CTkTextbox(self, width=510, height=340)
        self.programme_txt.place(x=305, y=10)
        self.programme_txt.insert(0.0, "Zone d'insertion pour les programmes :")

    # Champ terminal
        self.etat_txt = customtkinter.CTkLabel(self, width=100, height=30, text="Etat serveur et retour sur programme :")
        self.etat_txt.place(x=10, y=125)
        self.terminal = customtkinter.CTkTextbox(self, width=280, height=190)
        self.terminal.place(x=10, y=160)
        self.terminal.insert(0.0,"")
        
    # champ aide
        self.aide_txt = customtkinter.CTkButton(self, text="?", width=30, height=30)
        self.aide_txt.place(x=10, y=360)

    # champ importer
        self.bouton_importer = customtkinter.CTkButton(self, text="importer", width=120, height=30, command=importer_fichier)
        self.bouton_importer.place(x=435, y=360)


def main():
    app = Sae()
    app.mainloop()


if __name__ == '__main__':
    main()
