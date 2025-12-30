from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def index():
    return "<h1>Hello</h1>"

@router.get("/onboarding/complete", response_class=HTMLResponse)
def onboarding_complete():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Onboarding Complete</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 {
                color: #2e7d32;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Onboarding Complete ✅</h1>
            <p>Your Stripe onboarding is finished.</p>
            <p>You can safely close this page.</p>
        </div>
    </body>
    </html>
    """

@router.get("/onboarding/refresh", response_class=HTMLResponse)
def onboarding_refresh():
    return "<h1>Please continue onboarding</h1>"


