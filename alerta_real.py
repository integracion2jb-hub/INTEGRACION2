import os
import time
import re
from enviarEmail import enviarMail, SUBJECTS
# Ruta hacia los logs a observar
LOG_PATH = "/var/log/central-logs/suricata-192.30.30.5.log"
PATRONES_CRITICOS = [
    r"Priority:\s*1",
    r"\bET\s+TROJAN\b",
    r"\bET\s+EXPLOIT\b",
    r"\bET\s+MALWARE\b",
    r"\bET\s+ATTACK\b",
    r"\bET\s+SCAN\b",
]

def es_alerta_critica(linea):
    for patron in PATRONES_CRITICOS:
        if re.search(patron, linea, re.IGNORECASE):
            return True
    return False

def abrir_log(path):
    # abrir en modo lectura, con encoding seguro
    return open(path, "r", encoding="utf-8", errors="ignore")

def monitorear_suricata():
    print("Iniciando el monitoreo en archivo de logs suricata")
    path = LOG_PATH
    if not os.path.exists(path):
        print(f"ALERTA!!! Archivo no existe: {path}")
        return

    f = abrir_log(path)
    f.seek(0, os.SEEK_END)   # empezar en el final del archivo, similar a tail -f
    inode = os.fstat(f.fileno()).st_ino # encontrar inodo del archivo
    partial = ""             # buffer para líneas parciales
    seen_hashes = set()      # opcional para evitar duplicados exactos (puedes limitar su tamaño)

    try:
        while True:
            line = f.readline()
            if not line:
                # comprobar si archivo fue rotado/reemplazado/truncado
                try:
                    st = os.stat(path)
                    if st.st_ino != inode:
                        # archivo reemplazado: reabrir el nuevo
                        f.close()
                        f = abrir_log(path)
                        inode = os.fstat(f.fileno()).st_ino
                        f.seek(0, os.SEEK_END)
                        print("[↺] Detectada rotación/reemplazo del archivo. Reabriendo.")
                except FileNotFoundError:
                    # archivo temporalmente no existe (rotación). esperar y reintentar.
                    time.sleep(1)
                time.sleep(0.5)
                continue

            # Gestionar lineas parciales (En caso de que el escritor todavia no haya escrito '/n' )
            if not line.endswith("\n"):
                partial += line
                # no procesamos hasta que tengamos la línea completa
                continue
            else:
                if partial:
                    line = partial + line
                    partial = ""

            line = line.strip()
            if not line:
                continue

            # Evitar re-notificar exactamente la misma línea en corto plazo
            h = hash(line)
            if h in seen_hashes:
                # ya la vimos recientemente -> saltar
                continue
            # mantener conjunto pequeño (ej: última 100 entradas)
            seen_hashes.add(h)
            if len(seen_hashes) > 150:
                # eliminar algunos hashes arbitrariamente
                seen_hashes = set(list(seen_hashes)[-100:])

            # filtrar por patrón crítico
            if es_alerta_critica(line):
                print(f"[⚠️] ALERTA: {line}")
                enviarMail("correo_admin@gmail.com", line, SUBJECTS.ALERTA_REAL)
    except KeyboardInterrupt:
        print("\n[🛑] Monitoreo detenido manualmente.")
    finally:
        try:
            f.close()
        except:
            pass

if __name__ == "__main__":
    monitorear_suricata()