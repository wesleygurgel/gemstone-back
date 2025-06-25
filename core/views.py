from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HealthCheckView(APIView):
    """
    A simple view to check if the API is running.
    """
    permission_classes = []  # No authentication required

    def get(self, request, format=None):
        return Response(
            {"status": "ok", "message": "API is running"},
            status=status.HTTP_200_OK
        )