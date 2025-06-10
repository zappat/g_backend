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
]

AVIALBLE_GEAR_ITEMS_URL_PATTERN = [
    path('', views.AvailableGearItemListAPIView.as_view(), name='available-gear-items'),
]

GEAR_ITEMS_PICTURE_URL_PATTERN = [
    path('create', views.GearItemPictureCreateApiView.as_view(), name='gear-items-picture-create'),
    path('update/<str:pk>/', views.GearItemPictureUpdateApiView.as_view(), name='gear-items-picture-update'),
    path('delete/<str:pk>/', views.GearItemPictureDestroyAPIView.as_view(), name='gear-items-picture-delete'),
]

REVIEWS_URL_PATTERN = [
    path('<str:gear_item>/', views.ReviewListApiView.as_view(), name='reviews'),
    path('create', views.ReviewCreateApiView.as_view(), name='reviews-create'),
    path('delete/<str:pk>/', views.ReviewDeleteApiView.as_view(), name='reviews-delete'),
]

FAVORITE_URL_PATTERN = [
    path('create/', views.AddFavoriteCreateApiView.as_view(), name='create-favorite'),
    path('list/', views.ListFavoriteApiView.as_view(), name='list-favorite'),
    path('delete/<str:gear_item_id>/', views.AddFavoriteDestroyAPIView.as_view(), name='delete-favorite'),
]

BOOKING_URL_PATTERN = [
    path('create/', views.BookingCreateApiView.as_view(), name='booking-create'),
    path('<str:pk>/', views.BookingRetrieveUpdateApiView.as_view(), name='booking-retrive-update'),
    path('delete/<str:pk>/', views.BookingDeleteApiView.as_view(), name='booking-delete'),
    path('', views.BookingListApiView.as_view(), name='booking-list'),
]

RESERVATIONS_URL_PATTERN = [
    path('', views.ReservationListApiView.as_view(), name='booking-reservation-list'),
    path('<uuid:booking_id>/confirm/', views.BookingStatusUpdateAPIView.as_view(), name='booking-reservation-confirm' )
]

GEAR_CATEGORIES_URL_PATTERN = [
    path('', views.GearCategoriesListAPIView.as_view(), name='gear-categories'),
]

GEAR_ITEMS_RENT_URL_PATTERN = [
    path('', views.GearItemRentListCreateView.as_view(), name='gearitemrent-list-create'),
    path('<str:pk>/', views.GearItemRentRetrieveUpdateDestroyView.as_view(), name='gearitemrent-detail'),
]

CART_URL_PATTERN = [
    path('create/', views.CartCreateAPIView.as_view(), name='create-cart'),
    path('<uuid:id>/retrieve/', views.CartRetrieveAPIView.as_view(), name='retrieve-cart-item'),
    path('<uuid:id>/update/', views.CartUpdateAPIView.as_view(), name='update-cart-item'),
    path('list/', views.CartListAPIView.as_view(), name='cart-list'),
    path('<uuid:id>/delete/', views.CartDeleteAPIView.as_view(), name='delete-cart-item'),
    path('delete/all/', views.CartDeleteAllAPIView.as_view(), name='delete-all-cart-item'),

]


urlpatterns = [
    path('gear-items-picture/', include(GEAR_ITEMS_PICTURE_URL_PATTERN)),
    path('gear-items/', include(GEAR_ITEMS_URL_PATTERN)),
    path('gear-categories/', include(GEAR_CATEGORIES_URL_PATTERN)),
    path('add-favorite/', include(FAVORITE_URL_PATTERN)),
    path('booking/', include(BOOKING_URL_PATTERN)),
    path('gear-items-rent/', include(GEAR_ITEMS_RENT_URL_PATTERN)),
    path('reviews/', include(REVIEWS_URL_PATTERN)),
    path('bookings/reservations/', include(RESERVATIONS_URL_PATTERN)),
    path('available/', include(AVIALBLE_GEAR_ITEMS_URL_PATTERN)),
    path('cart/', include(CART_URL_PATTERN))
]
