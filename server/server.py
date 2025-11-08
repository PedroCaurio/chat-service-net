import socket
import os
import json
from dotenv import load_dotenv
from registry import get_command
import threading

from services import action, login

load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 12345))

client = {}

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            try:
                msg = json.loads(data.decode())
                msg_type = msg.get("type")
                payload = msg.get("payload", {})

                if msg_type == "request" and payload:
                    command = payload.get("command")
                    func = get_command(command)
                    if func:
                        result = func(**{k: v for k, v in payload.items() if k != "command"})
                        response = {"type": "status", "payload": result}
                    else:
                        response = {"type": "error", "payload": {"message": f"Comando '{command}' não encontrado."}}

                else:
                    response = {"type": "error", "payload": {"message": "Tipo de mensagem não suportado."}}

            except Exception as e:
                response = {"type": "error", "payload": {"message": str(e)}}

            conn.sendall(json.dumps(response).encode() + b"\n")

def main():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escutando em {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()

            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()

            print(f"[THREAD] Novo cliente em {addr}, total de threads ativas: {threading.active_count() - 1}")

            handle_client(conn, addr)

if __name__ == "__main__":
    main()
