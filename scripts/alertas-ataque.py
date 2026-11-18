#!/usr/bin/env python3
"""
Evidencia de deteccion para la tabla 2.4.
Lista, para una IP de origen y una hora de inicio, la PRIMERA alerta de cada regla
generada en el SIEM y el tiempo transcurrido desde el inicio del ataque.

Uso (desde la carpeta del repositorio, en la laptop):
    python3 scripts/alertas-ataque.py <IP_ORIGEN> "<AAAA-MM-DD HH:MM:SS>" [nivel_minimo]
Ejemplo:
    python3 scripts/alertas-ataque.py 192.168.56.30 "2026-11-17 20:05:10" 3

La hora de inicio se toma en Kali justo antes de lanzar el ataque:  date "+%F %T"
(Todas las VM usan la zona America/Costa_Rica, UTC-6.)
"""
import json, subprocess, sys
from datetime import datetime, timezone, timedelta

if len(sys.argv) < 3:
    sys.exit(__doc__)
ip, inicio_txt = sys.argv[1], sys.argv[2]
nivel_min = int(sys.argv[3]) if len(sys.argv) > 3 else 3
CR = timezone(timedelta(hours=-6))
inicio = datetime.strptime(inicio_txt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=CR)

# Solo las lineas que mencionan la IP (filtrado en el SIEM para no traer todo el archivo)
cmd = ["vagrant", "ssh", "siem", "-c",
       f"sudo grep -F '\"{ip}\"' /var/ossec/logs/alerts/alerts.json"]
salida = subprocess.run(cmd, capture_output=True, text=True).stdout

primeras = {}
for linea in salida.splitlines():
    try:
        a = json.loads(linea)
    except json.JSONDecodeError:
        continue
    d = a.get("data", {})
    if ip not in (d.get("srcip"), d.get("src_ip")):
        continue
    t = datetime.strptime(a["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
    r = a["rule"]
    if t < inicio or r["level"] < nivel_min:
        continue
    cuenta = primeras.get(r["id"], (None, None, 0))[2] + 1
    if r["id"] not in primeras:
        primeras[r["id"]] = (t, a, cuenta)
    else:
        primeras[r["id"]] = (primeras[r["id"]][0], primeras[r["id"]][1], cuenta)

if not primeras:
    sys.exit(f"Sin alertas de nivel >= {nivel_min} para {ip} desde {inicio_txt}")

print(f"Origen {ip} | inicio {inicio_txt} (UTC-6) | nivel >= {nivel_min}\n")
print(f"{'Regla':>7} {'Niv':>3} {'Primera alerta':>15} {'T+ (s)':>8} {'Total':>5}  MITRE        Descripcion")
for rid, (t, a, n) in sorted(primeras.items(), key=lambda x: x[1][0]):
    r = a["rule"]
    mitre = ",".join(r.get("mitre", {}).get("id", [])) or "-"
    delta = (t - inicio).total_seconds()
    print(f"{rid:>7} {r['level']:>3} {t.strftime('%H:%M:%S.%f')[:-3]:>15} {delta:>8.1f} {n:>5}  {mitre:<12} {r['description'][:90]}")
