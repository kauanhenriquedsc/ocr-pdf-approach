import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import re
import shutil
 
 
# Indique o caminho do executável do Tesseract no Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
 
# Configurações
pdf_path = r'C:\Users\Paulo Santos\Desktop\DEV\python_ocr\input\cnpj_01.pdf'
output_folder = 'tmp_imgs'
os.makedirs(output_folder, exist_ok=True)
 
# 1. Converte cada página do PDF em imagem
images = convert_from_path(pdf_path, dpi=300, output_folder=output_folder, fmt='png')
 
all_text = ""
for i, image in enumerate(images):
    # Salva imagem (opcional, para ver depois)
    img_path = os.path.join(output_folder, f'page_{i+1}.png')
    image.save(img_path, 'PNG')
    # 2. OCR com Tesseract
    text = pytesseract.image_to_string(image, lang='por')
    all_text += text + "\n"
 
# --------- EXTRAÇÃO GENÉRICA DOS CAMPOS PRINCIPAIS ---------
def search_first(pattern, text, flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    if not match:
        return ""
    if match.lastindex:
        return next((g.strip() for g in match.groups() if g and g.strip()), "")
    return match.group(0).strip()
 
dados = {}
 
# CNPJ - aceita ponto ou vírgula (erro comum de OCR)
dados['CNPJ'] = search_first(r'(\d{2}[.,]\d{3}[.,]\d{3}/\d{4}[.-]\d{2})', all_text)
if dados['CNPJ']:
    # Corrige vírgula para ponto no CNPJ, se existir
    dados['CNPJ'] = dados['CNPJ'].replace(',', '.')
 
# Nome Empresarial
dados['Nome Empresarial'] = search_first(
    r'NOME EMPRESARIAL\s*\n?([A-Z0-9 \.\-&]+)', all_text)
 
# Nome Fantasia (raro em MEI/empresário individual)
dados['Nome Fantasia'] = search_first(
    r'NOME DE FANTASIA\s*([A-Z0-9 \.\-&]+)|T[ÍI]TULO DO ESTABELECIMENTO\s*\n?([A-Z0-9 \.\-&]+)', all_text)
 
# Natureza Jurídica
dados['Natureza Jurídica'] = search_first(
    r'NATUREZA JUR[IÍ]DICA\s*\n?([\w\s\-\(\)]+)', all_text)
 
# Telefone - tolera diferentes formatos e espaços
dados['Telefone'] = search_first(
    r'(\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4})', all_text)
 
# Email - tolera ausência de arroba por OCR (ex: GOGMAIL.COM)
dados['Email'] = search_first(
    r'([A-Z0-9\.\-_]+@[A-Z0-9\.\-]+)', all_text, flags=re.IGNORECASE)
if not dados['Email']:
    # Tenta corrigir se veio GOGMAIL.COM, substituindo "GOGMAIL" por "@GMAIL"
    dados['Email'] = search_first(r'([A-Z0-9\.\-_]+GOGMAIL\.COM)', all_text, flags=re.IGNORECASE)
    if dados['Email']:
        dados['Email'] = re.sub(r'GOGMAIL', '@gmail', dados['Email'], flags=re.IGNORECASE)
 
# CEP
dados['CEP'] = search_first(
    r'(\d{2}\.\d{3}-\d{3}|\d{5}-\d{3})', all_text)
 
# Logradouro, Número, Complemento
logradouro_match = re.search(
    r'LOGRADOURO N[ÚU]MERO COMPLEMENTO\s*\n?([A-Z ]+)\s+(\d+)\s*([A-Z0-9 ]*)', all_text)
if logradouro_match:
    dados['Logradouro'] = logradouro_match.group(1).strip()
    dados['Número'] = logradouro_match.group(2).strip()
    dados['Complemento'] = logradouro_match.group(3).strip()
else:
    # fallback: só logradouro e número
    dados['Logradouro'] = search_first(r'LOGRADOURO\s*\n?([A-Z0-9 \.\-]+)', all_text)
    dados['Número'] = search_first(r'N[ÚU]MERO\s*\n?([0-9]+)', all_text)
    dados['Complemento'] = search_first(r'COMPLEMENTO\s*\n?([A-Z0-9 \.\-]*)', all_text)
 
# Bairro/Distrito, Município, UF
# Pega linha depois do CEP, separando corretamente
endereco_match = re.search(
    r'(?:CEP.*\n)?(?:\d{2}\.\d{3}-\d{3}|\d{5}-\d{3})\s+([A-Z0-9 \-\/]+)\s+([A-Z ]+)\s+([A-Z]{2})', all_text)
if endereco_match:
    dados['Bairro/Distrito'] = endereco_match.group(1).strip()
    dados['Município'] = endereco_match.group(2).strip()
    dados['UF'] = endereco_match.group(3).strip()
else:
    # fallback para separar colunas da linha "CEP BAIRRO/DISTRITO MUNICÍPIO UF"
    linhas = all_text.splitlines()
    for i, linha in enumerate(linhas):
        if re.search(r'\d{2}\.\d{3}-\d{3}|\d{5}-\d{3}', linha):
            partes = linha.split()
            if len(partes) >= 4:
                dados['CEP'] = partes[0]
                dados['Bairro/Distrito'] = partes[1]
                dados['Município'] = partes[2]
                dados['UF'] = partes[3]
            break
 
# Limpeza final para evitar pegar "MUNIC" e "UF" por erro de OCR
if dados.get('Bairro/Distrito', '').upper() == 'MUNIC':
    dados['Bairro/Distrito'] = ''
if dados.get('Município', '').upper() == 'UF':
    dados['Município'] = ''
if dados.get('UF', '') and len(dados['UF']) > 2:
    dados['UF'] = ''
 
# Mostra resultado final
print("\nDADOS EXTRAÍDOS:")
for campo, valor in dados.items():
    print(f"{campo}: {valor}")
 
# 4. (Opcional) Apagar imagens temporárias
shutil.rmtree(output_folder)
 
print("Dados brutos: ", dados)
 
print("Texto bruto: ", all_text)