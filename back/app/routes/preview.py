# app/routes/preview.py
from flask import Blueprint, request, jsonify
from app.utils.image_processing import process_image  # Importe a função de processamento

preview_bp = Blueprint('preview', __name__)

@preview_bp.route('/preview', methods=['POST'])
def generate_preview():
    """
    Endpoint para gerar a pré-visualização do produto customizado.
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            image_url:
              type: string
            clothing_template:
              type: string
        required: true
    responses:
      200:
        description: URL da pré-visualização.
        schema:
          type: object
          properties:
            preview_url:
              type: string
      400:
        description: Dados insuficientes.
    """
    data = request.json
    if not data or 'image_url' not in data or 'clothing_template' not in data:
        return jsonify({'error': 'Dados insuficientes. Informe image_url e clothing_template.'}), 400

    # Chama a função que processa a imagem
    processed_path = process_image(data['image_url'], data['clothing_template'])

    # Se quiser, você pode checar se a função retornou algum erro em forma de string
    if processed_path.startswith("Erro"):
        return jsonify({'error': processed_path}), 500

    # Retorna o caminho (ou URL) do arquivo processado
    return jsonify({'preview_url': processed_path}), 200