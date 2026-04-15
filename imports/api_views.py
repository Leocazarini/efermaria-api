import logging

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FileImportSerializer
from .services import import_from_file

logger = logging.getLogger('imports.api_views')


class FileImportView(APIView):
    """
    POST /api/v1/imports/file/

    Importa alunos ou funcionários a partir de um arquivo CSV ou XLSX.
    Requer is_staff=True (IsAdminUser).
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = FileImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entity_type = serializer.validated_data['entity_type']
        file = serializer.validated_data['file']

        try:
            log = import_from_file(file, entity_type, request.user)
        except ValueError as exc:
            logger.warning(f"Importação rejeitada: {exc}")
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(
            f"Importação concluída via API — {entity_type}, "
            f"criados={log.created_count}, atualizados={log.updated_count}, "
            f"erros={log.error_count}, usuário={request.user}"
        )

        return Response(
            {
                'import_id':  log.id,
                'entity_type': log.entity_type,
                'total_rows':  log.total_rows,
                'created':     log.created_count,
                'updated':     log.updated_count,
                'errors':      log.errors,
            },
            status=status.HTTP_200_OK,
        )


class ExternalSyncView(APIView):
    """
    POST /api/v1/imports/sync/

    Reservado para integração futura com API externa (TOTVS RM ou similar).
    Retorna 501 Not Implemented enquanto não implementado.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        return Response(
            {'detail': 'Integração com API externa não implementada.'},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
