import subprocess
import os
import requests
import shutil
import winshell
from win32com.client import Dispatch

# URL do script atualizado no GitHub (link "Raw")
URL_ATUALIZACAO = "https://raw.githubusercontent.com/guutoth/ProjetosInvestimentos/main/RetornosStocks"

# Nome do arquivo Python original e do executável
NOME_PROGRAMA = "Calculo de Retornos"
NOME_ARQUIVO = f"{NOME_PROGRAMA}.py"
NOME_EXECUTAVEL = f"{NOME_PROGRAMA}.exe"
PASTA_ALVO = f"C:\\{NOME_PROGRAMA}"
NOME_SPEC = f"{NOME_ARQUIVO}.spec"

def preparar_ambiente():
    os.makedirs(PASTA_ALVO, exist_ok=True)

def baixar_atualizacao():
    try:
        print("Baixando atualização...")
        response = requests.get(URL_ATUALIZACAO, stream=True)
        response.raise_for_status()

        caminho_script = os.path.join(PASTA_ALVO, NOME_ARQUIVO)

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        downloaded = 0

        with open(caminho_script, 'wb') as f:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                print(f"Download: {int((downloaded / total_size) * 100)}% concluído", end='\r')

        print(f"Atualização baixada com sucesso e salva em {caminho_script}.")
    except Exception as e:
        print(f"Erro ao baixar atualização: {e}")

def gerar_executavel():
    try:
        print("Gerando o executável...")
        subprocess.run(["pyinstaller", "--onefile", NOME_ARQUIVO], cwd=PASTA_ALVO, check=True)

        caminho_dist = os.path.join(PASTA_ALVO, "dist", NOME_EXECUTAVEL)
        caminho_destino = os.path.join(PASTA_ALVO, NOME_EXECUTAVEL)
        shutil.move(caminho_dist, caminho_destino)

        shutil.rmtree(os.path.join(PASTA_ALVO, "build"), ignore_errors=True)
        shutil.rmtree(os.path.join(PASTA_ALVO, "dist"), ignore_errors=True)

        pycache_dir = os.path.join(PASTA_ALVO, '__pycache__')
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir, ignore_errors=True)

        print(f"Executável gerado e movido para {caminho_destino}.")
    except Exception as e:
        print(f"Erro ao gerar o executável: {e}")

def criar_atalho():
    try:
        print("Criando atalho na área de trabalho...")
        desktop = winshell.desktop()
        caminho_atualizador = os.path.join(PASTA_ALVO, NOME_EXECUTAVEL)
        atalho = os.path.join(desktop, f"{NOME_EXECUTAVEL}.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(atalho)
        shortcut.TargetPath = caminho_atualizador
        shortcut.WorkingDirectory = PASTA_ALVO
        shortcut.save()

        print(f"Atalho criado na área de trabalho: {atalho}.")
    except Exception as e:
        print(f"Erro ao criar atalho: {e}")

def remover_arquivos_temp():
    try:
        arquivos_para_remover = [NOME_ARQUIVO, NOME_SPEC]
        for arquivo in arquivos_para_remover:
            caminho_arquivo = os.path.join(PASTA_ALVO, arquivo)
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
                print(f"Arquivo {caminho_arquivo} removido com sucesso.")
            else:
                print(f"Arquivo {caminho_arquivo} não encontrado.")
    except Exception as e:
        print(f"Erro ao remover arquivos temporários: {e}")

if __name__ == "__main__":
    preparar_ambiente()        # Garantir que a pasta e o arquivo existam
    baixar_atualizacao()       # Baixar o script atualizado
    gerar_executavel()         # Gerar o novo executável
    criar_atalho()             # Criar atalho na área de trabalho
    remover_arquivos_temp()    # Remover arquivos temporários
