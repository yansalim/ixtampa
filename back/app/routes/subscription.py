# app/routes/subscription.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.extensions import db
import stripe

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscription', methods=['POST'])
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
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{'price': plan}],
            expand=['latest_invoice.payment_intent']
        )
        return jsonify({'message': 'Assinatura criada com sucesso.', 'subscription': subscription}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao criar assinatura: {str(e)}'}), 500