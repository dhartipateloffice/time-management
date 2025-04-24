from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Project, Task, TaskComment, User

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name','description']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','assignee','status','due_date','priority','tags']
        widgets = {'due_date': forms.DateInput(attrs={'type':'date'})}

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['comment']