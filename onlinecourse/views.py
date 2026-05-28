from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id
#def submit(request, course_id):


# An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
   submitted_anwsers = []
   for key in request.POST:
       if key.startswith('choice'):
           value = request.POST[key]
           choice_id = int(value)
           submitted_anwsers.append(choice_id)
   return submitted_anwsers

# <HINT> Create a submit view to create an exam submission record for a course enrollment
def submit(request, course_id):
    if not request.user.is_authenticated:
        return redirect('onlinecourse:login')
        
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        # Get the associated enrollment object created when the user enrolled the course
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        # Create a submission object referring to the enrollment
        submission = Submission.objects.create(enrollment=enrollment)
        
        # Collect the selected choices from exam form using the modified helper logic
        selected_ids = []
        for key in request.POST:
            if key.startswith('choice_'):
                # Since checkboxes share the same name per question, grab the list of selected options
                choice_list = request.POST.getlist(key)
                selected_ids.extend([int(uid) for uid in choice_list])
        
        # Add each selected choice object to the submission object if any were checked
        if selected_ids:
            submission.choices.set(selected_ids)
            submission.save()
            
        # Redirect to show_exam_result with the course id and submission id
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
        
    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


# Keeping the starter method footprint intact 
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice_'):
            choices = request.POST.getlist(key)
            submitted_answers.extend([int(c_id) for c_id in choices])
    return submitted_answers


# <HINT> Create an exam result view to check if learner passed exam and show their question results
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Calculate the total score and earned score
    total_score = 0
    earned_score = 0
    
    for question in course.question_set.all():
        total_score += question.grade
        # Filter the selected choice ids for this specific question
        selected_ids = submission.choices.filter(question=question).values_list('id', flat=True)
        # Use our model method to check if answer set matches requirements
        if question.is_get_score(selected_ids):
            earned_score += question.grade
            
    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'earned_score': earned_score
    }
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


