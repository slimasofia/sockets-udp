import socket
import os
import sys
import time

# Configurações do cliente
SERVIDOR_HOST = 'localhost'
SERVIDOR_PORT = 9600
BUFFER_SIZE = 1024
TAMANHO_FRAGMENTO = 1000    # Tamanho de cada fragmento a ser enviado
TIMEOUT = 1.0               # Timeout para retransmissão em segundos
MAX_TENTATIVAS = 5          # Número máximo de tentativas de retransmissão

try:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.settimeout(TIMEOUT)
except socket.error as e:
    print(f"Erro ao criar socket: {e}")
    sys.exit(1)

# Função para enviar arquivo
def enviar_arquivo(caminho_arquivo):
    nome_arquivo = os.path.basename(caminho_arquivo)
    tamanho_arquivo = os.path.getsize(caminho_arquivo)
    seq_num = 0     # (número de sequência do fragmento)
    bytes_enviados = 0

    print(f"\nIniciando envio de '{nome_arquivo}' ({tamanho_arquivo} bytes)...")

    try:
        with open(caminho_arquivo, 'rb') as arquivo:
            inicio = time.time()

            while True:
                fragmento = arquivo.read(TAMANHO_FRAGMENTO)
                if not fragmento:
                    # Se não há mais dados, envia um pacote especial de término
                    fim_seq = (0xFFFFFFFF).to_bytes(4, byteorder='big')
                    cliente.sendto(fim_seq, (SERVIDOR_HOST, SERVIDOR_PORT))
                    try:
                        # aguarda a confirmação do servidor referente ao término
                        ack_data, _ = cliente.recvfrom(BUFFER_SIZE)
                        # verifica se o ACK recebido também contém o código de término
                        if int.from_bytes(ack_data[:4], byteorder='big') == 0xFFFFFFFF:
                            print("\nConfirmação de término recebida.")
                    except socket.timeout:
                        print("\nTimeout aguardando ACK final.")
                    break
                
                # cria o cabeçalho com o número de sequência (4 bytes)
                cabecalho = seq_num.to_bytes(4, byteorder='big')
                pacote = cabecalho + fragmento
                ack_recebido = False
                tentativas = 0

                # reenvia o fragmento até receber o ACK ou atingir o limite de tentativas
                while not ack_recebido and tentativas < MAX_TENTATIVAS:
                    cliente.sendto(pacote, (SERVIDOR_HOST, SERVIDOR_PORT))
                    print(f"\rEnviados: {bytes_enviados}/{tamanho_arquivo} bytes | Fragmento: {seq_num}", end="")

                    try:
                        ack_data, _ = cliente.recvfrom(BUFFER_SIZE)
                        # verifica se o ACK é do fragmento atual
                        if int.from_bytes(ack_data[:4], byteorder='big') == seq_num:
                            ack_recebido = True
                            bytes_enviados += len(fragmento)
                    except socket.timeout:
                        tentativas += 1

                if not ack_recebido:
                    raise Exception(f"Falha no fragmento {seq_num} após {MAX_TENTATIVAS} tentativas")

                seq_num += 1

            tempo_total = time.time() - inicio
            taxa = bytes_enviados / tempo_total / 1024

            print(f"\n\nTransferência concluída!")
            print(f"Tamanho do arquivo: {tamanho_arquivo} bytes")
            print(f"Tempo total: {tempo_total:.2f} s")
            print(f"Taxa de transferência: {taxa:.2f} KB/s")
            return True

    except Exception as e:
        print(f"\nErro durante a transferência: {e}")
        return False

# Função principal
def main():
    if len(sys.argv) != 2:
        print("Uso: python cliente_arquivos.py <caminho_do_arquivo>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]

    # Verificar se o arquivo existe
    if not os.path.isfile(caminho_arquivo):
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)

    try:
        # Enviar solicitação inicial ao servidor
        nome_arquivo = os.path.basename(caminho_arquivo)
        solicitacao = f"ENVIAR:{nome_arquivo}"
        print(f"Solicitando envio de '{nome_arquivo}'...")
        cliente.sendto(solicitacao.encode('utf-8'), (SERVIDOR_HOST, SERVIDOR_PORT))

        resposta, _ = cliente.recvfrom(BUFFER_SIZE)
        if resposta.decode('utf-8') == "PRONTO":
            print("Servidor pronto. Iniciando transferência...")
            if enviar_arquivo(caminho_arquivo):
                print("Arquivo enviado com sucesso!")
            else:
                print("Falha no envio.")
        else:
            print(f"Resposta inesperada: {resposta.decode('utf-8')}")

    except socket.timeout:
        print("Timeout: Servidor não respondeu.")
    except KeyboardInterrupt:
        print("\nEnvio cancelado.")
    finally:
        cliente.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    main()