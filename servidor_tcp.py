import socket
import os
import threading
import sys
import time

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 9700
BUFFER_SIZE = 4096
DIRETORIO_ARQUIVOS = './arquivos_tcp_recebidos/'
# Criar diretório para salvar arquivos se não existir
os.makedirs(DIRETORIO_ARQUIVOS, exist_ok=True)
# Função para lidar com a conexão de um cliente
def handle_client(conn, addr):
    print(f"Nova conexão: {addr}")

    try:
        # Receber nome do arquivo
        nome_arquivo = conn.recv(BUFFER_SIZE).decode('utf-8')
        if not nome_arquivo:
            return
        # Caminho completo para salvar
        caminho_arquivo = os.path.join(DIRETORIO_ARQUIVOS, nome_arquivo)
        # Confirmar pronto para receber
        conn.send("PRONTO".encode('utf-8'))
        # Receber e salvar o arquivo
        with open(caminho_arquivo, 'wb') as f:
            bytes_recebidos = 0
            inicio = time.time()
            while True:
                dados = conn.recv(BUFFER_SIZE)
                if not dados or dados == b'FIM':
                    break
                f.write(dados)
                bytes_recebidos += len(dados)
            fim = time.time()
            # Calcular estatísticas
            tempo_total = fim - inicio
            taxa_transferencia = bytes_recebidos / tempo_total / 1024
            # KB/s
            print(f"Arquivo {nome_arquivo} recebido com sucesso.")
            print(f"Tamanho: {bytes_recebidos} bytes")
            print(f"Tempo: {tempo_total:.2f} segundos")
            print(f"Taxa de transferência: {taxa_transferencia:.2f} KB/s")
    except Exception as e:
        print(f"Erro no processamento do cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"Conexão fechada: {addr}")
# Criar socket TCP
try:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    print(f"Servidor TCP iniciado em {HOST}:{PORT}")
except socket.error as e:

    print(f"Erro ao criar socket: {e}")
    sys.exit(1)
# Loop principal do servidor
try:
    print("Aguardando conexões...")
    while True:
        conn, addr = servidor.accept()
        # Iniciar nova thread para lidar com o cliente
        thread_cliente = threading.Thread(target=handle_client, args=
(conn, addr))
        thread_cliente.daemon = True
        thread_cliente.start()
except KeyboardInterrupt:
    print("\nServidor encerrado pelo usuário.")
finally:
    servidor.close()
    print("Socket do servidor fechado.")