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
            self._verify_model()
            self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        except Exception as e:
            logger.error("Initialization failed: %s", str(e))
            raise

    def _verify_model(self):
        """Verify model availability and capabilities"""
        models = genai.list_models()
        if not any(m.name == "models/gemini-1.5-flash-latest" for m in models):
            available_models = [m.name for m in models]
            logger.error("Requested model not available. Available models: %s", available_models)
            raise ValueError(f"Model not found. Available models: {available_models}")

    def transpile(self, c_code: str) -> str:
        """Convert C code to safe Rust code"""
        try:
            if not c_code.strip():
                return "// Error: Empty input code"

            prompt = self._create_prompt(c_code)
            response = self.model.generate_content(prompt)
            return self._validate_output(response.text)

        except Exception as e:
            logger.error("Transpilation failed: %s", str(e))
            return f"// Transpilation Error: {str(e)}"

    def _create_prompt(self, c_code: str) -> str:
        """Constructs a strict prompt enforcing safety in Rust transpilation"""
        return f"""Convert the following C code to Rust, ensuring complete safety:

        {c_code}

        STRICT REQUIREMENTS:
        - Maintain **all functionality** of the original C code.
        - Use **Rust's ownership model** to handle memory safely.
        - **NO UNSAFE BLOCKS OR RAW POINTERS.** (e.g., `unsafe {{ }}` is forbidden)
        - Replace manual memory allocation (`malloc`, `free`) with **Rust's `Box`, `Vec`, or Rc/Arc` as appropriate.
        - Use **Result, Option, or meaningful error handling** instead of returning `NULL` or `-1`.
        - Avoid **manual memory management**, favor **RAII principles**.
        - Use **borrowed references (`&T`, `&mut T`) when applicable** instead of raw pointers (`*mut T`, `*const T`).
        - Convert loops (`for`, `while`) idiomatically, using **iterators instead of indexed loops** where appropriate.
        - Use **Rust's standard library features** (e.g., `String`, `Vec<T>`, `HashMap`) instead of C-style arrays and manual memory allocation.
        - Ensure **thread safety** if applicable by using **Arc, Mutex, or RwLock** where necessary.
        - NO extra comments or explanations in the output.
        - Output **only** the Rust code.

        ### BAD EXAMPLES (REJECT):
        - Usage of `unsafe {{ ... }}`.
        - Raw pointer manipulation (`*mut`, `*const`).
        - Manual memory allocation (`std::alloc::alloc`, `std::alloc::dealloc`).
        - Null pointer handling (`std::ptr::null_mut()`).

        ### GOOD EXAMPLES:
        - Using `Box::new(...)` instead of `malloc/free`.
        - Using `Vec<T>` instead of C-style arrays.
        - Using `Option<T>` instead of `NULL`.
        - Using `Result<T, E>` for proper error handling.

        **STRICTLY FOLLOW THESE RULES. Any deviation will result in incorrect output.**"""

    def _validate_output(self, rust_code: str) -> str:
        """Validate generated code for unsafe keywords"""
        validation_checks = [
            ("unsafe", "Unsafe keyword detected"),
            ("unsafe ", "Unsafe blocks detected"),
            ("unsafe\t", "Unsafe keyword with tab"),
            ("unsafe\n", "Unsafe keyword with newline"),
        ]

        for keyword, message in validation_checks:
            if keyword in rust_code:
                logger.warning("Safety violation: %s", message)
                return f"// Safety Error: {message}\n// Please try different input code"

        return rust_code