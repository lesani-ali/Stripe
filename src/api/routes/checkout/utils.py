import stripe
from ...config.config import CURRENCY, PROVIDER_PCT, REFERRER_PCT


def money_split(total_amount_cents: int):
    provider_amt = int(round(total_amount_cents * PROVIDER_PCT))
    referrer_amt = int(round(total_amount_cents * REFERRER_PCT))
    platform_amt = total_amount_cents - provider_amt - referrer_amt
    if platform_amt < 0:
        raise ValueError("Split produced negative platform amount.")
    return provider_amt, referrer_amt, platform_amt

def transfer_to_connected(
    destination_acct: str, 
    amount_cents: int, 
    transfer_group: str, 
    payment_intent_id: str,
    charge_id: str
):
    return stripe.Transfer.create(
        amount=amount_cents,
        currency=CURRENCY,
        destination=destination_acct,
        transfer_group=transfer_group,
        source_transaction=charge_id,
        metadata={"payment_intent_id": payment_intent_id},
    )