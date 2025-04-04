from rest_framework.routers import SimpleRouter

from credrails.apps.reconciliation import views

router = SimpleRouter()
router.register(
    "reconciliation",
    views.ReconciliationViewSet,
    basename="reconciliation",
)

app_name = "reconciliation"
urlpatterns = router.urls
