from pydantic import BaseModel, EmailStr

class CreateConnectedAccountRequest(BaseModel):
    country: str = "US"
    email: EmailStr
    manual_payouts: bool = True


class CreateOnboardingLinkRequest(BaseModel):
    connected_account_id: str