"""
URL mapping for the user APIs
"""

from django.urls import path, include

from user import views

app_name = 'user'

MERCHANT_PROFILE_URL_PATTERNS = [
    # Fixed paths first
    path('get-all-merchants/', views.GetAllMerchantsAPIView.as_view(), name='get-all-merchants'),
    path('by-merchant-ids/', views.MerchantsByMerchantIdsAPIView.as_view(), name='merchants-by-merchant-ids'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='merchant-pro-stripe-webhook'),
    path(
        'delete/<str:pk>/',
        views.MerchantProfileDeleteAPIView.as_view(),
        name='merchant-delete'
    ),
    
    # Base path
    path(
        '',
        views.MerchantProfileRetrieveUpdateAPIView.as_view(),
        name='merchant-create-retrive-update'
    ),
    
    # Dynamic paths last
    path(
        '<int:pk>/',
        views.MerchantProfileDetailAPIView.as_view(),
        name='merchant-profile-detail'
    ),
    path(
        '<str:email>/',
        views.MerchantProfileByEmailView.as_view(),
        name='merchant-profile-by-email'
    ),
]

RENTER_PROFILE_URL_PATTERNS = [
    # Fixed paths first
    path('get-all-renters/', views.GetAllRentersAPIView.as_view(), name='get-all-renters'),
    path(
        'delete/<str:pk>/',
        views.RenterProfileDeleteAPIView.as_view(),
        name='renter-delete'
    ),
    
    # Base path
    path(
        '',
        views.RenterProfileRetrieveUpdateAPIView.as_view(),
        name='renter-create-retrive-update'
    ),
    
    # Dynamic paths last
    path(
        '<int:pk>/',
        views.RenterProfileDetailAPIView.as_view(),
        name='renter-profile-detail'
    ),
    path(
        '<str:email>/',
        views.RenterProfileByEmailView.as_view(),
        name='renter-profile-by-email'
    ),
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
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification-code/', views.ResendVerificationCodeView.as_view(), name='resend-verification-code'),
    path('update/<str:email>/', views.UpdateUserByEmailView.as_view(), name='update-by-email'),
]

EQUIPMENT_CATEGORY_URL_PATTERNS = [
    path('', views.EquipmentCategoryListAPIView.as_view(), name='equipment-categories'),
    path('<int:pk>/', views.EquipmentCategoryDetailAPIView.as_view(), name='equipment-category-detail'),
]

urlpatterns = [
    path('merchant-profile/', include(MERCHANT_PROFILE_URL_PATTERNS)),
    path('renter-profile/', include(RENTER_PROFILE_URL_PATTERNS)),
    path('identity-verification/', include(IDENTITY_VERFICATION_URL_PATTERNS)),
    path('equipment-categories/', include(EQUIPMENT_CATEGORY_URL_PATTERNS)),
    path('', include(USER_URL_PATTERNS)),
]
