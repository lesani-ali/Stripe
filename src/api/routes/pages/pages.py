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

@router.get("/pay/success", response_class=HTMLResponse)
def payment_success():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .box {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }
            h1 {
                color: #2e7d32;
                margin-bottom: 20px;
            }
            .icon {
                font-size: 60px;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <div class="icon">✅</div>
            <h1>Payment Successful!</h1>
            <p>Your card has been saved successfully.</p>
            <p>You'll be charged when your service is delivered.</p>
            <p>You can safely close this page.</p>
        </div>
    </body>
    </html>
    """

@router.get("/pay/cancel", response_class=HTMLResponse)
def payment_cancel():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .box {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }
            h1 {
                color: #d32f2f;
                margin-bottom: 20px;
            }
            .icon {
                font-size: 60px;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                line-height: 1.6;
            }
            .btn {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: #1976d2;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            .btn:hover {
                background: #1565c0;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <div class="icon">❌</div>
            <h1>Payment Cancelled</h1>
            <p>Your payment was cancelled.</p>
            <p>No charges were made to your account.</p>
            <a href="/" class="btn">Return to Home</a>
        </div>
    </body>
    </html>
    """