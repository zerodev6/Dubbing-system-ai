from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
import requests
import os
import uvicorn

app = FastAPI()

# --- API CONFIGURATION ---
API_KEY = "sk_5421105f6d97732f3294868059b29b9597babb9236beebf3"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Filmzi AI Dubbing Studio</title>
        <style>
            body { background: #0b0b0b; color: #d4af37; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #161616; padding: 40px; border-radius: 20px; border: 2px solid #d4af37; text-align: center; box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); width: 380px; }
            h2 { margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; color: #d4af37; }
            p { color: #888; font-size: 14px; }
            input[type="file"] { margin: 25px 0; color: #fff; width: 100%; border: 1px dashed #444; padding: 10px; border-radius: 5px; }
            button { background: #d4af37; color: #000; border: none; padding: 15px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; transition: 0.3s; }
            button:hover { background: #fff; box-shadow: 0 0 20px #fff; }
            #status { margin-top: 25px; font-size: 14px; color: #00ff00; font-weight: bold; word-break: break-all; }
            .loader { border: 4px solid #f3f3f3; border-top: 4px solid #d4af37; border-radius: 50%; width: 30px; height: 30px; animation: spin 2s linear infinite; display: none; margin: 10px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Filmzi AI</h2>
            <p>Dub Movie to Sinhala (Original Voice)</p>
            <input type="file" id="movieFile" accept="video/*,audio/*">
            <br>
            <button id="dubBtn" onclick="uploadFile()">START DUBBING</button>
            <div id="loader" class="loader"></div>
            <div id="status"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('movieFile');
                const status = document.getElementById('status');
                const btn = document.getElementById('dubBtn');
                const loader = document.getElementById('loader');
                
                if (fileInput.files.length === 0) {
                    alert("Ado file ekak select karahan!");
                    return;
                }

                const formData = new FormData();
                formData.append("file", fileInput.files[0]);

                status.style.color = "#d4af37";
                status.innerText = "Uploading & Processing... Poddak iwasala hitapan machn.";
                btn.disabled = true;
                loader.style.display = "block";

                try {
                    const response = await fetch("/dub", {
                        method: "POST",
                        body: formData
                    });

                    const result = await response.json();
                    loader.style.display = "none";
                    btn.disabled = false;

                    if (result.dubbing_id) {
                        status.style.color = "#00ff00";
                        status.innerText = "Wade Hari! Dubbing ID: " + result.dubbing_id + "\\nElevenLabs Dashboard eke balapan.";
                    } else {
                        status.style.color = "#ff4444";
                        status.innerText = "Error: " + JSON.stringify(result.detail);
                    }
                } catch (err) {
                    loader.style.display = "none";
                    btn.disabled = false;
                    status.style.color = "#ff4444";
                    status.innerText = "Server error ekak awa! Connection eka check karapan.";
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
    
    # Save file temporary
    file_path = f"temp_{file.filename}"
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Payload updated with correct language name
        files = {
            "file": (file.filename, open(file_path, "rb"), file.content_type),
            "target_lang": (None, "sinhala"), # Corrected from 'si' to 'sinhala'
        }

        response = requests.post(url, headers=headers, files=files)
        
        # Always remove the temp file
        os.remove(file_path)

        if response.status_code == 200:
            return response.json()
        else:
            return {"detail": response.json() if response.headers.get('content-type') == 'application/json' else response.text}
            
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"detail": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
