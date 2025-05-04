import socket
import os
import sys
import time
# Configurações do cliente
SERVIDOR_HOST = 'localhost'
SERVIDOR_PORT = 9700
BUFFER_SIZE = 4096
# Função para enviar arquivo
def enviar_arquivo(caminho_arquivo, conn):
    try:
        # Obter tamanho do arquivo
        tamanho_arquivo = os.path.getsize(caminho_arquivo)
        # Enviar nome do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        conn.send(nome_arquivo.encode('utf-8'))
        # Esperar confirmação do servidor
        confirmacao = conn.recv(BUFFER_SIZE).decode('utf-8')
        if confirmacao != "PRONTO":
            print(f"Erro: Resposta inesperada do servidor: {confirmacao}")
            return False
        # Enviar o arquivo
        with open(caminho_arquivo, 'rb') as f:
            bytes_enviados = 0
            inicio = time.time()
            # Ler e enviar o arquivo em blocos
            dados = f.read(BUFFER_SIZE)
            while dados:
                conn.send(dados)
                bytes_enviados += len(dados)
                # Exibir progresso
                progresso = bytes_enviados / tamanho_arquivo * 100
                print(f"\rProgresso: {progresso:.1f}% - {bytes_enviados}/{tamanho_arquivo} bytes", end="")
                dados = f.read(BUFFER_SIZE)
            # Sinalizar fim do arquivo
            conn.send(b'FIM')
            fim = time.time()
            # Calcular estatísticas
            tempo_total = fim - inicio
            taxa_transferencia = bytes_enviados / tempo_total / 1024
            # KB/s
            print("\nArquivo enviado com sucesso.")
            print(f"Tamanho: {bytes_enviados} bytes")
            print(f"Tempo: {tempo_total:.2f} segundos")
            print(f"Taxa de transferência: {taxa_transferencia:.2f} KB/s")
            return True
    except Exception as e:
        print(f"Erro ao enviar arquivo: {e}")
        return False
# Função principal
def main():
    if len(sys.argv) != 2:
        print("Uso: python cliente_tcp.py <caminho_do_arquivo>")
        sys.exit(1)
    caminho_arquivo = sys.argv[1]
    # Verificar se o arquivo existe
    if not os.path.isfile(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não existe.")
        sys.exit(1)
    try:
        # Criar socket TCP e conectar ao servidor
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Conectando ao servidor {SERVIDOR_HOST}: {SERVIDOR_PORT}...")
        cliente.connect((SERVIDOR_HOST, SERVIDOR_PORT))
        # Enviar o arquivo
        print(f"Enviando arquivo'{os.path.basename(caminho_arquivo)}'...")
        enviar_arquivo(caminho_arquivo, cliente)
    except ConnectionRefusedError:
        print("Conexão recusada. Verifique se o servidor está em execução.")
    except KeyboardInterrupt:
        print("\nCliente encerrado pelo usuário.")
    finally:
        cliente.close()
        print("Socket do cliente fechado.")
if __name__ == "__main__":
    main()