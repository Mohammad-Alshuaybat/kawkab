import random


def distribute_questions(n, percentages):
  distribute_questions = {}
  total_percentage = sum(percentages.values())


  for key, percentage in percentages.items():
    distribute_questions[key] = int(n * (percentage / total_percentage)) if int(n * (percentage / total_percentage)) != 0 else 1

  while sum(distribute_questions.values()) != n:
    if sum(distribute_questions.values()) < n:
      distribute_questions[random.choice(list(percentages.keys()))] += 1
    else:
      distribute_questions[max(distribute_questions, key=distribute_questions.get)] -= 1

  return distribute_questions


print(distribute_questions(8, {'1': 0.2, '2': 0.2, '3': 0.6}))
print(distribute_questions(2, {'4': 0.4, '5': 0.1, '6': 0.5}))

print(distribute_questions(10, {'1': 1.6, '2': 1.6, '3': 4.8, '4': 0.8, '5': 0.2, '6': 1.0}))

print('********'*4)

print(distribute_questions(1, {'1': 0.2, '2': 0.2, '3': 0.6}))
print(distribute_questions(9, {'4': 0.4, '5': 0.1, '6': 0.5}))

print(distribute_questions(10, {'1': 0.2, '2': 0.2, '3': 0.6, '4': 3.6, '5': 0.9, '6': 4.5}))


# def lesson_module(module_ques, lesson_per):
#   modules_lessons = {}
#   lessons_ques = []
#
#   for module in module_ques.keys():
#     modules_lessons[module] = set(lesson_per.keys()).intersection(module.lesson_set.all())
#
#   for module, lessons in modules_lessons.items():
#     lessons_ques.append(distribute_questions(module_ques[module], {lesson: lesson_per[lesson] for lesson in lessons}))
#
#   return lessons_ques


# import time
# start = time.perf_counter()
# end = time.perf_counter()


#     starting_date = models.DateField(null=True, blank=True)
#     registration_info = models.OneToOneField('RegistrationInfo', db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
#     scholarship = models.BooleanField(null=True, blank=True)
#     @property
#     def average(self):
#         avg = self.certificate.aggregate(average=Avg(F('first')+F('second')+F('third')+F('final')))['average']
#         return avg


# general relation field
# from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
# content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
# object_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
# content_object = GenericForeignKey('content_type', 'object_id')


# add field for serializer
# status = serializers.SerializerMethodField('status_value')
#
# @staticmethod
# def status_value(obj):
#     return False


# order many to many field
# This way, when you query the authors and access their books, they will be ordered based on the order field of the BookAuthor model.
# class Book(models.Model):
#     name = models.CharField(max_length=100)
#
# class Author(models.Model):
#     name = models.CharField(max_length=100)
#     books = models.ManyToManyField(
#         Book,
#         through='BookAuthor',
#         through_defaults={'order': 0},
#     )
#
# class BookAuthor(models.Model):
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)
#     order = models.PositiveSmallIntegerField()
#
#     class Meta:
#         ordering = ['order']
