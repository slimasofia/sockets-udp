# Atividade 2: Sistema de Transferência de Arquivos
# Implementação do Cliente

import socket
import os
import sys
import time
from collections import defaultdict

# Configurações do cliente
SERVIDOR_HOST = 'localhost'
SERVIDOR_PORT = 9600
BUFFER_SIZE = 1024
TAMANHO_FRAGMENTO = 1000  # Tamanho de cada fragmento a ser enviado
TIMEOUT = 1.0             # Timeout para retransmissão em segundos
MAX_TENTATIVAS = 5        # Número máximo de tentativas de retransmissão

# Criar socket UDP
try:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.settimeout(TIMEOUT)
except socket.error as e:
    print(f"Erro ao criar socket: {e}")
    sys.exit(1)

def enviar_arquivo(caminho_arquivo):
    nome_arquivo = os.path.basename(caminho_arquivo)
    tamanho_arquivo = os.path.getsize(caminho_arquivo)
    seq_num = 0
    bytes_enviados = 0

    print(f"\nIniciando envio de '{nome_arquivo}' ({tamanho_arquivo} bytes)...")

    try:
        with open(caminho_arquivo, 'rb') as arquivo:
            inicio = time.time()
            
            while True:
                # Ler e enviar um fragmento por vez
                fragmento = arquivo.read(TAMANHO_FRAGMENTO)
                if not fragmento:
                    cabecalho = seq_num.to_bytes(4, byteorder='big')
                    cliente.sendto(cabecalho + b'', (SERVIDOR_HOST, SERVIDOR_PORT))
                    break 
                
                cabecalho = seq_num.to_bytes(4, byteorder='big')
                pacote = cabecalho + fragmento
                bytes_enviados += len(fragmento)
                ack_recebido = False
                tentativas = 0
                
                while not ack_recebido and tentativas < MAX_TENTATIVAS:
                    cliente.sendto(pacote, (SERVIDOR_HOST, SERVIDOR_PORT))
                    print(f"\rEnviados: {bytes_enviados}/{tamanho_arquivo} bytes | Fragmento: {seq_num}", end="")
                    
                    try:
                        ack_data, _ = cliente.recvfrom(BUFFER_SIZE)
                        if int.from_bytes(ack_data[:4], byteorder='big') == seq_num:
                            ack_recebido = True
                    except socket.timeout:
                        tentativas += 1
                
                if not ack_recebido:
                    raise Exception(f"Falha no fragmento {seq_num} após {MAX_TENTATIVAS} tentativas")
                
                seq_num += 1
               
            tempo_total = time.time() - inicio
            taxa = tamanho_arquivo / tempo_total / 1024 if tempo_total > 0 else 0

            print(f"\n\nTransferência concluída com sucesso!")
            print(f"Tamanho do arquivo: {tamanho_arquivo} bytes")
            print(f"Tempo total: {tempo_total:.2f} segundos")
            print(f"Taxa de transferência: {taxa:.2f} KB/s")
            return True

    except Exception as e:
        print(f"\nErro durante a transferência: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python cliente_arquivos.py <caminho_do_arquivo>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]

    if not os.path.isfile(caminho_arquivo):
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)

    try:
        # Enviar solicitação inicial
        nome_arquivo = os.path.basename(caminho_arquivo)
        solicitacao = f"ENVIAR:{nome_arquivo}"
        print(f"Solicitando envio de '{nome_arquivo}'...")
        cliente.sendto(solicitacao.encode('utf-8'), (SERVIDOR_HOST, SERVIDOR_PORT))

        # Esperar confirmação do servidor
        resposta, _ = cliente.recvfrom(BUFFER_SIZE)
        if resposta.decode('utf-8') == "PRONTO":
            print("Servidor pronto. Iniciando transferência...")
            if enviar_arquivo(caminho_arquivo):
                print("Arquivo enviado com sucesso!")
            else:
                print("Falha no envio do arquivo.")
        else:
            print(f"Resposta inesperada do servidor: {resposta.decode('utf-8')}")

    except socket.timeout:
        print("Timeout: Servidor não respondeu à solicitação inicial.")
    except KeyboardInterrupt:
        print("\nEnvio cancelado pelo usuário.")
    finally:
        cliente.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    main()