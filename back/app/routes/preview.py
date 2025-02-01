# app/routes/preview.py
from flask import Blueprint, request, jsonify

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

    # Aqui você pode chamar uma função de processamento de imagem
    preview_url = "https://exemplo.com/preview_placeholder.png"
    return jsonify({'preview_url': preview_url}), 200