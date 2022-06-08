import os
import uuid
import requests
from sanic.log import logger
from sanic import  Request, Sanic, json

app = Sanic(__name__)
config = {}
config["upload"] = "./uploads"

BASE_URL = "http://103.233.219.109:50051/upload"

def start_server():
    """ Function for bootstrapping sanic app. """
    # error hanlder
    app.config.FALLBACK_ERROR_FORMAT = "json"

    app.go_fast(debug=False, workers=2, host='0.0.0.0', access_log=False,auto_reload=True, port=6666)


@app.route("/upload", methods=['POST'])
def upload_audio(request : Request):
    os.makedirs(config['uploads'], exist_ok=True)

    try:
        test_file = request.files.get("audio")
        file_parameters = {
            'body': test_file.body,
            'name': test_file.name,
            'type': test_file.type,
        }

        if str(file_parameters['name']).endswith('.wav'):
            uid = str(uuid.uuid4())
            uuid_dir = f"{config['upload']}/{uid}"
            os.makedirs(uuid_dir, exist_ok=True)
            file_path = f"{uuid_dir}/{file_parameters['name']}"
            with open(file_path, 'wb') as f:
                f.write(file_parameters['body'])

            logger.info(f'file wrote to disk - {file_path}')

            # send the audio to the main server
            res = get_transcription(file_path)

            return json({"trancription": res, "file_name": file_parameters['name'], "success": True })
        
        return json({"file_name": file_parameters['name'], "success": False, "status": "invalid file uploaded" })
    except Exception as e:
        return json({"error": "bad_request", "log": str(e)}, status=403)


def get_transcription(path : str) -> str:
    payload={}
    files=[
        ('audio',('original_audio.wav',open(path,'rb'),'audio/wav'))
    ]
    headers = {}

    response = requests.request("POST", BASE_URL, headers=headers, data=payload, files=files)

    print(response.text)
    return response.text


if __name__ == '__main__':
    start_server()
