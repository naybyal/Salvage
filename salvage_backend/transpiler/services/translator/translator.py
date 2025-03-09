import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Transpiler:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("Missing GEMINI_API_KEY in environment variables")
            raise ValueError("API key not configured")

        try:
            genai.configure(api_key=self.api_key)

            # Verify API connectivity
            models = genai.list_models()
            if not any(m.name == 'models/gemini-1.5-flash-latest' for m in models):
                logger.error("Model not available. Available models: %s", [m.name for m in models])
                raise ValueError("Requested model not available")

            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

        except Exception as e:
            logger.error("Gemini initialization failed: %s", str(e))
            raise

    def transpile(self, c_code: str) -> str:
        try:
            prompt = f"""Translate this C code to Rust:
            {c_code}

            Requirements:
            1. Maintain original functionality
            2. Use Rust idioms
            3. Return only code with no comments
            """
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error("Transpilation failed: %s", str(e))
            return f"// Transpilation Error: {str(e)}"