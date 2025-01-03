import socket 
import threading
import json
import subprocess
import os
import uuid
import customtkinter
import re 

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class SlaveApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.client_socket = None
        self.running = False
        self.lock = threading.Lock()

        self.title("Esclave")
        self.geometry("500x340")
        self.resizable(False, False)

        self.master_addr_txt = customtkinter.CTkLabel(self, text="Adresse du Master :")
        self.master_addr_txt.place(x=10, y=10)
        self.master_addr = customtkinter.CTkEntry(self, width=150, justify="center")
        self.master_addr.place(x=175, y=10)
        self.master_addr.insert(0, "192.168.x.y")

        self.master_port_txt = customtkinter.CTkLabel(self, text="Port du Master :")
        self.master_port_txt.place(x=10, y=50)
        self.master_port = customtkinter.CTkEntry(self, width=150, justify="center")
        self.master_port.place(x=175, y=50)
        self.master_port.insert(0, "1111")

        self.start_stop_button = customtkinter.CTkButton(self, text="Démarrer", width=480, height=30, command=self.toggle_connection)
        self.start_stop_button.place(x=10, y=90)

        self.log_box = customtkinter.CTkTextbox(self, width=480, height=200)
        self.log_box.place(x=10, y=130)

        self.protocol("WM_DELETE_WINDOW", self.fermer_proprement)

    def log(self, message):
        self.log_box.insert("1.0", message + "\n\n")
        print(message)

    def toggle_connection(self):
        if not self.running:
            self.start_client()
            self.start_stop_button.configure(text="Arrêter")
        else:
            self.stop_client()
            self.start_stop_button.configure(text="Démarrer")

    def start_client(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.master_addr.get(), int(self.master_port.get())))
            self.running = True
            self.log("[*] Connecté au Master.")
            role = "JAVA/Python"
            self.client_socket.sendall(role.encode("utf-8"))

            threading.Thread(target=self.listen_to_master, daemon=True).start()
        except Exception as e:
            self.log(f"[!] Erreur : {e}")

    def stop_client(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        self.log("[*] Déconnecté du Master.")

    def listen_to_master(self):
        while self.running:
            try:
                message = self.client_socket.recv(4096).decode("utf-8")
                if not message:
                    break

                try:
                    data = json.loads(message)
                    file_type = data.get("type_de_fichier", "Inconnu")
                    program_code = data.get("code", "")
                    self.log(f"[*] Tâche reçue : {file_type}\n[*] Programme: {program_code}")

                    threading.Thread(target=self.process_task, args=(file_type, program_code)).start()

                except json.JSONDecodeError:
                    self.log("[!] Erreur : données non valides reçues.")
            except Exception as e:
                self.log(f"[!] Erreur de réception : {e}")
                break

    def extract_java_class_name(self, code):
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            self.log(f"[!] {match}")
            return match.group(1)
        else:
            self.log("[!] Aucune classe publique trouvée.")
            return "Main" 

    def process_task(self, file_type, program_code):
        try:
            filename = f"/tmp/temp_{uuid.uuid4().hex}.java" if file_type == "Java" else f"/tmp/temp_{uuid.uuid4().hex}.py"
            executable = f"/tmp/temp_{uuid.uuid4().hex}"

            if file_type == "Java":
                class_name = self.extract_java_class_name(program_code)

                filename = f"/tmp/{class_name}.java"
                self.log(f"[!] nom {filename}")

                with open(filename, "w") as f:
                    f.write(program_code)

                compile_command = ["javac", filename]
                compile_process = subprocess.run(compile_command, capture_output=True, text=True)

                if compile_process.returncode != 0:
                    self.log(f"[!] Erreur de compilation : {compile_process.stderr}")
                    response = json.dumps({"error": compile_process.stderr})
                    self.client_socket.sendall(response.encode("utf-8"))
                    return

                execute_command = ["java", "-cp", "/tmp", class_name] 

            elif file_type == "Python":
                with open(filename, "w") as f:
                    f.write(program_code)
                execute_command = ["python3", filename]
            else:
                self.log(f"[!] Type de fichier inconnu : {file_type}")
                return

            execute_process = subprocess.run(execute_command, capture_output=True, text=True)

            if execute_process.returncode != 0:
                self.log(f"[!] Erreur d'exécution : {execute_process.stderr}")
                response = json.dumps({"error": execute_process.stderr})
            else:
                self.log(f"[*] Résultat : {execute_process.stdout}")
                response = json.dumps({"resultat": execute_process.stdout})

            self.client_socket.sendall(response.encode("utf-8"))

        except Exception as e:
            self.log(f"[!] Erreur : {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def fermer_proprement(self):
        self.stop_client()
        self.destroy()


def main():
    app = SlaveApp()
    app.mainloop()


if __name__ == "__main__":
    main()
