# app/routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db
from flask_jwt_extended import create_access_token
import stripe

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
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

@auth_bp.route('/login', methods=['POST'])
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