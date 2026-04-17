from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from elevenlabs.client import ElevenLabs
import os
import uvicorn
import shutil

app = FastAPI()

# --- API CONFIGURATION ---
API_KEY = "sk_5421105f6d97732f3294868059b29b9597babb9236beebf3"
client = ElevenLabs(api_key=API_KEY)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Filmzi AI Dubbing</title>
        <style>
            body { background: #0b0b0b; color: #d4af37; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #161616; padding: 40px; border-radius: 20px; border: 2px solid #d4af37; text-align: center; width: 380px; box-shadow: 0 0 20px rgba(212,175,55,0.2); }
            h2 { letter-spacing: 2px; }
            input { margin: 20px 0; color: white; }
            button { background: #d4af37; color: #000; border: none; padding: 15px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; transition: 0.3s; }
            button:hover { background: #fff; }
            #status { margin-top: 20px; color: #00ff00; font-size: 13px; word-break: break-all; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>FILMZI AI</h2>
            <p style="color:#888;">Dub Movie to Sinhala</p>
            <input type="file" id="movieFile">
            <button id="btn" onclick="uploadFile()">START DUBBING</button>
            <div id="status"></div>
        </div>
        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('movieFile');
                const status = document.getElementById('status');
                const btn = document.getElementById('btn');
                
                if (fileInput.files.length === 0) return alert("Select file!");
                
                const formData = new FormData();
                formData.append("file", fileInput.files[0]);
                
                btn.disabled = true;
                status.innerText = "Processing... SDK eka haraha wade wenawa. Iwasala hitapan...";

                try {
                    const response = await fetch("/dub", { method: "POST", body: formData });
                    const result = await response.json();
                    status.innerText = "Done! Dubbing ID: " + (result.dubbing_id || "Check ElevenLabs Dashboard");
                } catch (e) {
                    status.innerText = "Error ekak awa machn!";
                } finally {
                    btn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/dub")
async def start_dubbing(file: UploadFile = File(...)):
    # Temporary save path
    file_path = f"temp_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # ElevenLabs SDK eka use karala dubbing start kirima
        with open(file_path, "rb") as audio_file:
            response = client.dubbing.dub_a_video_or_an_audio_file(
                file=audio_file,
                target_lang="si", # Official SDK eke 'si' thamai code eka
                mode="automatic",
                num_speakers=0, # Automatic speakers detect karanawa
                watermark=False
            )
        
        os.remove(file_path) # File eka delete karamu
        return {"dubbing_id": response.dubbing_id}

    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
