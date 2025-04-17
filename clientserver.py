import socket
import requests
import time
import threading

SERVER_URL = "https://flaskserver-1-mtrp.onrender.com"
PORT = 5001  # Port fixe utilisé pour la connexion socket

# Récupérer l'IP publique via une API
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json()['ip']
    except Exception as e:
        print(f"❌ Erreur IP publique : {e}")
        return None

# Envoi de l'adresse IP publique + port au serveur
def send_ip_to_server(my_uid):
    last_ip = None
    while True:
        ip = get_public_ip()
        if ip != last_ip:
            last_ip = ip
            data = {
                "value1": int(my_uid),
                "value2": str(ip),
                "value3": PORT
            }
            try:
                print("📤 Data envoyée :", data)
                response = requests.post(f"{SERVER_URL}/submit", json=data)
                print(f"✅ Réponse du serveur : {response.text}")
            except Exception as e:
                print(f"❌ Erreur d'envoi : {e}")
        time.sleep(5)  # Vérifier toutes les 5 secondes



# Reçoit les messages via socket
def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if msg:
                print(f"\n📨 Message reçu : {msg.decode('utf-8')}")
            else:
                break
        except:
            break

# Tente de se connecter à l'utilisateur distant
def connect_to_peer(ip_and_port):
    try:
        ip, port = ip_and_port.split(":")
        port = int(port)
    except ValueError:
        print(f"❌ Format d'IP ou de port incorrect : {ip_and_port}")
        return
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, port))
            print(f"✅ Connecté à {ip}:{port}")
            threading.Thread(target=receive_messages, args=(s,), daemon=True).start()
            while True:
                msg = input("Vous : ")
                s.sendall(msg.encode())
        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")


# Vérifie toutes les 5 sec si l'utilisateur distant est présent
def wait_for_peer(remote_uid):
    print(f"⏳ En attente de l'utilisateur UID {remote_uid}...")
    while True:
        try:
            response = requests.post(f"{SERVER_URL}/getin", json={"value1": str(remote_uid)})
            response_json = response.json()  # Décoder la réponse en JSON
            if "message" in response_json and response_json["message"] != "Utilisateur non trouvé":
                ip_port = response_json["message"]
                print(f"👤 Utilisateur trouvé ! IP/Port = {ip_port}")
                connect_to_peer(ip_port)
                break
        except Exception as e:
            print(f"❌ Erreur serveur : {e}")
        time.sleep(5)


# Écoute les connexions entrantes pour recevoir des messages
def listen_for_incoming():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", PORT))
    s.listen()
    print(f"📡 En écoute sur le port {PORT}...")
    conn, addr = s.accept()
    print(f"🔗 Connexion entrante depuis {addr}")
    threading.Thread(target=receive_messages, args=(conn,), daemon=True).start()
    while True:
        msg = input("Vous : ")
        conn.sendall(msg.encode())

# Lancement du client
def main():
    my_uid = input("Entrez votre UID : ")
    remote_uid = input("Entrez l'UID de la personne à contacter : ")

    # Envoi de l'IP en fond
    threading.Thread(target=send_ip_to_server, args=(my_uid,), daemon=True).start()

    # Démarrage du serveur local pour recevoir les messages
    threading.Thread(target=listen_for_incoming, daemon=True).start()

    # Attente de la personne cible
    wait_for_peer(remote_uid)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
