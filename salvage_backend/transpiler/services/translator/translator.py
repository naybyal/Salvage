import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class Transpiler:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def transpile(self, c_code: str) -> str:
        try:
            prompt = f"""Translate this C code to Rust:
            {c_code}

            Requirements:
            1. Maintain original functionality
            2. Use Rust idioms
            3. Add proper error handling
            4. No comments/explanations
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"// Transpilation Error: {str(e)}"