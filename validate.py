"""Validação REST com uma chamada de inferência paga e verificações HTTP."""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

root = Path(__file__).resolve().parent
url = os.environ.get("APP_BASE_URL", "http://localhost:8080/").rstrip("/") + "/"
auth = ("poc", os.environ["APP_PASSWORD"])
now = datetime.now(ZoneInfo("America/Sao_Paulo"))
question = {"message": f"Pesquise uma notícia publicada hoje ({now.date()}, horário de Brasília). Informe título, data, resumo e URL. Verifique a página; se não encontrar, diga isso claramente."}
started = time.monotonic()
response = requests.post(url + "api/chat", auth=auth, json=question, timeout=180)
report = {"tested_at": now.isoformat(), "request": question, "http": response.status_code,
          "seconds": round(time.monotonic() - started, 2), "response": response.json()}
folder = root / "evidence"
folder.mkdir(exist_ok=True)
(folder / "rest-news-today.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
response.raise_for_status()
data = response.json()
assert data["answer"], "Resposta vazia"
assert any(call["status"] == "completed" for call in data["web_search_calls"]), "Busca não confirmada"
assert data["citations"], "Citações ausentes"
checks = {path or "index": requests.get(url + path, auth=auth, timeout=20).status_code
          for path in ("", "app.js", "health")}
checks["unauthenticated_post"] = requests.post(url + "api/chat", json=question, timeout=20).status_code
checks["invalid_history"] = requests.post(url + "api/chat", auth=auth,
    json={"message": "test", "history": [{"role": "system", "content": "test"}]}, timeout=20).status_code
(folder / "http-checks.json").write_text(json.dumps(checks, indent=2))
assert checks == {"index": 200, "app.js": 200, "health": 200, "unauthenticated_post": 401, "invalid_history": 422}
print(f"REST HTTP 200; busca e citações presentes; {report['seconds']} s. Evidências em ./evidence/")
