from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import response, viewsets, parsers, renderers, mixins
from rest_framework.decorators import action
from rest_framework_csv.renderers import CSVRenderer

from credrails.apps.reconciliation.models import Reconciliation
from credrails.apps.reconciliation.serializers import ReconciliationSerializer


class ReconciliationWebhookViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        message = request.data["Message"]
        upload_id = message["details"]["upload_id"]
        reconciliation: Reconciliation = get_object_or_404(Reconciliation, pk=upload_id)
        reconciliation.status = message["status"]
        reconciliation.save(update_fields=["status"])
        return response.Response()


class ReconciliationViewSet(viewsets.GenericViewSet):
    authentication_classes = []
    serializer_class = ReconciliationSerializer
    parser_classes = [parsers.MultiPartParser]
    renderer_classes = [
        renderers.JSONRenderer,
        renderers.TemplateHTMLRenderer,
        renderers.BrowsableAPIRenderer,
        CSVRenderer,
    ]

    @extend_schema(summary="Reconcile", description="Reconcile `source` and `target` CSV files.")
    @action(methods=["POST", "GET"], detail=False, url_path="reconcile")
    def reconcile(self, request, *args, **kwargs):
        reports = {}
        render_html = request.accepted_renderer.format == "html"
        if request.method != "POST":
            serializer = self.get_serializer()
        else:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=not render_html):
                reports = serializer.data

        data = (
            {
                "reports": reports,
                "serializer": serializer,
            }
            if render_html
            else reports
        )
        return response.Response(data=data, template_name="reconciliation/reconcile.html")
