from pathlib import Path
import openpyxl
import os

pastascript = os.path.dirname(os.path.abspath(__file__))
 
nome_arquivo = input("Digite o caminho do arquivo .txt: ")
caminho_arquivo = os.path.join(pastascript, nome_arquivo)
    

nome_base_arquivo = Path(nome_arquivo).stem
planilha = f"{nome_base_arquivo}.xlsx"
caminho_planilha = os.path.join(pastascript, planilha)

workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Relatório de Vendas"

try:
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        if not linhas:
            raise ValueError("O arquivo de dados está vazio.")

        primeira_linha = linhas[0].strip()
        cabecalhos = [campo.split(':')[0] for campo in primeira_linha.split('|')]
        sheet.append(cabecalhos)
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            valores = [campo.split(':')[1] for campo in linha.split('|')]
            sheet.append(valores)

    workbook.save(caminho_planilha)
    print(f"Planilha '{planilha}' gerada com sucesso em: {caminho_planilha}")

except FileNotFoundError:
    print(f"Erro: O arquivo de dados '{nome_arquivo}' não foi encontrado.")