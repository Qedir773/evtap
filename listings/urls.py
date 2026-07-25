from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("elanlar/", views.ListingSearchView.as_view(), name="listing_search"),
    path("kateqoriya/<slug:slug>/", views.CategoryListView.as_view(), name="category_list"),
    path("elan/yeni/", views.ListingCreateView.as_view(), name="listing_create"),
    path("elan/<int:pk>/redakte/", views.ListingUpdateView.as_view(), name="listing_update"),
    path("elan/<slug:slug>-<int:pk>/", views.ListingDetailView.as_view(), name="listing_detail"),
    path("hesabim/elanlarim/", views.MyListingsView.as_view(), name="my_listings"),
    path("sevimliler/", views.FavoritesListView.as_view(), name="favorites"),
    path("sevimli/<int:pk>/toggle/", views.FavoriteToggleView.as_view(), name="favorite_toggle"),
]
