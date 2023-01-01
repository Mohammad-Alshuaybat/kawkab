from django.db import models
import uuid

from school.cdn.backends import MediaRootS3Boto3Storage
from user.models import User


class Subject(models.Model):
    semester_choices = (
        (1, 'الفصل الأول'),
        (2, 'الفصل الثاني'),
    )
    classification_choices = (
        (0, 'مادة علمية'),
        (1, 'مادة أدبية'),
    )

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=30, null=True, blank=True)
    semester = models.IntegerField(choices=semester_choices, null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    classification = models.IntegerField(choices=classification_choices, null=True, blank=True)

    def __str__(self):
        return f'{self.name} ف{self.semester} --{self.grade}'


class Skill(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True)  # symmetrical even if I follow you, you can don't follow me
    subject = models.ForeignKey(Subject, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class SkillInst(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    level = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    skill = models.ForeignKey(Skill, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.skill} - {self.user}'


class Module(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    subject = models.ForeignKey(Subject, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    module = models.ForeignKey(Module, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    skills = models.ManyToManyField(Skill, symmetrical=False, blank=True)  # symmetrical even if I follow you, you can don't follow me

    def __str__(self):
        return self.name


class Quiz(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    subject = models.ForeignKey(Subject, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    question = models.ManyToManyField('Question', blank=True)     # many to many

    def __str__(self):
        return self.name


class Question(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    body = models.TextField(null=True, blank=True)
    correct_answer = models.TextField(null=True, blank=True)
    skills = models.ManyToManyField('Skill', blank=True)     # many to many
    generalSkills = models.TextField(null=True, blank=True)
    image = models.ImageField(storage=MediaRootS3Boto3Storage(), null=True, blank=True)

    def __str__(self):
        return self.body


class Choice(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    body = models.TextField(null=True, blank=True)
    question = models.ForeignKey(Question, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    info = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'Q:{self.question}  choice:{self.body}'


class QuizAnswer(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    quiz = models.ForeignKey(Quiz, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.user} - {self.quiz}'


class QuestionAnswer(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    body = models.TextField(null=True, blank=True)
    correct = models.BooleanField(null=True, blank=True)
    question = models.ForeignKey(Question, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
    quiz_answer = models.ForeignKey(QuizAnswer, db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'Q:{self.question}  A:{self.body}'


# class AcademicYear(models.Model):
#     semester_choices = (
#         ('first', 'first semester'),
#         ('second', 'second semester')
#     )
#
#     id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
#     name = models.CharField(max_length=12, null=True, blank=True)
#     starting_date = models.DateField(null=True, blank=True)
#     name = models.IntegerField(null=True, blank=True)
#     school = models.ForeignKey('School', db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
#     semester = models.CharField(max_length=50, choices=semester_choices, null=True, blank=True)
#     students_set = models.ManyToManyField('Student', blank=True)     # many to many
#     registration_info = models.OneToOneField('RegistrationInfo', db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
#     scholarship = models.BooleanField(null=True, blank=True)
#     body = models.TextField(null=True, blank=True)
#     mark = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
#
#     def level(self):
#         return SkillInst.objects.get(skill=self).level  # TODO: check
#
#     # @property
#     # def average(self):
#     #     avg = self.certificate.aggregate(average=Avg(F('first')+F('second')+F('third')+F('final')))['average']
#     #     return avg
#
#     @property
#     def subject_grade(self):
#         total = self.first + self.second + self.third + self.final
#         return total
#
#     def __str__(self):
#         return f'{self.certificate} - {self.subject}'
