from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from .models import Project, Task, TimeLog, ProjectMembership
from .forms import RegistrationForm, ProjectForm, TaskForm, TaskCommentForm
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView

# Authentication

def register(request):
    if request.method == 'POST':
        print("POST request received")  # Debug print
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug print
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            print("Form is invalid:", form.errors)  # Debug
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

class CustomLoginView(LoginView):
    def get_redirect_url(self):
        user = self.request.user

        if user.is_authenticated:
            # get the first ProjectMembership for this user
            membership = ProjectMembership.objects.filter(user=user).first()

            if membership:
                if membership.is_admin:
                    return reverse('project_overview', args=[membership.project.pk])
                else:
                    return reverse('dashboard')
            else:
                # no project at all
                return reverse('dashboard')

        return super().get_redirect_url()
    
def custom_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts/'))  # Redirect to login page after logout\

#Dashboard   
@login_required
def dashboard(request):
    tasks = Task.objects.filter(assignee=request.user).order_by('due_date')
    return render(request, 'dashboard.html', {'tasks': tasks})

#Projects
@login_required
def project_list(request):
    projects = request.user.projects.all()
    return render(request, 'project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            ProjectMembership.objects.create(user=request.user, project=project, is_admin=True)
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner:
        return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('project_overview', pk=pk)
    return render(request, 'project_form.html', {'form': form})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner:
        return HttpResponseForbidden()
    project.delete()
    return redirect('project_list')

@login_required
def project_invite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user != project.owner:
        return HttpResponseForbidden()

    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            ProjectMembership.objects.get_or_create(user=user, project=project)
        except User.DoesNotExist:
            # Send invite email
            send_mail(
                subject='You are invited to join a project',
                message=f"Hi,\n\nYou've been invited to join the project '{project.name}'.\nRegister at: http://127.0.0.1:8000/register/\n\nThanks!",
                from_email='admin@example.com',
                recipient_list=[email],
                fail_silently=False,
            )

    return redirect('project_overview', pk=pk)

@login_required
def project_overview(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user not in project.members.all():
        return HttpResponseForbidden()
    tasks = Task.objects.filter(project=project)
    return render(request, 'project_overview.html', {'project': project, 'tasks': tasks})

#tasks

@login_required
def task_create(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user not in project.members.all():
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_overview', pk=pk)
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form, 'project': project})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user not in task.project.members.all():
        return HttpResponseForbidden()
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect('task_detail', pk=pk)
    return render(request, 'task_form.html', {'form': form, 'project': task.project})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    if request.user != task.project.owner:
        return HttpResponseForbidden()
    task.delete()
    return redirect('project_overview', pk=project_pk)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user not in task.project.members.all():
        return HttpResponseForbidden()
    comment_form = TaskCommentForm()
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', pk=pk)
    return render(request, 'task_detail.html', {'task': task, 'comment_form': comment_form})

@login_required
def start_timer(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user not in task.project.members.all():
        return HttpResponseForbidden()
    TimeLog.objects.create(task=task, user=request.user)
    return redirect('task_detail', pk=pk)

@login_required
def stop_timer(request, pk):
    task = get_object_or_404(Task, pk=pk)
    log = TimeLog.objects.filter(task=task, user=request.user, end_time__isnull=True).last()
    if log:
        log.end_time = timezone.now()
        log.save()
    return redirect('task_detail', pk=pk)
