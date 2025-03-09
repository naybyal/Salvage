import json
import os
import tempfile
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.preprocessor.preprocess import preprocess_c_file
from .services.preprocessor.segmentation import extract_symbols, build_dependency_graph, segment_code
from .services.preprocessor.metadata import generate_metadata
from .services.translator.translator import Translator
from .utils.file_utils import write_rust_file, combine_rust_segments

logger = logging.getLogger(__name__)


class TranspileView(APIView):
    def post(self, request):
        try:
            source_code = request.data.get("sourceCode")
            file_name = request.data.get("fileName")

            if not source_code or not file_name:
                return Response(
                    {"error": "Both sourceCode and fileName are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create temporary workspace
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save source code to temporary file
                input_path = os.path.join(temp_dir, "input.c")
                with open(input_path, "w") as f:
                    f.write(source_code)

                # Preprocess the C code
                preprocessed_file = preprocess_c_file(input_path, temp_dir)

                # Extract symbols and segment the code
                symbols = extract_symbols(preprocessed_file)
                dependency_graph = build_dependency_graph(symbols)
                segment_files = segment_code(preprocessed_file, symbols, temp_dir)

                # Generate metadata
                metadata_file = generate_metadata(symbols, segment_files, temp_dir)

                # Translate each segment to Rust
                translator = Translator()
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)

                for segment in metadata["segments"]:
                    segment_id = segment["segment_id"]
                    with open(segment["file"], "r") as f:
                        c_code = f.read()
                        rust_code = translator.transpile(c_code)
                        write_rust_file(segment_id, rust_code, metadata, temp_dir)

                # Combine Rust segments
                final_rust_file = os.path.join(temp_dir, "output.rs")
                combine_rust_segments(metadata_file, final_rust_file)

                # Read and return result
                with open(final_rust_file, "r") as f:
                    rust_code = f.read()

                return Response({"rustCode": rust_code}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Transpilation failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Transpilation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )