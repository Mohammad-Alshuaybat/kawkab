# import time
# start = time.perf_counter()
# end = time.perf_counter()


#     registration_info = models.OneToOneField('RegistrationInfo', db_constraint=False, null=True, blank=True, on_delete=models.SET_NULL)
#     @property
#     def average(self):
#         avg = self.certificate.aggregate(average=Avg(F('first')+F('second')+F('third')+F('final')))['average']
#         return avg


# general relation field
# from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
# content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
# object_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
# content_object = GenericForeignKey('content_type', 'object_id')
