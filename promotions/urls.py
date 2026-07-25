from django.urls import path

from . import views

app_name = "promotions"

urlpatterns = [
    path("boost/<int:pk>/", views.BoostListingView.as_view(), name="boost"),
    path("boost/odenis/<int:pk>/", views.MockPaymentView.as_view(), name="mock_payment"),
    path("boost/ugur/<int:pk>/", views.PaymentSuccessView.as_view(), name="payment_success"),
]
