
# Stripe Connect Payment System

A FastAPI-based payment platform implementing Stripe Connect for marketplace/platform payments with delayed charging capability. This project is for demo purposes only; real implementations need additional production hardening.

## Prerequisites

- Python 3.12+
- Stripe Account
- Domain with SSL (production)
- For local development, `localhost` is fine.

---

## Setup Instructions

### Step 1: Get Stripe API Keys

- Go to: https://dashboard.stripe.com/ --> developers --> API Keys
- Copy your **Secret key**

### Step 2: Set Up Webhooks

1. Production (custom domain + SSL):
    - Go to: https://dashboard.stripe.com/ --> Webhooks
    - Click **"Add destination"**
    - Endpoint URL: `https://yourdomain.com/checkout/webhook`
    - Select events: `checkout.session.completed`, `payment_intent.succeeded`
    - Copy the **Signing secret**
2. For local development, use the Stripe CLI to forward webhooks: 
    ```bash
    stripe listen --forward-to http://localhost:3010/checkout/webhook
    ```

---

## Python Project Setup

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root and update variables:

```bash
cp .env.example .env
```
Required variables are listed in `.env.example`: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `FRONTEND_URL`, `CURRENCY`.

### 3. Start the Application

```bash
# Development (with auto-reload)
uvicorn src.api.main:app --host 127.0.0.1 --port 3010 --reload

# Production (with Gunicorn)
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:3010
```

`FRONTEND_URL` is set via env vars, and the onboarding pages are served from `src/api/routes/pages`.

---

## API Endpoints
This demo uses in-memory storage for orders and processed events, so data resets on restart.

### Onboarding

**Create Connected Account**
```bash
curl -X POST http://localhost:3010/onboarding/connected-account \
  -H "Content-Type: application/json" \
  -d '{
    "country": "US",
    "email": "provider@example.com",
    "manual_payouts": true
  }'
```

**Generate Onboarding Link**
```bash
curl -X POST http://localhost:3010/onboarding/onboarding-link \
  -H "Content-Type: application/json" \
  -d '{
    "connected_account_id": "acct_xxxxx"
  }'
```

### Checkout & Payments

**Create Setup Session (Save Card)**
```bash
curl -X POST http://localhost:3010/checkout/create-setup-session \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_123",
    "amount_cents": 10000,
    "provider_account_id": "acct_provider",
    "referrer_account_id": "acct_referrer"
  }'
```

**Charge Order Later**
```bash
curl -X POST "http://localhost:3010/checkout/charge-order?order_id=order_123"
```

**Release Payout**
```bash
curl -X POST http://localhost:3010/checkout/release-payout \
  -H "Content-Type: application/json" \
  -d '{
    "connected_account_id": "acct_xxxxx",
    "amount_cents": 7000
  }'
```

---

## Test Cards

Use these cards in test mode:

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 0077` | Charge succeeds, funds available immediately |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |
| `4000 0000 0000 9995` | Declined |

**Expiry:** Any future date  
**CVC:** Any 3 digits  
**ZIP:** Any 5 digits

More info: check [this](https://docs.stripe.com/testing)

---

## Production Deployment

### 1. Update Environment Variables
```env
STRIPE_SECRET_KEY="sk_live_YOUR_LIVE_KEY"
STRIPE_WEBHOOK_SECRET="whsec_YOUR_PRODUCTION_WEBHOOK_SECRET"
FRONTEND_URL="https://yourdomain.com"
CURRENCY="usd"
```

### 2. Set Up Nginx Reverse Proxy

```nginx
server {
    server_name yourdomain.com;
    client_max_body_size 100M;

    
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    location / {
        proxy_pass http://127.0.0.1:3010; #PORT API_CLIENT
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable SSL
```bash
sudo certbot --nginx -d yourdomain.com
```
