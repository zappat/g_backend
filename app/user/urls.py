"""
URL mapping for the user APIs
"""

from django.urls import path, include

from user import views

app_name = 'user'

ORGANIZATION_URL_PATTERNS = [
    path(
        'create/',
        views.OrganizationCreateAPIView.as_view(),
        name='create-organization'
    ),
    path(
        '<str:pk>/',
        views.OrganizationRetrieveUpdateAPIView.as_view(),
        name='create-retrive-update'
    ),
    path(
        'delete/<str:pk>/',
        views.OrganizationDeleteAPIView.as_view(),
        name='delete'
    ),
]

MERCHANT_PROFILE_URL_PATTERNS = [
    path(
        '',
        views.MerchantProfileRetrieveUpdateAPIView.as_view(),
        name='merchant-create-retrive-update'
    ),
    path(
        'delete/<str:pk>/',
        views.MerchantProfileDeleteAPIView.as_view(),
        name='merchant-delete'
    )
]

RENTER_PROFILE_URL_PATTERNS = [
    path(
        '',
        views.RenterProfileRetrieveUpdateAPIView.as_view(),
        name='renter-create-retrive-update'
    ),
    path(
        'delete/<str:pk>/',
        views.RenterProfileDeleteAPIView.as_view(),
        name='renter-delete'
    )
]

ADDITIONAL_URL_PATTERN = [
    path(
        "additional-email/create/",
        views.AdditionalEmailCreateAPIView.as_view(),
        name="create-additional-email"
    ),
    path(
        "additional-phone-number/create/",
        views.AdditionalPhoneNumberCreateAPIView.as_view(),
        name="create-additional-phone-number"
    ),
    path(
        "additional-info-list/",
        views.AdditionalInfoRetrieveAPIView.as_view(),
        name="additional-info-list"
    ),
    path(
        "additional-email/<uuid:id>/update/",
        views.AdditionalEmailUpdateAPIView.as_view(),
        name="additional-email-update"
    ),
    path(
        "additional-phone-number/<uuid:id>/update/",
        views.AdditionalPhoneNumberUpdateAPIView.as_view(),
        name="additional-phone-number-update"
    )

]

IDENTITY_VERFICATION_URL_PATTERNS = [
    path('', views.IdentityVerificationCreateAPIView.as_view(),
         name='identity-verification'),
    path(
        '<str:pk>/',
        views.IdentityVerificationRetrieveUpdateAPIView.as_view(),
        name='retrive-update'
    ),
    path(
        'delete/<str:pk>/',
        views.IdentityVerificationDeleteAPIView.as_view(),
        name='delete'
    ),
]

USER_URL_PATTERNS = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('delete/<int:pk>/', views.UserDeleteApiView.as_view(), name='delete'),
]

urlpatterns = [
    path('organization/', include(ORGANIZATION_URL_PATTERNS)),
    path('merchant-profile/', include(MERCHANT_PROFILE_URL_PATTERNS)),
    path('renter-profile/', include(RENTER_PROFILE_URL_PATTERNS)),
    path('identity-verification/', include(IDENTITY_VERFICATION_URL_PATTERNS)),
    path('additional-info/', include(ADDITIONAL_URL_PATTERN)),
    path('', include(USER_URL_PATTERNS)),
]
