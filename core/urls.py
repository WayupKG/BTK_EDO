from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include("home.urls")),
    path('doc/', include("document.urls")),
    path('employee/', include("employee.urls")),
    path('notification/', include("notification.urls")),
    path('check-list/', include("check_list.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += i18n_patterns(path('__debug__/', include(debug_toolbar.urls)),)


handler404 = 'core.errors.custom_page_not_found_view'
handler500 = 'core.errors.custom_error_view'
handler403 = 'core.errors.custom_permission_denied_view'
handler400 = 'core.errors.custom_bad_request_view'