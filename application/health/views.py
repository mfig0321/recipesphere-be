from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

import os


class HealthCheckEndpoint(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        msg = {
            'version': '1.1a',
            'test': 'Test repo path changes'
        }
        return Response(msg, status=HTTP_200_OK)

