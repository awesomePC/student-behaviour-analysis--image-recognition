from django.contrib import admin

from django.apps import apps

list_skip_fields = [{
    "model_name": "examcandidatephoto",
    "skip_fields": ["np_face",]
}]

# Register your models here.
app = apps.get_app_config('exam')
for model_name, model in app.models.items():
    model_admin = type(model_name + "Admin", (admin.ModelAdmin,), {})
    
    model_admin.list_per_page = 5 # No of records per page 
    
    has_blocked_fields = False
    for element in list_skip_fields:
        if model_name in element["model_name"].lower():
            has_blocked_fields = True
            skip_fields = element["skip_fields"]
            break

    if has_blocked_fields:
        model_admin.list_display = tuple([field.name for field in model._meta.fields  if field.name not in skip_fields])
    else:
        model_admin.list_display = model.admin_list_display if hasattr(model, 'admin_list_display') else tuple([field.name for field in model._meta.fields])
    
    model_admin.list_filter = model.admin_list_filter if hasattr(model, 'admin_list_filter') else model_admin.list_display
    model_admin.list_display_links = model.admin_list_display_links if hasattr(model, 'admin_list_display_links') else ()
    model_admin.list_editable = model.admin_list_editable if hasattr(model, 'admin_list_editable') else ()
    model_admin.search_fields = model.admin_search_fields if hasattr(model, 'admin_search_fields') else ()

    admin.site.register(model, model_admin)