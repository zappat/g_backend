"""
URL Mapping for the Gear Apis.
"""

from django.urls import path, include

from gear_hub import views

app_name = 'gear-hub'

GEAR_ITEMS_URL_PATTERN = [
    path('', views.GearItemListAPIView.as_view(), name='gear-items'),
    path('<str:pk>/', views.GearItemRetrieveAPIView.as_view(), name='gear-item'),
    path('create', views.GearItemCreateApiView.as_view(), name='gear-items-create'),
    path('update/<str:pk>/', views.GearItemUpdateApiView.as_view(), name='gear-items-update'),
    path('delete/<str:pk>/', views.GearItemDestroyAPIView.as_view(), name='gear-items-delete'),
    path('bulk-delete/<str:ids>/', views.GearItemBulkDestroyAPIView.as_view(), name='gear-item-bulk-delete'),
    path('<str:pk>/toggle-visibility/', views.GearItemToggleVisibilityAPIView.as_view(), name='gear-item-toggle-visibility'),
]

AVIALBLE_GEAR_ITEMS_URL_PATTERN = [
    path('', views.AvailableGearItemListAPIView.as_view(), name='available-gear-items'),
]

GEAR_ITEMS_PICTURE_URL_PATTERN = [
    path('create', views.GearItemPictureCreateApiView.as_view(), name='gear-items-picture-create'),
    path('update/<str:pk>/', views.GearItemPictureUpdateApiView.as_view(), name='gear-items-picture-update'),
    path('delete/<str:pk>/', views.GearItemPictureDestroyAPIView.as_view(), name='gear-items-picture-delete'),
]


FAVORITE_URL_PATTERN = [
    path('create/', views.AddFavoriteCreateApiView.as_view(), name='create-favorite'),
    path('list/', views.ListFavoriteApiView.as_view(), name='list-favorite'),
    path('delete/<str:gear_item_id>/', views.AddFavoriteDestroyAPIView.as_view(), name='delete-favorite'),
]

GEAR_CATEGORIES_URL_PATTERN = [
    path('', views.GearCategoriesListAPIView.as_view(), name='gear-categories'),
]


# Only keep relevant URL patterns for existing views
urlpatterns = [
    path('gear-items-picture/', include(GEAR_ITEMS_PICTURE_URL_PATTERN)),
    path('gear-items/', include(GEAR_ITEMS_URL_PATTERN)),
    path('gear-categories/', include(GEAR_CATEGORIES_URL_PATTERN)),
    path('add-favorite/', include(FAVORITE_URL_PATTERN)),
    path('available/', include(AVIALBLE_GEAR_ITEMS_URL_PATTERN)),
]
