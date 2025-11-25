from openai import OpenAI
import os
from enviarEmail import enviarMail, SUBJECTS
from datetime import datetime
from basedatos import  incializar_db, guardar_resultados, eliminar_datos_fecha_superior

API_KEY = "aqui va la api key"


client = OpenAI(api_key=API_KEY)

# RUTA DE LOS LOGS (en server central)
LOGS_DIR = "/var/log/central-logs/"


# ELIMINAR REGISTROS QUE SOBREPASEN LOS 3 MESES (COMO REQUERIMIENTO DE GUARDADO HISTORICO)
eliminar_datos_fecha_superior()


# Inicializar Base de datos local + creacion de tabla

incializar_db()


## Detectar sede por ip.

def detectar_sede (ip:str):
    if ip.startswith("192.10.10"):
        return "SEDE A"
    elif ip.startswith("192.30.30"):
        return "SEDE A"
    elif ip.startswith("192.66.66"):
        return "SEDE A"
    elif ip.startswith("192.20.20"):
        return  "SEDE B"
    elif ip.startswith("192.40.40"):
        return  "SEDE B"
    elif ip.startswith("192.99.99"):
        return  "SEDE B"
    else :
        return "SEDE DESCONOCIDA -- IP externa"



def leer_logs():
    dispositivos = []
    for archivo in os.listdir(LOGS_DIR):
        if archivo.endswith(".log"):
            ruta = os.path.join(LOGS_DIR, archivo)
            nombre, _ = os.path.splitext(archivo)
            tipo, ip = nombre.split("-", 1)
            with open(ruta, "r") as f:
                contenido = f.read().strip()
            dispositivos.append({"tipo": tipo, "ip": ip, "logs": contenido})
    return dispositivos



# GENERACION DE PROMPT

def generar_prompt(dispositivo):
    return f"""
    Eres un asistente experto en ciberseguridad y análisis de logs de red.
    Analiza los siguientes registros y genera un resumen técnico y educativo.

    Contexto:
    - Los resultados serán enviados por correo electrónico, por lo que DEBES usar formato HTML, no Markdown.
    - Usa etiquetas HTML simples: <b>, <p>, <ul>, <li>.
    - No incluyas caracteres de formato como * o **.
    - EL entorno es educativo por lo que los logs enviados pueden no representar amenazas.
    - Aplica estilo CSS inline para mantener el formato compacto, limpio y profesional.
    - Responde con información útil y recomendaciones incluso ante eventos leves.
    - Informacion sobre a que sede pertenecen las IPs que seran enviadas.
        1) 192.10.10.0/24 -- SEDE A
        2) 192.30.30.0/29 -- SEDE A
        3) 192.66.66.0/29 -- SEDE A
        4) 192.20.20.0/24 -- SEDE B
        5) 192.40.40.0/29 -- SEDE B
        6) 192.99.99.0/29 -- SEDE B


    Datos de entrada:

    Sede: Desconocida (basada en IP)
    Dispositivo: {dispositivo['tipo']} ({dispositivo['ip']})

    Logs recientes:
    {dispositivo['logs'][:2000]}  

    Requerimientos de salida:
    1. Entrega la respuesta en HTML, dentro de un contenedor principal con estilo compacto.
    2. Aplica estilos inline (no <style> global) para evitar márgenes grandes.
    3. Usa esta estructura y estilo como referencia:

    <div style="font-family: Arial, sans-serif; font-size: 13px; color: #222; line-height: 1.3; margin: 5px 0;">
    <p style="margin: 4px 0;"><b>Dispositivo:</b> {dispositivo['tipo']} ({dispositivo['ip']})</p>
    <p style="margin: 4px 0;"><b>Resumen:</b> [Texto breve]</p>

    <p style="margin: 4px 0;"><b>Posibles causas o eventos destacados:</b></p>
    <ul style="margin: 2px 0 6px 18px; padding: 0;">
        <li>[Punto 1]</li>
        <li>[Punto 2]</li>
    </ul>

    <p style="margin: 4px 0;"><b>Recomendaciones:</b></p>
    <ul style="margin: 2px 0 6px 18px; padding: 0;">
        <li>[Recomendación 1]</li>
        <li>[Recomendación 2]</li>
        <li>[Recomendación 3]</li>
    </ul>

    <p style="margin: 4px 0;"><b>Nivel de severidad:</b> Bajo / Medio / Alto</p>
    </div>

    4. Mantén la salida legible y compacta (sin espacios vacíos entre secciones).
    5. Si no se detectan eventos importantes, entrega consejos de buenas prácticas de red o seguridad.
    """



# LEER CADA LOG Y ENVIARLOS A LA API DE CHATGPT
def analizar_logs():
    resultados = []
    dispositivos = leer_logs()
    for d in dispositivos:
        prompt = generar_prompt(d)
        print(f"Analizando {d['tipo']} - {d['ip']}...")

        respuesta = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "Eres un analista de seguridad experto."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        salida = respuesta.choices[0].message.content
        resultados.append({
            "dispositivo": d["tipo"],
            "ip": d["ip"],
            "resultado": salida
        })
        for result in resultados:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sede = detectar_sede(result["ip"])
            ip = result["ip"]
            dispositivo = result["dispositivo"]
            html = result["resultado"]

            guardar_resultados(fecha, sede, dispositivo, ip, html)
    return resultados

if __name__ == "__main__":
    resultados = analizar_logs()
    enviarMail("bayledog12@gmail.com", resultados, SUBJECTS.LOGS)
   

