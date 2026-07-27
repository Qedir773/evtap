from django.urls import path

from . import views

app_name = "tokens"

urlpatterns = [
    path("token/redeem/", views.RedeemPromoCodeView.as_view(), name="redeem_promocode"),
    path("elan/<int:pk>/bump/", views.BumpListingView.as_view(), name="bump"),
    path("elan/<int:pk>/vip/", views.ActivateVipView.as_view(), name="activate_vip"),
    path("elan/<int:pk>/urgent/", views.ActivateUrgentView.as_view(), name="activate_urgent"),
]
