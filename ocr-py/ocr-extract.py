import ocrmypdf
import sys
import os

def ocr_pdf(input_pdf, output_pdf, txt_output=None, lang="por+eng"):
    """
    Aplica OCR em um PDF-imagem, salvando um PDF pesquisável e (opcionalmente) um TXT extraído.
    """
    kwargs = {
        "language": lang,
        "deskew": True,         
        "force_ocr": True,      
        "skip_text": False,     
        "rotate_pages": True,   
        "tesseract_timeout": 180,  
        # "optimize": 1,         
    }
    if txt_output:
        kwargs["sidecar"] = txt_output

    try:
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            **kwargs
        )
    except Exception as e:
        print(f"Erro durante o OCR: {e}")
        sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python ocr_process.py input.pdf output.pdf [texto_extraido.txt]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    txt_output = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.isfile(input_pdf):
        print(f"Arquivo de entrada não encontrado: {input_pdf}")
        sys.exit(1)

    ocr_pdf(input_pdf, output_pdf, txt_output)
    print(f"PDF processado e salvo em: {output_pdf}")
    if txt_output:
        print(f"Texto extraído salvo em: {txt_output}")
