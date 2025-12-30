import stripe

from .settings import settings

# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY
if not stripe.api_key:
    raise RuntimeError("Missing STRIPE_SECRET_KEY environment variable")

STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

# Application configuration
FRONTEND_URL = settings.FRONTEND_URL
CURRENCY = settings.CURRENCY

# Business logic configuration
PROVIDER_PCT = 0.70
REFERRER_PCT = 0.10