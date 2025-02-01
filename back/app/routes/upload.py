# app/routes/upload.py
from flask import Blueprint, request, jsonify, current_app
import boto3
import uuid

upload_bp = Blueprint('upload', __name__)

def get_s3_client():
    config = current_app.config
    return boto3.client(
        's3',
        region_name=config['AWS_REGION'],
        aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY']
    )

@upload_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    Endpoint para upload de imagem.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Arquivo de imagem a ser enviado.
    responses:
      200:
        description: URL da imagem carregada.
        schema:
          type: object
          properties:
            url:
              type: string
      400:
        description: Nenhum arquivo enviado.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    filename = f"{uuid.uuid4()}_{file.filename}"
    s3_client = get_s3_client()
    try:
        s3_client.upload_fileobj(
            file,
            current_app.config['S3_BUCKET'],
            filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        file_url = f"https://{current_app.config['S3_BUCKET']}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{filename}"
        return jsonify({'url': file_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500