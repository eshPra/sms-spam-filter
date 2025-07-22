from src.filter_engine import filter_message

# Test cases
test_messages = [
    "Your OTP is 123456. Do not share it with anyone.",  # Should be whitelisted
    "Check out our sale at https://trip.com ",            # Whitelisted domain
    "You've won! Claim prize at https://fakewebsite.com ", # Spam
    "Your package has been shipped.",                    # Whitelisted phrase
    "Urgent: Verify now at https://verify-now.online ",   # Spam
    ""                                                   # Empty → blocked
]

for msg in test_messages:
    result = filter_message(msg)
    print(f"\nMessage: {msg}")
    print(f"Result: {result}")