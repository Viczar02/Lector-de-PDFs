import os
import fitz  # PyMuPDF
import re
import csv

def extract_text_from_pdf(pdf_path):
    """Extrae el texto completo de un archivo PDF."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_lesiones_tabla(texto):
    fallecidos = 0
    sobrevivientes = 0

    lines = texto.splitlines()
    buffer = []

    # Buscar la sección de lesiones personales
    lines = texto.splitlines()
    buffer = []

    # Guardar índices donde aparece la sección de lesiones personales
    posibles_indices = []
    for i, line in enumerate(lines):
        line_lower = line.lower()

        if re.search(r'lesiones\s+(personales|a\s+personas)', line_lower) or re.match(r'1\.2\s+lesiones\s+personales', line_lower):
            posibles_indices.append(i)

        # También contempla el caso dividido en dos líneas
        if "lesiones" in line_lower and i + 1 < len(lines):
            next_line_lower = lines[i + 1].lower()
            if "personales" in next_line_lower or "a personas" in next_line_lower:
                posibles_indices.append(i)

    # Usar la última ocurrencia válida
    if posibles_indices:
        ultima = posibles_indices[-1]
        buffer = lines[ultima:ultima + 60]


    # Procesar líneas del buffer
    for i, line in enumerate(buffer):
        clean = line.strip().lower()

        # Fallecidos: buscar números en las 4 líneas siguientes a "mortales"
        if clean.startswith("mortales"):
            for j in range(3, 5):
                if i + j < len(buffer):
                    siguiente_linea = buffer[i + j]
                    if "total" not in siguiente_linea.lower():
                        numeros = [int(n) for n in re.findall(r'\b\d+\b', siguiente_linea)]
                        fallecidos += sum(numeros)

        # Sobrevivientes: buscar desde la línea actual y las 4 siguientes
        elif any(clean.startswith(k) for k in ["graves", "leves", "ilesos"]):
            for j in range(3, 5):
                if i + j < len(buffer):
                    siguiente_linea = buffer[i + j]
                    if "total" not in siguiente_linea.lower():
                        numeros = [int(n) for n in re.findall(r'\b\d+\b', siguiente_linea)]
                        sobrevivientes += sum(numeros)

    return str(fallecidos), str(sobrevivientes)


def extract_info(text):
    """Extrae datos clave del informe."""
    operador = re.search(r'Explotador:\s+(.*)', text)
    tipo_aeronave = re.search(r'Aeronave:\s+(.*)', text)
    certificado = re.search(r'Certificado\s+aeronavegabilidad:\s*(?:No\.\s*)?([A-Za-z]?\d+)', text, re.IGNORECASE)

    fallecidos, sobrevivientes = extract_lesiones_tabla(text)

    return {
        "Operador": operador.group(1).strip() if operador else "No encontrado",
        "Tipo de Aeronave": tipo_aeronave.group(1).strip() if tipo_aeronave else "No encontrado",
        "Certificado Aeronavegabilidad": certificado.group(1).strip() if certificado else "No encontrado",
        "Fallecidos": fallecidos,
        "Sobrevivientes": sobrevivientes
    }

def process_folder(folder_path, output_csv="accidentes.csv"):
    """Procesa todos los PDF en una carpeta, guarda los resultados en CSV y los muestra en consola."""
    data = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)

            info = extract_info(text)
            info["Archivo"] = filename
            data.append(info)

            # Imprimir resultado en consola
            print(f"{filename}")
            print(f"Operador: {info['Operador']}")
            print(f"Tipo de Aeronave: {info['Tipo de Aeronave']}")
            print(f"Certificado aeronavegabilidad: {info['Certificado Aeronavegabilidad']}")
            print(f"Fallecidos: {info['Fallecidos']}")
            print(f"Sobrevivientes: {info['Sobrevivientes']}")
            print("-" * 50)

    # Guardar resultados en CSV
    if data:
        keys = ["Archivo", "Operador", "Tipo de Aeronave", "Certificado Aeronavegabilidad", "Fallecidos", "Sobrevivientes"]
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

    print(f"\n{len(data)} archivos procesados.")
    print(f"Resultados guardados en '{output_csv}'")
    print(f"Archivos .txt generados con el texto de cada PDF.\n")


if __name__ == "__main__":
    folder_path = "pdfs"  # Cambia esta ruta si los PDFs están en otra carpeta
    process_folder(folder_path)