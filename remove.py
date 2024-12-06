from flask import Flask, render_template, request, send_file
from rembg import remove
from PIL import Image
import io
import os
from pymongo import MongoClient
import time

app = Flask(__name__, template_folder='/templates/index.html')


# Configuração do MongoDB
client = MongoClient('mongodb+srv://alan:123@cluster0.z5foh.mongodb.net/?retryWrites=true&w=majority')
db = client['image_db']  
images_collection = db['images']  

# Diretório de uploads
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    input_data = file.read()
    output_data = remove(input_data)

    output_image = Image.open(io.BytesIO(output_data))

    output_path = os.path.join(UPLOAD_FOLDER, 'output.png')
    output_image.save(output_path)

    # Adicionando um campo de timestamp no banco de dados
    image_info = {
        'original_filename': file.filename,
        'output_filename': 'output.png',
        'image_url': output_path,  
        'timestamp': time.time()  # Armazenar o timestamp atual
    }
    
    images_collection.insert_one(image_info)

    return render_template('index.html', image_url=output_path)

def cleanup_images():
    """Limpar imagens e documentos no MongoDB após 1 hora"""
    current_time = time.time()
    expiration_time = 60 * 60  # 1 hora (em segundos)

    # Buscar imagens que estão expiradas
    expired_images = images_collection.find({'timestamp': {'$lt': current_time - expiration_time}})

    for image in expired_images:
        # Remover a imagem do diretório de uploads
        file_path = image['image_url']
        if os.path.exists(file_path):
            os.remove(file_path)  # Exclui o arquivo

        # Remover o documento do banco de dados
        images_collection.delete_one({'_id': image['_id']})  # Exclui o documento do MongoDB

if __name__ == '__main__':
    app.run(debug=True)

    # Agendar a limpeza das imagens antigas a cada 30 minutos
    from threading import Timer
    def schedule_cleanup():
        cleanup_images()
        # Chama a função novamente após 30 minutos (1800 segundos)
        Timer(1800, schedule_cleanup).start()

    schedule_cleanup()  # Inicia a limpeza periódica ao rodar a aplicação
