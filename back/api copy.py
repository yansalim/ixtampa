# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import uuid
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import stripe
from flasgger import Swagger

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações AWS S3
S3_BUCKET = os.environ.get('S3_BUCKET')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

# Novas variáveis para JWT, Banco de Dados e Stripe
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')

# Inicializa a aplicação Flask e configurações
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
swagger = Swagger(app)

# Inicializa o Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Cliente S3
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    stripe_customer_id = db.Column(db.String(120), nullable=True)  # Para integração com Stripe

    def __repr__(self):
        return f'<User {self.username}>'

# Cria as tabelas do banco de dados
with app.app_context():
    db.create_all()

@app.route('/upload', methods=['POST'])
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
    
    try:
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return jsonify({'url': file_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview', methods=['POST'])
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

    # Aqui você poderá implementar o processamento com Pillow para combinar as imagens
    return jsonify({'preview_url': 'https://exemplo.com/preview_placeholder.png'}), 200

@app.route('/register', methods=['POST'])
def register():
    """
    Endpoint de registro de usuário.
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
        required: true
    responses:
      200:
        description: Usuário registrado com sucesso.
      400:
        description: Dados inválidos ou usuário já existe.
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email e password são necessários.'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Usuário já existe.'}), 400

    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash)
    
    # Cria um cliente no Stripe para o novo usuário
    try:
        stripe_customer = stripe.Customer.create(email=email, name=username)
        new_user.stripe_customer_id = stripe_customer['id']
    except Exception as e:
        return jsonify({'error': f'Erro ao criar cliente no Stripe: {str(e)}'}), 500

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário registrado com sucesso.'}), 200

@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint de login.
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
        required: true
    responses:
      200:
        description: Token JWT de acesso.
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Credenciais inválidas.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username e password são necessários.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Credenciais inválidas.'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/subscription', methods=['POST'])
@jwt_required()
def manage_subscription():
    """
    Endpoint para gerenciamento de assinaturas.
    ---
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Token JWT (Bearer token)
      - in: body
        name: body
        schema:
          type: object
          properties:
            plan:
              type: string
              description: ID do preço/plano configurado no Stripe.
        required: true
    responses:
      200:
        description: Assinatura criada com sucesso.
        schema:
          type: object
          properties:
            message:
              type: string
            subscription:
              type: object
      400:
        description: Dados inválidos.
      500:
        description: Erro ao processar a assinatura.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    data = request.get_json()
    plan = data.get('plan')
    if not plan:
        return jsonify({'error': 'Plano é necessário.'}), 400

    try:
        # Cria a assinatura no Stripe
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{'price': plan}],  # 'plan' deve ser o ID do preço configurado no Stripe
            expand=['latest_invoice.payment_intent']
        )
        return jsonify({'message': 'Assinatura criada com sucesso.', 'subscription': subscription}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao criar assinatura: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)