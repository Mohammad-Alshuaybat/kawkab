from datetime import date

from rest_framework.decorators import api_view
from rest_framework.response import Response

from quiz.models import Subject
from user.models import Quote, Advertisement, DailyTask
from user.serializers import DailyTaskSerializer, AdvertisementSerializer
from user.utils import signup, login, check_user, get_user


@api_view(['POST'])
def sign_up(request):
    # 0-->account_created  1-->account_already_exit  2-->email_is_used  3-->phone_num_is_used
    data = request.data
    return Response(signup(data))
# {
#     "email": "malek315@gmail.com",
#     "phone": "0786636678",
#     "password": "password",
#     "firstName": "malek",
#     "lastName": "aldebsi",
#     "section": "s",
#     "grade": 8
# }


@api_view(['POST'])
def log_in(request):
    # 0-->logged_in  1-->password_are_wrong  2-->email_or_phone_not_exist
    data = request.data
    return Response(login(data))
# {
#     "email": "malek315@gmail.com",
#     "password": "password"
# }
# or
# {
#     "phone": "0786636678",
#     "password": "password"
# }


@api_view(['POST'])
def dashboard(request):
    data = request.data

    if check_user(data):
        user = get_user(data)

        quote = Quote.objects.order_by('creationDate').first().image.url

        _advertisements = Advertisement.objects.filter(active=True)
        advertisements_serializer = AdvertisementSerializer(_advertisements, many=True)

        # _advertisements = Advertisement.objects.order_by('creationDate').filter(active=True)
        # advertisements = []
        # for advertisement in _advertisements:
        #     advertisements.append(advertisement.image.url)

        today_date = date.today()
        formated_date = today_date.strftime("%d-%m-%Y")

        tasks = DailyTask.objects.filter(user=user, date=today_date)
        task_serializer = DailyTaskSerializer(tasks, many=True)

        return Response({'user_name': user.firstName, 'quote': quote, 'advertisements': advertisements_serializer.data,
                         'today_date': formated_date, 'tasks': task_serializer.data})
    else:
        return Response(0)


@api_view(['POST'])
def edit_tasks(request):
    data = request.data
    subject_id = data.pop('subject_id', None)
    tasks = data.pop('tasks', None)

    if check_user(data):
        user = get_user(data)
        subject = Subject.objects.get(id=subject_id)
        today_date = date.today()

        for task in tasks:
            daily_task, _ = DailyTask.objects.get_or_create(user=user, subject=subject, date=today_date)
            daily_task.task = task
            daily_task.save()

        return Response()
    else:
        return Response(0)

