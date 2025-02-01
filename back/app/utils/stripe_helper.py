# app/utils/stripe_helper.py
import stripe

def create_stripe_subscription(customer_id, price_id):
    """
    Cria uma assinatura no Stripe para o cliente e preço informados.
    """
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            expand=['latest_invoice.payment_intent']
        )
        return subscription
    except Exception as e:
        raise e