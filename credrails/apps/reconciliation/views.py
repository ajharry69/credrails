from drf_spectacular.utils import extend_schema
from rest_framework import response, viewsets, parsers
from rest_framework.decorators import action

from credrails.apps.reconciliation.serializers import ReconciliationSerializer


class ReconciliationViewSet(viewsets.GenericViewSet):
    authentication_classes = []
    parser_classes = [parsers.MultiPartParser]
    serializer_class = ReconciliationSerializer

    @extend_schema(summary="Reconcile", description="Reconcile `source` and `target` CSV files.")
    @action(methods=["POST"], detail=False, url_path="reconcile")
    def reconcile(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
