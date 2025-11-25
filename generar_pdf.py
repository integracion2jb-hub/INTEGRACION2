from datetime import datetime
from fpdf import FPDF
from basedatos import datos_pdf

class PDF(FPDF):
    pass

pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

def generar_pdf_desde_db():
    registros = datos_pdf()
    dia = datetime.now().strftime("%Y-%m-%d")
    


    for fecha, dispositivo, ip, html in registros:
        
        pdf.write_html(f"<h3>{dispositivo} ({ip}) - {fecha}</h3>{html}<hr>")


    pdf.output(f"informe_logs-{dia}.pdf")
    print("Informe PDF generado correctamente.")




generar_pdf_desde_db()