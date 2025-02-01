# app/utils/image_processing.py
import requests
import io
from PIL import Image  # Removido Resampling da importação
import uuid
import os
import boto3
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (caso ainda não estejam carregadas)
load_dotenv()

# Variáveis de ambiente para S3
S3_BUCKET = os.environ.get("S3_BUCKET")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

def upload_to_s3(file_path):
    """
    Faz o upload de um arquivo para o S3 e retorna a URL pública.
    """
    s3_client = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    filename = f"{uuid.uuid4()}_{os.path.basename(file_path)}"
    s3_client.upload_file(file_path, S3_BUCKET, filename, ExtraArgs={'ACL': 'public-read'})
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"

def process_image(image_url, template, scale=0.25, upload=False):
    """
    Processa a imagem base obtida de `image_url` e sobrepõe o template (logo)
    fornecido como caminho local para o arquivo de imagem.

    Parâmetros:
      - image_url (str): URL da imagem base.
      - template (str): Caminho local para o arquivo de template (logo).
      - scale (float, opcional): Fator de escala para o template em relação à largura da imagem base (default=0.25).
      - upload (bool, opcional): Se True, faz upload da imagem processada para o S3 e retorna a URL pública.
    
    Retorna:
      - str: Caminho local da imagem processada ou a URL pública (caso upload seja True).
    """
    try:
        # Baixar a imagem base
        response = requests.get(image_url)
        response.raise_for_status()
        base_image = Image.open(io.BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        return f"Erro ao baixar ou abrir a imagem base: {str(e)}"

    try:
        # Abrir a imagem do template (logo)
        template_image = Image.open(template).convert("RGBA")
    except Exception as e:
        return f"Erro ao abrir o template: {str(e)}"

    # Redimensionar o template proporcionalmente
    base_width, base_height = base_image.size
    new_width = int(base_width * scale)
    template_aspect_ratio = template_image.width / template_image.height
    new_height = int(new_width / template_aspect_ratio)
    # Usa Image.LANCZOS em vez de Resampling.LANCZOS
    template_image = template_image.resize((new_width, new_height), Image.LANCZOS)

    # Define a posição: canto inferior direito com margem
    margin = 10
    position = (base_width - new_width - margin, base_height - new_height - margin)

    # Sobrepõe o template à imagem base
    base_image.paste(template_image, position, template_image)

    # Gera um nome único para o arquivo processado
    processed_filename = f"processed_{uuid.uuid4()}.png"
    base_image.save(processed_filename)

    if upload:
        # Envia a imagem processada para o S3 e remove o arquivo local
        public_url = upload_to_s3(processed_filename)
        os.remove(processed_filename)
        return public_url
    else:
        return processed_filename