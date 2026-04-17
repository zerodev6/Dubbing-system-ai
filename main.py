From fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os

app = FastAPI()

# API Configuration
API_KEY = "sk_5421105f6d97732f3294868059b29b9597babb9236beebf3"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Simple HTML UI eka methana thiyenne
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Dubbing Studio</title>
        <style>
            body { background: #0f0f0f; color: #gold; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1a1a1a; padding: 30px; border-radius: 15px; border: 1px solid #d4af37; text-align: center; box-shadow: 0 0 20px rgba(212, 175, 55, 0.2); }
            input { margin: 20px 0; color: white; }
            button { background: #d4af37; color: black; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
            #status { margin-top: 20px; color: #00ff00; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Filmzi AI Dubber</h2>
            <p>Select Movie File (MP4/MP3)</p>
            <input type="file" id="movieFile">
            <br>
            <button onclick="uploadFile()">Start Dubbing</button>
            <div id="status"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('movieFile');
                const status = document.getElementById('status');
                
                if (fileInput.files.length === 0) {
                    alert("Please select a file first!");
                    return;
                }

                const formData = new FormData();
                formData.append("file", fileInput.files[0]);

                status.innerText = "Uploading & Processing... Please wait.";

                const response = await fetch("/dub", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();
                if (result.dubbing_id) {
                    status.innerText = "Dubbing Started! ID: " + result.dubbing_id;
                } else {
                    status.innerText = "Error: " + result.detail;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/dub")
async def start_dubbing(file: UploadFile = File(...)):
    url = "https://api.elevenlabs.io/v1/dubbing"
    headers = {"xi-api-key": API_KEY}
    
    # File eka temporary save karaganna
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    files = {
        "file": (file.filename, open(file_path, "rb"), file.content_type),
        "target_lang": (None, "si"),
    }

    response = requests.post(url, headers=headers, files=files)
    os.remove(file_path) # Temp file eka ain karanna

    if response.status_code == 200:
        return response.json()
    else:
        return {"detail": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
