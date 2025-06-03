# Field Validation FastAPI Service

## Steps to Use the Code

1. **Unzip the file**  
   Extract the contents of the provided archive to your desired directory.

2. **Install Dependencies**  
   Make sure you have Python 3.8+ installed.  
   Install the required Python packages using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**  
   - Open the `.env` file in the project root.
   - Set the correct paths for your certificates:
     ```
     CURL_CA_BUNDLE=/path/to/cacert.pem
     REQUESTS_CA_BUNDLE=/path/to/cacert.pem
     SSL_CERT_FILE=/path/to/cacert.pem
     ```
   - Add your host machine's username and password:
     ```
     USERNAME=your_username
     PASSWORD=your_password
     ```
   - You may also edit `CLIENT_ID` and `RESOURCE` if needed.

4. **(Optional) Check Java Version**  
   If you want HTML syntax validation using the local W3C validator, ensure you have Java 11 or higher:
   ```bash
   java -version
   ```
   If Java is installed and version is 11 or higher:
   - Open `new_main.py`
   - **Uncomment** line 72 and **comment out** line 73 to enable local HTML validation.

5. **Start the FastAPI Server**  
   Run the following command to start the server:
   ```bash
   uvicorn new_main:app --reload
   ```

## Usage

The main endpoint you will use is:  
```
/code_correction
```

### Preparing Your HTML

1. **Escape your HTML** before sending it to the API:
   ```python
   from html_escaper_deescaper import escape_html, deescape_html

   escaped_html = escape_html(raw_html)
   ```

2. **Send a POST request** to the `/code_correction` endpoint:
   ```python
   import requests

   url = '<server url>/code_correction'
   headers = {
       'accept': 'application/json',
       'Content-Type': 'application/json',
   }
   data = {
       'html': '<escaped_html>',
   }
   response = requests.post(url, headers=headers, json=data)
   print(response.json())
   ```

3. **De-escape the response** to get the corrected HTML:
   ```python
   raw_html = deescape_html(escaped_html)
   ```

The response should be a single-line, escaped HTML string, which you can convert back to raw HTML using `deescape_html`.

---

**Note:**  
- Only the `/code_correction` endpoint is relevant for most users.
- Make sure your `.env` file is correctly configured before starting the server.
- For HTML validation, Java 11+ is required and the validator must be set up as described above.
