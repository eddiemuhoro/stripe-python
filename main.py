from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import stripe
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Define data model for items
class Item(BaseModel):
    price: float

class Items(BaseModel):
    items: list[Item]

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Stripe Payment API!"}

# Config endpoint to retrieve publishable key
@app.get("/config")
async def get_config():
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    if not publishable_key:
        raise HTTPException(status_code=500, detail="Publishable key not found.")
    return {"publishableKey": publishable_key}

# Endpoint to create a PaymentIntent
@app.post("/create-payment-intent")
async def create_payment_intent(data: Items):
    try:
        total = sum(item.price for item in data.items)
        amount = int(total * 100)  # Convert to cents
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="KES",
            automatic_payment_methods={"enabled": True},
        )
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
