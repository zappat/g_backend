from django.contrib import admin
from core.models import User
from user.models import Organization, IdentityVerification, MerchantProfile, RenterProfile, AdditionalEmail, AdditionalPhoneNumber

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(IdentityVerification)
admin.site.register(MerchantProfile)
admin.site.register(RenterProfile)
admin.site.register(AdditionalEmail)
admin.site.register(AdditionalPhoneNumber)