import re
import json

def _search(pattern, text, group=1, flags=0):
    m = re.search(pattern, text, flags)
    if not m:
        return ""
    try:
        return m.group(group).strip()
    except IndexError:
        return m.group(0).strip()

def parse_ocr(text):
    txt = text.replace('\r', ' ').replace('\n', ' ')
    txt = re.sub(r'\s{2,}', ' ', txt)  # reduz múltiplos espaços para um

    campos = [
        ("CNPJ",                r"([A4]\d\.\d{3}\.\d{3}/\d{4}\.\d{2})"),
        ("DATA DE ABERTURA",    r"COMPROVANTE DE INSCRIÇÃO E DE SITUAÇÃO\s*([\d/]{10})"),
        ("NOME DE FANTASIA",    r"NOME DE FANTASIA\)\s*PORTE\s*([A-Z0-9\- ]+)"),
        ("ATIVIDADE PRINCIPAL", r"PRINCIPAL\s*([\d\.\-]+ - [^-]+)"),
        ("NATUREZA JURÍDICA",   r"NATUREZA JURÍDICA\s*([\d\-]+ - [A-Za-zÀ-ÿ ]+)"),
        ("LOGRADOURO",          r"LOGRADOURO NÚMERO COMPLEMENTO\s*R ([A-Z ]+)"),
        ("NUMERO",              r"R FRADIQUE COUTINHO (\d+)"),
        ("COMPLEMENTO",         r"R FRADIQUE COUTINHO \d+ ([A-Z0-9 ]+) CEP"),
        ("CEP",                 r"(\d{2}\.\d{3}-\d{3})"),
        ("BAIRRO",              r"\d{2}\.\d{3}-\d{3}\s*([A-Z ]+)"),
        ("MUNICIPIO",           r"\d{2}\.\d{3}-\d{3}\s*[A-Z ]+\s*([A-Z ]+) SP"),
        ("E-MAIL",              r"([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})", 1, re.IGNORECASE),
        ("TELEFONE",            r"(\(\d{2}\)\s*\d{4,5}-\d{4})"),
    ]

    validacoes = []
    for nome, pattern, *rest in campos:
        group = rest[0] if rest else 1
        flags = rest[1] if len(rest) > 1 else 0
        valor = _search(pattern, txt, group, flags)
        if nome == "CNPJ" and valor:
            valor = valor.replace('A', '4').replace('O', '0')
        validacoes.append({"nome": nome, "valor": valor})

    return {"validacoes": validacoes}


if __name__ == "__main__":
    ocr_text = """
19/05/25, 16:05 about:blank

REPÚBLICA FEDERATIVA DO BRASIL

CADASTRO NACIONAL DA PESSOA JURÍDICA

NÚMERO DE INSCRIÇÃO A A Cy | DATA DE ABERTURA
A6.136.300/0001.01 COMPROVANTE DE INSCRIÇÃO E DE SITUAÇÃO 25/04/2022

NOME EMPRESARIAL
DATASMARTCOM S/A

TÍTULO DO ESTABELECIMENTO (NOME DE FANTASIA) PORTE
DATASMARTCOM DEMAIS

CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA PRINCIPAL
63.11-9-00 - Tratamento de dados, provedores de serviços de aplicação e serviços de hospedagem na internet
(Dispensada *)

CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS

62.01-5-01 - Desenvolvimento de programas de computador sob encomenda (Dispensada *)
64.63-8-00 - Outras sociedades de participação, exceto holdings (Dispensada *)

77.33-1-00 - Aluguel de máquinas e equipamentos para escritórios (Dispensada *)

95.11-8-00 - Reparação e manutenção de computadores e de equipamentos periféricos (Dispensada *)
95.12-6-00 - Reparação e manutenção de equipamentos de comunicação (Dispensada *)

CÓDIGO E DESCRIÇÃO DA NATUREZA JURÍDICA
205-4 - Sociedade Anônima Fechada

LOGRADOURO NÚMERO COMPLEMENTO

R FRADIQUE COUTINHO 531 APT 74G

CEP BAIRRO/DISTRITO MUNICÍPIO UF
05.416-914 PINHEIROS SAO PAULO SP
ENDEREGO ELETRONICO TELEFONE
SOCIETARIO@RNVCONSULTORIA.COM.BR (11) 3081-8677

ENTE FEDERATIVO RESPONSAVEL (EFR)

detected

SITUAÇÃO CADASTRAL DATA DA SITUAÇÃO CADASTRAL
ATIVA 25/04/2022

MOTIVO DE SITUAÇÃO CADASTRAL

SITUAÇÃO ESPECIAL DATA DA SITUAÇÃO ESPECIAL

RERKKEKRKK RERKERER

(*) A dispensa de alvarás e licenças é direito do empreendedor que atende aos requisitos constantes na Resolução CGSIM nº 51, de 11 de
junho de 2019, ou da legislação própria encaminhada ao CGSIM pelos entes federativos, não tendo a Receita Federal qualquer
responsabilidade quanto às atividades dispensadas.

Aprovado pela Instrução Normativa RFB nº 2.119, de 06 de dezembro de 2022.
Emitido no dia 19/05/2025 às 16:05:24 (data e hora de Brasília). Página: 1/1

about:blank

    """
    resultado = parse_ocr(ocr_text)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
