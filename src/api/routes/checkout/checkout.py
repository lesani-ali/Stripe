import stripe
from fastapi import APIRouter, HTTPException, Request, Response
import time

from ...config.config import CURRENCY, STRIPE_WEBHOOK_SECRET, FRONTEND_URL
from .utils import money_split, transfer_to_connected
from .schema import CreateCheckoutRequest, ReleasePayoutRequest

router = APIRouter()

# -------------------------
# Demo-only in-memory DB
# (replace with real DB)
# -------------------------
ORDERS = {}
PROCESSED_EVENTS = set()


@router.post("/create-setup-session")
def create_setup_session(req: CreateCheckoutRequest):
    """
    DELAYED CHARGE FLOW (save card now, charge later):
    - Create Checkout Session in mode="setup"
    - Stripe collects card details and saves a PaymentMethod (no money taken)
    - Webhook checkout.session.completed stores customer_id + payment_method_id
    """
    try:
        # Store order/booking details
        ORDERS[req.order_id] = {
            "order_id": req.order_id,
            "amount_cents": req.amount_cents,  # charge later
            "provider_account_id": req.provider_account_id,
            "referrer_account_id": req.referrer_account_id,
            "status": "created",
            "created_at": int(time.time()),
            # will be filled after setup completes:
            "customer_id": None,
            "payment_method_id": None,
        }

        session = stripe.checkout.Session.create(
            mode="setup",
            currency=CURRENCY,  # ✅ collect & save card, no charge
            success_url=f"{FRONTEND_URL}/pay/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/pay/cancel",
            metadata={"order_id": req.order_id},
            # recommended so you always get a Customer
            customer_creation="always",
        )

        return {"checkout_url": session.url, "session_id": session.id}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=getattr(e, "user_message", str(e)))


@router.post("/charge-order")
def charge_order_now(order_id: str):
    """
    Call this on the service date (e.g., 30 days later) to charge off-session.
    In production, you'd run this from a scheduled job/worker.

    - Requires order to have customer_id + payment_method_id (from setup webhook)
    - Creates off-session PaymentIntent
    - Transfers are done in webhook payment_intent.succeeded
    """
    try:
        order = ORDERS.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Unknown order_id")

        if not order.get("customer_id") or not order.get("payment_method_id"):
            raise HTTPException(status_code=400, detail="Card not saved yet (setup not completed)")

        if order.get("status") in ("charged", "paid_and_transferred"):
            return {"ok": True, "status": order["status"]}

        pi = stripe.PaymentIntent.create(
            amount=order["amount_cents"],
            currency=CURRENCY,
            customer=order["customer_id"],
            payment_method=order["payment_method_id"],
            off_session=True,
            confirm=True,
            description=f"Delayed charge for order {order_id}",
            metadata={"order_id": order_id},
            transfer_group=f"ORDER_{order_id}",
        )

        order["payment_intent_id"] = pi.id
        order["status"] = "charge_attempted"

        # Note: if SCA is needed, Stripe may return requires_action and raise an error.
        # We should handle that case by notifying the user to authenticate.
        return {"payment_intent_id": pi.id, "status": pi.status, "amount": pi.amount}

    except stripe.error.CardError as e:
        # Common for off-session if authentication is required
        # e.error.payment_intent may exist
        pi = getattr(e, "error", None)
        raise HTTPException(status_code=402, detail=getattr(e, "user_message", str(e)))
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=getattr(e, "user_message", str(e)))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handles BOTH:
    1) checkout.session.completed (mode=setup): save customer_id + payment_method_id
    2) payment_intent.succeeded: do transfers (provider + referrer)
    """
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Missing STRIPE_WEBHOOK_SECRET")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return Response(status_code=400)

    # Idempotency (demo)
    event_id = event.get("id")
    if event_id and event_id in PROCESSED_EVENTS:
        return Response(status_code=200)
    if event_id:
        PROCESSED_EVENTS.add(event_id)

    event_type = event["type"]

    # -----------------------------------
    # 1) Setup complete -> save card refs
    # -----------------------------------
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]

        # We only care about setup mode here
        if session.get("mode") != "setup":
            return Response(status_code=200)

        order_id = (session.get("metadata") or {}).get("order_id")
        setup_intent_id = session.get("setup_intent")

        if not order_id or order_id not in ORDERS:
            return Response(status_code=200)

        if not setup_intent_id:
            return Response(status_code=200)

        # Retrieve SetupIntent to get customer + payment_method
        si = stripe.SetupIntent.retrieve(setup_intent_id)

        ORDERS[order_id]["customer_id"] = si.customer
        ORDERS[order_id]["payment_method_id"] = si.payment_method
        ORDERS[order_id]["status"] = "card_saved"

        return Response(status_code=200)

    # -----------------------------------
    # 2) Payment succeeded -> do transfers
    # -----------------------------------
    if event_type == "payment_intent.succeeded":
        pi = event["data"]["object"]
        order_id = (pi.get("metadata") or {}).get("order_id")

        if not order_id or order_id not in ORDERS:
            return Response(status_code=200)

        order = ORDERS[order_id]
        provider_acct = order["provider_account_id"]
        referrer_acct = order["referrer_account_id"]

        amount_total = pi["amount"]
        payment_intent_id = pi["id"]
        transfer_group = pi.get("transfer_group") or f"ORDER_{order_id}"

        provider_amt, referrer_amt, platform_amt = money_split(amount_total)

        # For delayed/off-session charges, using source_transaction requires a charge id.
        # We retrieve the PI with expanded latest_charge.
        pi_full = stripe.PaymentIntent.retrieve(payment_intent_id, expand=["latest_charge"])
        charge_id = pi_full.latest_charge["id"] if pi_full.latest_charge else None
        if not charge_id:
            # Can't create source_transaction transfers without a charge
            return Response(status_code=200)

        t1 = transfer_to_connected(
            provider_acct,
            provider_amt,
            transfer_group,
            payment_intent_id,
            charge_id,
        )
        t2 = transfer_to_connected(
            referrer_acct,
            referrer_amt,
            transfer_group,
            payment_intent_id,
            charge_id,
        )

        order["status"] = "paid_and_transferred"
        order["payment_intent_id"] = payment_intent_id
        order["transfers"] = {"provider_transfer_id": t1.id, "referrer_transfer_id": t2.id}
        order["split"] = {"provider": provider_amt, "referrer": referrer_amt, "platform": platform_amt}

        return Response(status_code=200)

    return Response(status_code=200)


@router.post("/release-payout")
def release_payout(req: ReleasePayoutRequest):
    """
    Manual payouts: release money from connected account balance to bank.
    Works only if connected account has enough AVAILABLE balance.
    """
    try:
        bal = stripe.Balance.retrieve(stripe_account=req.connected_account_id)
        available = sum(x.amount for x in bal.available if x.currency == CURRENCY)

        if available < req.amount_cents:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough AVAILABLE balance. available={available}, requested={req.amount_cents}"
            )

        payout = stripe.Payout.create(
            amount=req.amount_cents,
            currency=CURRENCY,
            stripe_account=req.connected_account_id,
        )
        return {"payout_id": payout.id, "status": payout.status}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=getattr(e, "user_message", str(e)))