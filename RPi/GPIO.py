from random import randint
BOARD = 1
OUT = 1
IN = 1
micro=0
heatsensor=0
def setmode(a):
   print (a)
def setup(a, b):
   print (a)
def output(a, b):
   print (a)
   if b is 1:
      print ('on')
   else:
      print('off')
def cleanup():
   print ('pins released as inputs')
def setwarnings(flag):
   print ('False')
def input(number,source):
   print(number)
   if source =='m':
      if micro == 1:
         return True
         
      else:
         return False
   if source =='h':
      if heatsensor == 1:
         return True
         
      else:
         return False