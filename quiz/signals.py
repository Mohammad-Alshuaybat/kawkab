from django.db.models.signals import post_save, post_delete
from .models import UserMultipleChoiceAnswer, UserAnswer, UserMultiSectionAnswer, UserFinalAnswer


def create_user_multiple_choice_answer(sender, instance, created, **kwargs):  # sender: which model  instance: which project or profile or etc in the model  created: is the update was create new instance
    if created:
        answer = instance.usermultiplechoiceanswer
        question = answer.question.multiplechoicequestion
        answers_num = UserAnswer.objects.filter(question=question).count()
        level = question.tags.exclude(questionlevel=None).first()
        # 1-->easy   2-->inAverage   3-->hard
        if answer == question.correct_answer:
            if answer.duration < question.idealDuration:
                answerLevel = 1
            else:
                answerLevel = 2
        else:
            answerLevel = 3

        level.questionlevel.level = (level.questionlevel.level * (answers_num - 1) + answerLevel) / answers_num
        question.idealDuration = (question.idealDuration * (answers_num - 1) + answer.duration) / answers_num
        level.save()
        question.save()


def create_user_final_answer_answer(sender, instance, created, **kwargs):
    if created:
        answer = instance.userfinalanswer
        question = answer.question.finalanswerquestion
        answers_num = UserAnswer.objects.filter(question=question).count()
        level = question.tags.exclude(questionlevel=None).first()
        # 1-->easy   2-->inAverage   3-->hard
        if answer == question.correct_answer:
            if answer.duration < question.idealDuration:
                answerLevel = 1
            else:
                answerLevel = 2
        else:
            answerLevel = 3

        level.questionlevel.level = (level.questionlevel.level * (answers_num - 1) + answerLevel) / answers_num
        question.idealDuration = (question.idealDuration * (answers_num - 1) + answer.duration) / answers_num

        level.save()
        question.save()

# def updateUser(sender, instance, created, **kwargs):
#     answer = instance
#
#     if not created:
#
#
#
# def deleteUser(sender, instance, **kwargs):
#     answer = instance
#     answer.delete()


post_save.connect(create_user_multiple_choice_answer, sender=UserMultipleChoiceAnswer)
post_save.connect(create_user_final_answer_answer, sender=UserFinalAnswer)
# post_save.connect(create_user_multiple_choice_answer, sender=UserMultipleChoiceAnswer)

# post_save.connect(updateUser, sender=Profile)
# post_delete.connect(deleteUser, sender=Profile)
