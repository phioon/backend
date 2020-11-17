from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def warmup():
    Response(status=status.HTTP_200_OK)
