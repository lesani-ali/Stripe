from pydantic import BaseModel

class CreateCheckoutRequest(BaseModel):
    order_id: str
    amount_cents: int
    provider_account_id: str  
    referrer_account_id: str

class ReleasePayoutRequest(BaseModel):
    connected_account_id: str
    amount_cents: int