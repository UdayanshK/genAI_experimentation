import subprocess
import tempfile
import os
import json
import re

# Update this to your actual vnu.jar path
VNU_JAR_PATH = r"vnu.jar_20.6.30/dist/vnu.jar"

def _run_validator_on_html(html_fragment: str) -> list:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
        temp_file.write(html_fragment)
        temp_file_path = temp_file.name

    try:
        cmd = [
            "java", "-jar", VNU_JAR_PATH,
            "--format", "json", temp_file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return []

        output = result.stdout if result.stdout else result.stderr
        report = json.loads(output)
        return report.get("messages", [])

    finally:
        os.remove(temp_file_path)


def validate_html(html_code: str):
    sections = {
        "full": html_code,
        "head": _extract_tag_content(html_code, "head"),
        "body": _extract_tag_content(html_code, "body")
    }

    all_errors = []

    for section_name, content in sections.items():
        if content:
            fake_html = f"<!DOCTYPE html><html><{section_name}>{content}</{section_name}></html>"
            messages = _run_validator_on_html(fake_html)
            for msg in messages:
                msg["scope"] = section_name
                all_errors.append(msg)

    return {
        "valid": len(all_errors) == 0,
        "messages": [
            {
                "scope": msg.get("scope", "full"),
                "type": msg.get("type"),
                "message": msg.get("message"),
                "extract": msg.get("extract"),
                "line": msg.get("lastLine"),
                "column": msg.get("lastColumn"),
                "hiliteStart": msg.get("hiliteStart"),
                "hiliteLength": msg.get("hiliteLength"),
                "subType": msg.get("subType"),
            }
            for msg in all_errors
        ]
    }

def _extract_tag_content(html: str, tag: str) -> str:
    """Extracts content inside a specific HTML tag."""
    pattern = re.compile(rf"<{tag}[^>]*>(.*?)</{tag}>", re.DOTALL | re.IGNORECASE)
    match = pattern.search(html)
    return match.group(1).strip() if match else ""


if __name__=="__main__":
    # Example usage
    html_code = """<!DOCTYPE html>
    <html>
    <head>
        <title>Broken Page<title>
        <meta charset="UTF-8">
        <link href="style.css">
    </head>
    <body>
        <h1>Welcome to My Page
        <p>This paragraph is not closed
        <div>
        <ul>
            <li>Item one
            <li>Item two
        </div>
    </body>
    </html>
    """
    
    result = validate_html(html_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
