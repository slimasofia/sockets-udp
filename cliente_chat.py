# Atividade 1: Chat UDP Simples
# Implementação do Cliente

import socket
import threading
import sys
import time

# Configurações do cliente
SERVIDOR_HOST = 'localhost'     # Endereço do servidor
SERVIDOR_PORT = 9500            # Porta do servidor
BUFFER_SIZE = 1024

# Criar socket UDP
try:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.settimeout(5.0)  # Timeout para operações de socket
except socket.error as e:
    print(f"Erro ao criar socket: {e}")
    sys.exit(1)

# Função para receber mensagens
def receber_mensagens():
    while True:
        try:
            dados, _ = cliente.recvfrom(BUFFER_SIZE)
            mensagem = dados.decode('utf-8')
            print(f"\n{mensagem}\nDigite sua mensagem (/sair para sair): ", end="")
        except socket.timeout:
            continue  # Timeout normal, continua esperando
        except Exception as e:
            print(f"\nErro ao receber mensagem: {e}")
            break

# Registrar usuário no servidor
def registrar_usuario(nome):
    try:
        mensagem_registro = f"/registro:{nome}"
        cliente.sendto(mensagem_registro.encode('utf-8'), (SERVIDOR_HOST, SERVIDOR_PORT))
        
        # esperar confirmação (se o servidor não responder, o timeout irá capturar)
        dados, _ = cliente.recvfrom(BUFFER_SIZE)
        resposta = dados.decode('utf-8')
        
        if "entrou no chat" in resposta or nome in resposta:
            print(resposta)
            return True
        else:
            print(f"Erro no registro: {resposta}")
            return False
            
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")
        return False

# Função principal
def main():
    if len(sys.argv) != 2:
        print("Uso: python cliente_chat.py <seu_nome>")
        sys.exit(1)

    nome_usuario = sys.argv[1]

    try:
        # Registrar no servidor
        if not registrar_usuario(nome_usuario):
            print("Falha no registro. Encerrando cliente.")
            sys.exit(1)

        # Iniciar thread para receber mensagens
        thread_recebimento = threading.Thread(target=receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        print(f"Conectado ao servidor. Digite '/sair' para encerrar.")
        
        # Loop principal para enviar mensagens
        while True:
            mensagem = input("Digite sua mensagem (/sair para sair): ")
            
            if mensagem.lower() == '/sair':
                # Enviar comando de saída e encerrar cliente
                cliente.sendto("/sair".encode('utf-8'), (SERVIDOR_HOST, SERVIDOR_PORT))
                break
            
            # Enviar mensagem para o servidor
            try:
                cliente.sendto(mensagem.encode('utf-8'), (SERVIDOR_HOST, SERVIDOR_PORT))
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                break

    except KeyboardInterrupt:
        print("\nCliente encerrado pelo usuário.")
    finally:
        cliente.close()
        print("Socket do cliente fechado.")

if __name__ == "__main__":
    main()