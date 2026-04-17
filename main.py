from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
import requests
import os
import uvicorn

app = FastAPI()

# --- API CONFIGURATION ---
# Oya issella deepu key eka meke thiyanawa. VPS eke thawa secure karanna onenam 'os.getenv' use karamu.
API_KEY = "sk_5421105f6d97732f3294868059b29b9597babb9236beebf3"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Filmzi AI Dubber</title>
        <style>
            body { background: #0b0b0b; color: #d4af37; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #161616; padding: 40px; border-radius: 20px; border: 2px solid #d4af37; text-align: center; box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); width: 350px; }
            h2 { margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; }
            p { color: #888; font-size: 14px; }
            input[type="file"] { margin: 25px 0; color: #fff; width: 100%; }
            button { background: #d4af37; color: #000; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; transition: 0.3s; }
            button:hover { background: #fff; box-shadow: 0 0 15px #fff; }
            #status { margin-top: 25px; font-size: 14px; color: #00ff00; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Filmzi AI</h2>
            <p>Dub Movie to Sinhala (Natural Voice)</p>
            <input type="file" id="movieFile" accept="video/*,audio/*">
            <br>
            <button onclick="uploadFile()">START DUBBING</button>
            <div id="status"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('movieFile');
                const status = document.getElementById('status');
                
                if (fileInput.files.length === 0) {
                    alert("Ado file ekak select karapan issella!");
                    return;
                }

                const formData = new FormData();
                formData.append("file", fileInput.files[0]);

                status.innerText = "Processing... Meeka poddak wela yanawa machn.";

                try {
                    const response = await fetch("/dub", {
                        method: "POST",
                        body: formData
                    });

                    const result = await response.json();
                    if (result.dubbing_id) {
                        status.style.color = "#00ff00";
                        status.innerText = "Success! Dubbing ID: " + result.dubbing_id;
                    } else {
                        status.style.color = "#ff4444";
                        status.innerText = "Error: " + (result.detail || "Wade awul giya.");
                    }
                } catch (err) {
                    status.style.color = "#ff4444";
                    status.innerText = "Server error ekak awa!";
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
    
    # Temp save file
    file_path = f"temp_{file.filename}"
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        files = {
            "file": (file.filename, open(file_path, "rb"), file.content_type),
            "target_lang": (None, "si"),
        }

        response = requests.post(url, headers=headers, files=files)
        
        # Cleanup temp file
        os.remove(file_path)

        if response.status_code == 200:
            return response.json()
        else:
            return {"detail": response.text}
            
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"detail": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
