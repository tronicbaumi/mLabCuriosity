import time
fruits = ["apple", "banana", "beer"]
for x in fruits:
  print(x)
  
start = time.time()

mlab.set_do(0, 1)
time.sleep(1)
mlab.set_do(0, 0)
time.sleep(1)

print("ende")

  
  