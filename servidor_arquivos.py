# Atividade 2: Sistema de Transferência de Arquivos
# Implementação do Servidor

import socket
import os
import time
import sys
from collections import defaultdict

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 9600
BUFFER_SIZE = 1024
DIRETORIO_ARQUIVOS = './arquivos_recebidos/'
os.makedirs(DIRETORIO_ARQUIVOS, exist_ok=True)

def receber_arquivo(nome_arquivo, endereco_cliente):
    caminho_arquivo = os.path.join(DIRETORIO_ARQUIVOS, nome_arquivo)
    print(f"\nIniciando recebimento do arquivo: {nome_arquivo}")
    
    try:
        with open(caminho_arquivo, 'wb') as arquivo:
            esperado_seq = 0
            bytes_recebidos = 0
            inicio = time.time()
            servidor.settimeout(10.0)  # Timeout maior para transferência
            
            while True:
                try:
                    dados, _ = servidor.recvfrom(BUFFER_SIZE)
                    
                    cabecalho = dados[:4]
                    seq_num = int.from_bytes(cabecalho, byteorder='big')
                    fragmento = dados[4:]
                    
                    if seq_num == esperado_seq:
                        ack = seq_num.to_bytes(4, byteorder='big')
                        servidor.sendto(ack, endereco_cliente)
                        
                        if len(fragmento) == 0:  # Pacote vazio indica fim
                            break
                            
                        arquivo.write(fragmento)
                        bytes_recebidos += len(fragmento)
                        esperado_seq += 1
                        
                        print(f"\rRecebidos: {bytes_recebidos} bytes | Fragmento: {seq_num}", end="")
                    
                    else:
                        ack = (esperado_seq - 1).to_bytes(4, byteorder='big')
                        servidor.sendto(ack, endereco_cliente)
                
                except socket.timeout:
                    print(f"\nTimeout - Transferência concluída ou interrompida")
                    break
                
                except Exception as e:
                    print(f"\nErro no fragmento {seq_num}: {e}")
                    raise

    except Exception as e:
        print(f"\nFalha ao salvar arquivo: {e}")
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        return False
    
    tempo_total = time.time() - inicio
    taxa = bytes_recebidos / tempo_total / 1024 if tempo_total > 0 else 0
    
    print(f"\nArquivo {nome_arquivo} recebido com sucesso!")
    print(f"Tamanho: {bytes_recebidos} bytes")
    print(f"Tempo: {tempo_total:.2f} segundos")
    print(f"Taxa: {taxa:.2f} KB/s")
    return True

# Criar socket UDP
try:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind((HOST, PORT))
    print(f"Servidor de arquivos iniciado em {HOST}:{PORT}")
except socket.error as e:
    print(f"Erro ao criar socket: {e}")
    sys.exit(1)

try:
    print("Aguardando conexões...")
    while True:
        try:
            servidor.settimeout(5.0)  # Timeout para esperar nova conexão
            dados, endereco = servidor.recvfrom(BUFFER_SIZE)
            mensagem = dados.decode('utf-8')
            
            if mensagem.startswith('ENVIAR:'):
                nome_arquivo = mensagem.split(':')[1]
                print(f"\nSolicitação de envio de {nome_arquivo} de {endereco}")
                servidor.sendto("PRONTO".encode('utf-8'), endereco)
                receber_arquivo(nome_arquivo, endereco)
                
        except socket.timeout:
            continue  # Timeout normal ao esperar nova conexão
        except Exception as e:
            print(f"Erro: {e}")
            continue

except KeyboardInterrupt:
    print("\nServidor encerrado pelo usuário.")
finally:
    servidor.close()
    print("Socket do servidor fechado.")