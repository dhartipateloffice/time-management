from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Project)
admin.site.register(ProjectMembership)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(TimeLog)
