"""Cliente de teste para o chat TCP

Uso:
  - python client.py --host 127.0.0.1 --port 12345
  - Será pedido o seu user_id (envie o mesmo user_id que existe no banco)

Comandos no prompt:
  /general <mensagem>         - envia mensagem de broadcast
  /private <user> <mensagem>  - envia mensagem privada para <user>
  /group <group_id> <mensagem>- envia mensagem para grupo
  /json <raw-json>            - envia o JSON fornecido (sem \n)
  /quit                       - fecha o cliente

O cliente mantém uma thread que recebe e imprime mensagens do servidor.
"""
import socket
import threading
import argparse
import os
import json
import sys


def recv_loop(sock: socket.socket):
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("[conexão fechada pelo servidor]")
                break
            try:
                # tenta decodificar e imprimir como texto
                print(data.decode("utf-8"))
            except Exception:
                print(repr(data))
    except Exception as e:
        print(f"Erro no loop de recepção: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 12345)))
    args = parser.parse_args()

    host = args.host
    port = args.port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"Não foi possível conectar ao servidor {host}:{port}: {e}")
        sys.exit(1)

    # start receiver thread
    t = threading.Thread(target=recv_loop, args=(sock,), daemon=True)
    t.start()

    # read initial server prompt and send user_id
    try:
        # try to read server prompt (non-blocking short wait)
        # we'll just prompt the user locally
        user_id = input("Seu user_id: ").strip()
        if not user_id:
            print("user_id é obrigatório")
            sock.close()
            return
        sock.sendall(user_id.encode("utf-8"))

        print("Comandos: /general, /private, /group, /json, /quit")
        while True:
            line = input('> ').strip()
            if not line:
                continue
            if line.startswith('/quit'):
                break
            if line.startswith('/general '):
                text = line[len('/general '):]
                envelope = {"type": "general", "message": text}
                sock.sendall(json.dumps(envelope, ensure_ascii=False).encode('utf-8') + b"\n")
            elif line.startswith('/private '):
                parts = line.split(' ', 2)
                if len(parts) < 3:
                    print("Uso: /private <user> <mensagem>")
                    continue
                to_user = parts[1]
                text = parts[2]
                envelope = {"type": "private", "to": to_user, "message": text}
                sock.sendall(json.dumps(envelope, ensure_ascii=False).encode('utf-8') + b"\n")
            elif line.startswith('/group '):
                parts = line.split(' ', 2)
                if len(parts) < 3:
                    print("Uso: /group <group_id> <mensagem>")
                    continue
                group_id = parts[1]
                text = parts[2]
                envelope = {"type": "group", "group_id": group_id, "message": text}
                sock.sendall(json.dumps(envelope, ensure_ascii=False).encode('utf-8') + b"\n")
            elif line.startswith('/json '):
                raw = line[len('/json '):]
                # send raw JSON as provided
                try:
                    # validate JSON
                    obj = json.loads(raw)
                    sock.sendall(json.dumps(obj, ensure_ascii=False).encode('utf-8') + b"\n")
                except json.JSONDecodeError:
                    print("JSON inválido")
            else:
                # default: send as general message
                envelope = {"type": "general", "message": line}
                sock.sendall(json.dumps(envelope, ensure_ascii=False).encode('utf-8') + b"\n")

    finally:
        try:
            sock.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
