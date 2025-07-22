# locustfile.py
from locust import HttpUser, task, between
import random

# Sample messages (mix of types)
messages = [
    "Your OTP is 1234. Do not share it with anyone.",
    "Check out our sale at https://trip.com ",
    "You've won a prize! Claim now: https://fakewebsite.com ",
    "Your package with tracking ID 12345 has been shipped.",
    "Urgent: Verify your account at https://verify-now.online ",
    "Thank you for shopping with us!",
    "Reset your password now at https://get-rich-fast.biz "
]

class SMSUser(HttpUser):
    
    host = "http://localhost:8000"  # Adjust based on your FastAPI server
    wait_time = between(0.01, 0.1)  # Simulate rapid but staggered requests

    @task
    def check_sms(self):
        message = random.choice(messages)
        self.client.post(
            "/check_sms",
            json={"message": message},
            headers={"Content-Type": "application/json"}
        )
        
