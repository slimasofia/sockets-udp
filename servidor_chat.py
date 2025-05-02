# Atividade 1: Chat UDP Simples
# Implementação do Servidor

import socket
import threading
import time
import sys

# Configurações do servidor
HOST = '0.0.0.0'    # Aceita conexões de qualquer IP
PORT = 9500         # Porta para o servidor escutar
BUFFER_SIZE = 1024

# Dicionário para armazenar os clientes conectados (endereço: nome)
clientes = {}

# Criar socket UDP
try:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind((HOST, PORT))
    print(f"Servidor iniciado em {HOST}:{PORT}")
except socket.error as e:
    print(f"Erro ao criar socket: {e}")
    sys.exit(1)

# Função para enviar mensagem para todos os clientes
def broadcast(mensagem, endereco_origem=None):
    for endereco in clientes:
        if endereco != endereco_origem:  # não envia para o cliente de origem
            try:
                servidor.sendto(mensagem.encode('utf-8'), endereco)
            except socket.error as e:
                print(f"Erro ao enviar mensagem para {endereco}: {e}")
                # remove o cliente se ocorrer algum erro
                del clientes[endereco]

# Loop principal do servidor
try:
    print("Aguardando mensagens...")
    while True:
        try:
            # Receber mensagem e endereço do cliente
            dados, endereco = servidor.recvfrom(BUFFER_SIZE)
            mensagem = dados.decode('utf-8')

            # Processar a mensagem recebida
            if mensagem.startswith('/registro:'):
                nome = mensagem.split(':')[1].strip()
                clientes[endereco] = nome
                print(f"Novo cliente registrado: {nome} ({endereco})")
                
                # Envia confirmação DIRETA ao cliente que acabou de se registrar
                servidor.sendto(f"REGISTRO_OK:{nome}".encode('utf-8'), endereco)
                
                # Faz broadcast para os outros (opcional)
                broadcast(f"{nome} entrou no chat.", endereco)
                
            elif mensagem.startswith('/sair'):
                # Remover cliente que está saindo
                if endereco in clientes:
                    nome = clientes[endereco]
                    del clientes[endereco]
                    print(f"Cliente saiu: {nome} ({endereco})")
                    broadcast(f"{nome} saiu do chat.", endereco)
                    
            else:
                # Processar mensagem normal e fazer broadcast
                if endereco in clientes:
                    nome = clientes[endereco]
                    mensagem_formatada = f"{nome}: {mensagem}"
                    print(mensagem_formatada)
                    broadcast(mensagem_formatada, endereco)
                else:
                    servidor.sendto("Você precisa se registrar primeiro com /registro:seu_nome".encode('utf-8'), endereco)

        except Exception as e:
            print(f"Erro no processamento da mensagem: {e}")

except KeyboardInterrupt:
    print("\nServidor encerrado pelo usuário.")
finally:
    servidor.close()
    print("Socket do servidor fechado.")