from django.urls import path
from .web_views import receipt_html_view, admin_receipt_preview_view

urlpatterns = [
    path("receipt/<uuid:token>/", receipt_html_view, name="receipt-html"),
    path("admin/transactions/<int:transaction_id>/receipt-preview/", admin_receipt_preview_view, name="admin-receipt-preview-web"),
]
