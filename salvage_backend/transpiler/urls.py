from django.urls import path
from .services.translator.translator import Transpiler
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def transpile_code(request):
    c_code = request.data.get('code', '')
    transpiler = Transpiler()
    rust_code = transpiler.transpile(c_code)
    return Response({'rust_code': rust_code})

urlpatterns = [
    path('transpile/', transpile_code, name='transpile'),
]