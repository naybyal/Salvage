import json
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.preprocessor.preprocess import preprocess_c_file
from .services.preprocessor.segmentation import extract_symbols, build_dependency_graph, segment_code
from .services.preprocessor.metadata import generate_metadata
from .services.translator.translator import Translator
from .utils.file_utils import write_rust_file, combine_rust_segments

class TranspileView(APIView):
    def post(self, request):
        source_code = request.data.get("sourceCode")
        file_name = request.data.get("fileName")

        if not source_code or not file_name:
            return Response(
                {"error": "sourceCode and fileName are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Preprocess the C code
        preprocessed_file = preprocess_c_file(source_code)

        # Extract symbols and segment the code
        symbols = extract_symbols(preprocessed_file)
        dependency_graph = build_dependency_graph(symbols)
        segment_files = segment_code(preprocessed_file, symbols)

        # Generate metadata
        metadata_file = generate_metadata(symbols, segment_files)

        # Translate each segment to Rust
        translator = Translator()
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        for segment in metadata["segments"]:
            segment_id = segment["segment_id"]
            with open(segment["file"], "r") as f:
                c_code = f.read()
                rust_code = translator.translate(c_code, segment_id)
                write_rust_file(segment_id, rust_code, metadata)

        # Combine Rust segments into one file
        final_rust_file = os.path.join(os.path.dirname(metadata_file), "output.rs")
        combine_rust_segments(metadata_file, final_rust_file)

        # Read the final Rust code
        with open(final_rust_file, "r") as f:
            rust_code = f.read()

        return Response({"rustCode": rust_code}, status=status.HTTP_200_OK)