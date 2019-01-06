from django.conf.urls import url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
]
