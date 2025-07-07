from django.contrib import admin
from core.models import User
from user.models import IdentityVerification, MerchantProfile, RenterProfile

admin.site.register(User)
admin.site.register(IdentityVerification)
admin.site.register(MerchantProfile)
admin.site.register(RenterProfile)