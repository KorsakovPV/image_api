from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework.schemas import get_schema_view

urlpatterns = [
    # ...
    # Use the `get_schema_view()` helper to add a `SchemaView` to project URLs.
    #   * `title` and `description` parameters are passed to `SchemaGenerator`.
    #   * Provide view name for use with `reverse()`.
    path('openapi/', get_schema_view(
        title="Your Project",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
    # ...
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('redoc/', TemplateView.as_view(template_name='redoc.html'),
         name='redoc'),
    path('api/', include('api.urls')),
]
