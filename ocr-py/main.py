import os
import subprocess
import ocrmypdf
 
# 📂 Pastas
input_folder = "input"
output_pdf_folder = "output_pdf"
 
# 📁 Cria as pastas de saída se não existirem
os.makedirs(output_pdf_folder, exist_ok=True)
 
# 🔥 Processa cada PDF na pasta de entrada
for filename in os.listdir(input_folder):
    if filename.endswith(".pdf"):
        input_path = os.path.join(input_folder, filename)
       
        # Saídas
        output_pdf = os.path.join(output_pdf_folder, filename)
       
        print(f"\n🔵 Processando {filename}...")
 
        try:
            # ✅ OCR para gerar PDF pesquisável
            print("🟢 Fazendo OCR e gerando PDF pesquisável...")
            ocrmypdf.ocr(
                input_path,
                output_pdf,
                force_ocr=True,
                lang="por"
            )
            print(f"✅ PDF OCR salvo em {output_pdf}")
         
 
        except Exception as e:
            print(f"❌ Erro processando {filename}: {e}")
 
print("\n🏁 Processamento concluído!")