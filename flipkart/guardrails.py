import re
from utils.custom_exception import CustomException
from utils.logger import get_logger

class GuardRails:
    try:
        def validate_response(self,raw_output: str) -> str:
            # PII checks
            raw_output = re.sub(r"\b\d{10}\b", "[REDACTED]", raw_output)  # phone numbers
            raw_output = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED]", raw_output)

            # Harmful content filter
            harmful_keywords = ["suicide", "kill", "bomb", "attack"]
            if any(word in raw_output.lower() for word in harmful_keywords):
                raw_output = "Sorry, I cannot provide harmful content."

            # Length limit
            if len(raw_output) > 1000:
                raw_output = raw_output[:1000] + "That's the maximum information I can provide."

            return raw_output
    except Exception as e:
                get_logger("GuardRails").error("Error generating response: %s", str(e))
                raise CustomException("Failed to generate response", e)