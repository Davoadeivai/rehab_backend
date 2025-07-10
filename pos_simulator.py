import time
import random
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# --- FastAPI App Initialization ---
app = FastAPI(
    title="POS Simulator API",
    description="A simple API to simulate a physical POS device for payment processing.",
    version="1.0.0"
)

# --- Pydantic Models for Request/Response ---
class PaymentRequest(BaseModel):
    amount: float
    request_id: str

class PaymentResponse(BaseModel):
    status: str
    transaction_id: str | None = None
    message: str
    pos_data: dict | None = None

# --- API Endpoint ---
@app.post("/api/v1/pay", response_model=PaymentResponse)
async def process_payment(payment_request: PaymentRequest):
    """
    Simulates processing a payment through a POS device.

    Receives a payment amount and a unique request ID.
    After a simulated delay, it randomly returns a success or failure response.
    """
    print(f"Received payment request {payment_request.request_id} for amount: {payment_request.amount}")

    # Simulate delay for card processing (e.g., 2 to 5 seconds)
    time.sleep(random.randint(2, 5))

    # Randomly determine if the transaction is successful or failed
    if random.random() < 0.85:  # 85% chance of success
        transaction_id = f"POS_TRX_{int(time.time())}{random.randint(100, 999)}"
        print(f"Payment successful for request {payment_request.request_id}. Transaction ID: {transaction_id}")
        return PaymentResponse(
            status="successful",
            transaction_id=transaction_id,
            message="پرداخت با موفقیت انجام شد.",
            pos_data={
                "terminal_id": "T12345",
                "card_mask": "****-****-****-1234",
                "timestamp": time.time()
            }
        )
    else:  # 15% chance of failure
        print(f"Payment failed for request {payment_request.request_id}.")
        return PaymentResponse(
            status="failed",
            message="خطا در ارتباط با دستگاه کارتخوان. لطفاً دوباره تلاش کنید.",
        )

# --- Main entry point to run the app ---
if __name__ == "__main__":
    print("Starting POS Simulator Server...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
