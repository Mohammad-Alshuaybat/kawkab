import random

test_list = [1]

print("Original list is : " + str(test_list))

random_num = random.sample(test_list, 1) if len(test_list)>0 else 0

print("Random selected number is : " + str(random_num))
