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

        def switch():
            pass
        
        def fermer():
            if self.client_socket:
                self.client_socket.close()
                self.destroy()
            else:
                print("[*] Vous avez fermé le programme client ! ")
                self.destroy()

        def importer_fichier():
            fichier = filedialog.askopenfilename(
                filetypes=[
                    ("Scripts Python", "*.py"),
                    ("Fichiers C++", "*.cpp;*.hpp"),
                    ("Fichiers C", "*.c;*.h"),
                    ("Fichiers JavaScript", "*.js"),
                ]
            )
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
                    print(f"[*] Erreur lors de l'envoi : {e}")
            else:
                print("[*] Vous devez d'abord vous connecter au serveur !")

        def connexion():
            self.client_socket = socket.socket()
            host = self.addr.get()
            port = int(self.port.get())
            self.client_socket.connect((host, port))
            message = "Je suis le Client ! et bien connecté !"
            self.client_socket.send(f"{message}\n".encode())

        def thread_connexion():
            threading.Thread(target=connexion).start()

        self.title('SAE Client')
        self.geometry('800x400')
        self.resizable(False, False)

    # Champ adresse
        self.addr_txt = customtkinter.CTkLabel(self, width=100, height=30, text="adresse :")
        self.addr_txt.place(x=10, y=10)
        self.addr = customtkinter.CTkEntry(self, width=150, height=30, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, "127.0.0.1")

    # Champ port
        self.port_txt = customtkinter.CTkLabel(self, width=100, height=30, text="port :")
        self.port_txt.place(x=10, y=50)
        self.port = customtkinter.CTkEntry(self, width=150, height=30, justify="center")
        self.port.place(x=120, y=50)
        self.port.insert(0, "10000")

    # champ Langage de prog
        lang = ["Python", "C++", "C", "JS"]
        self.prog_txt = customtkinter.CTkLabel(self, width=100, height=30, text="fichier :")
        self.prog_txt.place(x=10, y=90)
        self.langage_prog = customtkinter.CTkComboBox(self, values=lang, width=150, height=30, justify="center")
        self.langage_prog.place(x=120, y=90)

    # champ connexion
        self.connexion = customtkinter.CTkButton(self, text="connexion", width=150, height=30, command=thread_connexion)
        self.connexion.place(x=120, y=130)

    # Bouton envoyer
        self.envoyer = customtkinter.CTkButton(self, text="envoyer", width=120, height=30, command=envoyer_txt)
        self.envoyer.place(x=545, y=360)

    # Bouton quitter
        self.quitter = customtkinter.CTkButton(self, text="quitter", width=120, height=30, command=fermer)
        self.quitter.place(x=675, y=360)

    # Champ programme
        self.programme_txt = customtkinter.CTkTextbox(self, width=510, height=340)
        self.programme_txt.place(x=285, y=10)
        self.programme_txt.insert(0.0, "Zone d'insertion pour les programmes :")

    # champ aide
        self.aide_txt = customtkinter.CTkButton(self, text="?", width=30, height=30)
        self.aide_txt.place(x=10, y=360)

    # champ importer
        self.bouton_importer = customtkinter.CTkButton(self, text="importer", width=120, height=30, command=importer_fichier)
        self.bouton_importer.place(x=50, y=360)

    # Etat connexion client-serveur
        self.etat_txt = customtkinter.CTkLabel(self, width=100, height=30, text="Etat connexion")
        self.etat_txt.place(x=10, y=170)
        self.etat_connexion = customtkinter.CTkSwitch(self, command=switch,text=None, width=150,height=30, state="disabled",onvalue="on",offvalue="off")
        self.etat_connexion.place(x=120, y =170)

def main():
    app = Sae()
    app.mainloop()


if __name__ == '__main__':
    main()
