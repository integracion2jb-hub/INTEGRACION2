import yagmail
from enum import Enum
from datetime import datetime


servicio_yag = yagmail.SMTP("integracion2jb@gmail.com","zxyj wivq bchn mbgt")

class SUBJECTS (str, Enum):
    LOGS = "Informe de análisis de logs - Sistema Automatizado"
    ALERTA_REAL = "Alerta critica detectada - Sistema Automatizado "

def contenido_enviar (subject: SUBJECTS , resultados):
    if subject not in [e.value for e in SUBJECTS]:
        return False
    
    if subject.value == SUBJECTS.ALERTA_REAL.value:
        return f"""
        <h2> ALERTA DETECTADA ACCION INMEDIATA</h2>
        <p><b>Fecha:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        {resultados}
        <p> Esta es una alerta critica detectada, realizar acciones inmediatamente</p>
        """
    return f"""
    <h2> Tips generados del sistema empresa JB</h2>
    <div style='max-width:600px;'>"
    {
        "<hr>".join([r["resultado"] for r in resultados]) 
    }

    </div>
    
    <p> Los Tips e informacion generados por el sistema deben ser revisados por el encargado para aplicar medidas correspondientes.</p>
    """

def enviarMail(email: str, resultados, subject: SUBJECTS ):
    if len(email) < 9 or not email.endswith("@gmail.com"):
        return "Error!, correo no enviado por errores de formato"
    
    if contenido_enviar(subject, resultados):
        servicio_yag.send(
        to = email,
        subject = subject,
        contents = contenido_enviar(subject, resultados)
        ) 
        print(f"Email enviado hacia el correo: {email}")

    return "Error correo no enviado"

