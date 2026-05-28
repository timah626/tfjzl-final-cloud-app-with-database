from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# <HINT> Register QuestionInline and ChoiceInline classes here

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    # We add QuestionInline here so questions show up inside the course page
    inlines = [LessonInline, QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


# Create QuestionAdmin class to manage questions and their choice items inline
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text', 'course', 'grade']


# <HINT> Register Question and Choice models here
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)

# Register the remaining new models so they show up on the admin site
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)