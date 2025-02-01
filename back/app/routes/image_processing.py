# app/utils/image_processing.py
import requests
import io
from PIL import Image

def process_image(image_url, template):
    """
    Processa a imagem base obtida de `image_url` e sobrepõe o template (logo)
    fornecido como caminho local para o arquivo de imagem.
    
    Retorna o caminho local para a imagem processada.
    """
    try:
        # Baixar a imagem base a partir da URL
        response = requests.get(image_url)
        response.raise_for_status()  # Levanta uma exceção em caso de erro
        base_image = Image.open(io.BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        return f"Erro ao baixar ou abrir a imagem base: {str(e)}"

    try:
        # Abrir a imagem do template (logo) a partir do caminho local
        template_image = Image.open(template).convert("RGBA")
    except Exception as e:
        return f"Erro ao abrir o template: {str(e)}"

    # Redimensionar o template para ser proporcional à imagem base
    base_width, base_height = base_image.size
    new_width = base_width // 4  # Por exemplo, 25% da largura da imagem base
    template_aspect_ratio = template_image.width / template_image.height
    new_height = int(new_width / template_aspect_ratio)
    template_image = template_image.resize((new_width, new_height), Image.ANTIALIAS)

    # Definir a posição para o template: canto inferior direito com uma margem
    margin = 10
    position = (base_width - new_width - margin, base_height - new_height - margin)

    # Colar o template na imagem base, usando o próprio template como máscara (para preservar a transparência)
    base_image.paste(template_image, position, template_image)

    # Salvar a imagem processada localmente
    processed_image_path = "processed_image.png"
    base_image.save(processed_image_path)

    return processed_image_path