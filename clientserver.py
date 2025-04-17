import socket
import requests
import time
import threading

SERVER_URL = "https://flaskserver-1-mtrp.onrender.com/"
PORT = 5001  # Port fixe utilisé pour la connexion socket

# Récupérer l'IP publique via une API
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json()['ip']
    except Exception as e:
        print(f"Erreur IP publique : {e}")
        return None

# Envoi de l'adresse IP publique + port au serveur
# Envoi de l'adresse IP publique + port au serveur
def send_ip_to_server(my_uid):
    ip = get_public_ip()
    if not ip:
        print("Impossible d'obtenir l'IP publique.")
        return
    data = {
        "value1": int(my_uid),
        "value2": ip,
        "value3": int(PORT)  # <--- Assure-toi qu'il est bien un entier
    }
    while True:
        try:
            response = requests.post(f"{SERVER_URL}/submit", json=data)
            print(f"IP envoyée au serveur : {response.text}")
        except Exception as e:
            print(f"Erreur d'envoi : {e}")
        time.sleep(1)


# Reçoit les messages via socket
def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if msg:
                print(f"\nMessage reçu : {msg.decode('utf-8')}")
            else:
                break
        except:
            break

# Tente de se connecter à l'utilisateur distant
def connect_to_peer(ip_and_port):
    ip, port = ip_and_port.split(":")
    port = int(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, port))
            print(f"✅ Connecté à {ip}:{port}")
            threading.Thread(target=receive_messages, args=(s,), daemon=True).start()
            while True:
                msg = input("Vous : ")
                s.sendall(msg.encode())
        except Exception as e:
            print(f"Erreur de connexion : {e}")

# Vérifie toutes les 5 sec si l'utilisateur distant est présent
def wait_for_peer(remote_uid):
    print(f"⏳ En attente de l'utilisateur UID {remote_uid}...")
    while True:
        try:
            response = requests.post(f"{SERVER_URL}/getin", json={"value1": remote_uid})
            if response.text != "False":
                print(f"👤 Utilisateur trouvé ! IP/Port = {response.text}")
                connect_to_peer(response.text)
                break
        except Exception as e:
            print(f"Erreur serveur : {e}")
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
