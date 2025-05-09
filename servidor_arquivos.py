import socket
import os
import time
import sys

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 9600
BUFFER_SIZE = 1024
DIRETORIO_ARQUIVOS = './arquivos_recebidos/'

# Criar diretório para salvar arquivos se não existir
os.makedirs(DIRETORIO_ARQUIVOS, exist_ok=True)

# Função para receber arquivo
def receber_arquivo(nome_arquivo, endereco_cliente):
    caminho_arquivo = os.path.join(DIRETORIO_ARQUIVOS, nome_arquivo)
    print(f"\nIniciando recebimento de {nome_arquivo}")
    inicio = time.time()

    try:
        with open(caminho_arquivo, 'wb') as arquivo:
            esperado_seq = 0        # pra contorle de ordem
            bytes_recebidos = 0
            #servidor.settimeout(10.0)

            while True:
                try:
                    # receber dados do cliente
                    dados, _ = servidor.recvfrom(BUFFER_SIZE)
                    # separa cabeçalho e fragmento
                    cabecalho = dados[:4]
                    seq_num = int.from_bytes(cabecalho, byteorder='big')
                    fragmento = dados[4:]

                    if seq_num == 0xFFFFFFFF:
                        # se for o pacote final envia confirmação e encerra
                        ack = (0xFFFFFFFF).to_bytes(4, byteorder='big')
                        servidor.sendto(ack, endereco_cliente)
                        print("\nPacote final recebido. Encerrando.")
                        break

                    if seq_num == esperado_seq:
                        # s eo número de sequência está correto, escreve no arquivo
                        arquivo.write(fragmento)
                        bytes_recebidos += len(fragmento)

                        # envia ack com o número de sequência atual 
                        ack = seq_num.to_bytes(4, byteorder='big')
                        servidor.sendto(ack, endereco_cliente)
                        
                        # atualiza o próximo número de sequência esperado
                        esperado_seq += 1
                        print(f"\rRecebidos: {bytes_recebidos} bytes | Fragmento: {seq_num}", end="")
                    else:
                        # se o fragmento está fora d eordem, reenvia ack anterior
                        ack = (esperado_seq - 1).to_bytes(4, byteorder='big')
                        servidor.sendto(ack, endereco_cliente)

                except socket.timeout:
                    print("\nTimeout - Encerrando (sem pacote final)")
                    break

    except Exception as e:
        print(f"\nErro ao salvar arquivo: {e}")
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        return False

    tempo_total = time.time() - inicio
    taxa = bytes_recebidos / tempo_total / 1024 if tempo_total > 0 else 0
    print(f"\nArquivo '{nome_arquivo}' recebido.")
    print(f"Tamanho: {bytes_recebidos} bytes")
    print(f"Tempo: {tempo_total:.2f} s")
    print(f"Taxa: {taxa:.2f} KB/s")
    return True

# Criar socket
try:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind((HOST, PORT))
    print(f"Servidor UDP iniciado em {HOST}:{PORT}")
except socket.error as e:
    print(f"Erro ao criar socket: {e}")
    sys.exit(1)

try:
    print("Aguardando solicitações...")
    while True:
        try:
            # Receber solicitação inicial
            dados, endereco = servidor.recvfrom(BUFFER_SIZE)
            mensagem = dados.decode('utf-8')

            # Se for uma solicitação de envio de arquivo
            if mensagem.startswith("ENVIAR:"):
                nome_arquivo = mensagem.split(":")[1]
                print(f"\nSolicitação de envio de {nome_arquivo} de {endereco}")

                # Enviar confirmação de pronto para receber
                servidor.sendto("PRONTO".encode('utf-8'), endereco)
                receber_arquivo(nome_arquivo, endereco)
        except Exception as e:
            print(f"Erro: {e}")
except KeyboardInterrupt:
    print("\nEncerrando servidor.")
finally:
    servidor.close()
    print("Socket fechado.")