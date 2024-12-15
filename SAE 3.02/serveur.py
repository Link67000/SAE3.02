import customtkinter
from tkinter import filedialog
import threading
import socket

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class Sae(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.server_socket = None
        self.en_fonctionnement = None
        
        def fermer():
            if self.server_socket:
                self.server_socket.close()
                self.destroy()
            else:
                print("[*] Vous avez fermé le programme serveur ! ")
                self.destroy()
                
                
        def on_off():
            if not self.en_fonctionnement:
                start()
                self.démarrer_eteindre.configure(text="Eteindre")
                self.en_fonctionnement = True
            else:
                stop()    
                self.démarrer_eteindre.configure(text="Allumer")
                self.en_fonctionnement = False
        
        def stop():
            self.server_socket.close()
            self.suivi_txt.insert("1.0","[*] Vous avez fermé le serveur !\n")

        def start():
            self.server_socket = socket.socket()
            host = self.addr.get()
            port = int(self.port.get())
            self.server_socket.bind((host, port))
            self.server_socket.listen(1)
            self.suivi_txt.insert("1.0",f"[*] Serveur Lancé addr : {self.addr.get()}, port : {self.port.get()} !\n")
            

        self.title('SAE Serveur maitre')
        self.geometry('400x500')
        self.resizable(True, False)


        self.addr_txt = customtkinter.CTkLabel(self, width=100, height=30, text="adresse :")
        self.addr_txt.place(x=10, y=10)
        self.addr = customtkinter.CTkEntry(self, width=150, height=30, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, "0.0.0.0")
        
        self.port_txt = customtkinter.CTkLabel(self, width=100, height=30, text="port :")
        self.port_txt.place(x=10, y=50)
        self.port = customtkinter.CTkEntry(self, width=150, height=30, justify="center")
        self.port.place(x=120, y=50)
        self.port.insert(0, "10000")
        
        self.max_prog = customtkinter.CTkLabel(self, width=100, height=30, text="programmes max :")
        self.max_prog.place(x=10, y=90)
        self.programme = customtkinter.CTkEntry(self, width=150, height=30, justify="center")
        self.programme.place(x=120, y=90)
        self.programme.insert(0, "4")
        
        self.démarrer_eteindre = customtkinter.CTkButton(self,text="Allumer", width=380, height=30, command=on_off)
        self.démarrer_eteindre.place(x=10, y=130)
        
        self.suivi_txt = customtkinter.CTkTextbox(self, width=380, height=280)
        self.suivi_txt.place(x=10, y=170)
        
        self.quitter = customtkinter.CTkButton(self, text="quitter", width=120, height=30, command=fermer)
        self.quitter.place(x=270, y=460)
        
def main():
    app = Sae()
    app.mainloop()


if __name__ == '__main__':
    main()











"""import socket
import time

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 10000))
server_socket.listen(1)
print("Serveur lancé")

try:
    while True:
        conn, address = server_socket.accept()

        while True:
            message = conn.recv(1024).decode()
            if not message:
                break

            if message == "arret":
                print("Arrêt du serveur demandé.")
                conn.send("Serveur arrêté".encode())
                time.sleep(1)
                conn.close()
                server_socket.close()
                exit()
            else:
                print("Message reçu du client :", message)
                reply = "Message reçu"
                conn.send(reply.encode())
            

        conn.close()

finally:
    server_socket.close()
"""
