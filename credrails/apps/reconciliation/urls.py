from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from credrails.apps.reconciliation import views

router = SimpleRouter()
router.register(
    "reconciliation",
    views.ReconciliationViewSet,
    basename="reconciliation",
)

app_name = "reconciliation"
urlpatterns = format_suffix_patterns(
    urlpatterns=router.urls,
    allowed=["json", "html", "csv", "api"],
)
