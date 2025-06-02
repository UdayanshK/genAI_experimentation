import subprocess
import tempfile
import os
import json

# Update this to your actual vnu.jar path
VNU_JAR_PATH = r"C:\tools\vnu\vnu.jar"

def validate_html(html_code: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
        temp_file.write(html_code)
        temp_file_path = temp_file.name

    try:
        cmd = [
            "java", "-jar", VNU_JAR_PATH,
            "--format", "json", temp_file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {"valid": True, "messages": []}

        output = result.stdout if result.stdout else result.stderr
        report = json.loads(output)

        messages = []
        for msg in report.get("messages", []):
            messages.append({
                "type": msg.get("type"),
                "message": msg.get("message"),
                "extract": msg.get("extract"),
                "line": msg.get("lastLine"),
                "column": msg.get("lastColumn"),
                "hiliteStart": msg.get("hiliteStart"),
                "hiliteLength": msg.get("hiliteLength"),
                "subType": msg.get("subType"),
            })

        return {"valid": False, "messages": messages}

    finally:
        os.remove(temp_file_path)

____________SERVER________________________-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from html_validator import validate_html

app = FastAPI()

class HTMLRequest(BaseModel):
    html: str

@app.post("/validate")
def validate(request: HTMLRequest):
    try:
        return validate_html(request.html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
