import customtkinter
from tkinter import *

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class Sae(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        def fermer():
            print("[*] vous avez fermer le programme client ! ")
            self.destroy()
            
        def envoyer():
            pass
            
        
        self.title('SAE Client')
        self.geometry('600x400')
        self.resizable(False, False)
    
    #Champ adresse 
        self.addr_txt = customtkinter.CTkLabel(self, width=100, height=30,text="adresse :")
        self.addr_txt.place(x=10,y=10)
        self.addr = customtkinter.CTkEntry(self, width=150, height=30, justify="center")
        self.addr.place(x=120, y=10)
        self.addr.insert(0, "127.0.0.1")
        
    #Champ port    
        self.port_txt = customtkinter.CTkLabel(self, width=100, height=30 ,text="port :")
        self.port_txt.place(x=10,y=50)
        self.port = customtkinter.CTkEntry(self,width=150,height=30, justify="center")
        self.port.place(x=120,y=50)
        self.port.insert(0, "10000")
        
    #champ Langage de prog 
        lang = ["Python","C++","C","JS"]
        self.prog_txt = customtkinter.CTkLabel(self, width=100, height=30 ,text="fichier :")
        self.prog_txt.place(x=10,y=90)
        self.langage_prog = customtkinter.CTkComboBox(self,values=lang,width=150,height=30, justify="center")
        self.langage_prog.place(x=120,y=90)
        
    #Champ RAM    
        self.RAM_txt = customtkinter.CTkLabel(self, width=100, height=30 ,text="RAM max :")
        self.RAM_txt.place(x=10,y=130)
        self.RAM = customtkinter.CTkEntry(self,width=150,height=30, justify="center")
        self.RAM.place(x=120,y=130)
        self.RAM.insert(0, "4")    
        
    #champ connexion 
        self.connexion = customtkinter.CTkButton(self,text="connexion", width=150, height=30)
        self.connexion.place(x=120,y=170)
    
    #Bouton envoyer     
        self.envoyer = customtkinter.CTkButton(self,text="envoyer", width=120, height=30)
        self.envoyer.place(x=345,y=360)
        
    #Bouton quitter    
        self.quitter = customtkinter.CTkButton(self,text="quitter", width=120, height=30, command=fermer)
        self.quitter.place(x=475,y=360)
        
    #Champ programme 
        self.programme_txt = customtkinter.CTkTextbox(self,width=310,height=340)
        self.programme_txt.place(x=285,y=10)
        
    #champ aide 
        self.aide_txt = customtkinter.CTkButton(self,text="?",width=30,height=30)
        self.aide_txt.place(x=10,y=360)
        
    #champ importer 
        self.programme_txt = customtkinter.CTkButton(self,text="importer", width=120, height=30)
        self.programme_txt.place(x=50,y=360)

    
app = Sae()
app.mainloop()