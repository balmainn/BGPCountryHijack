import matplotlib.pyplot as plt

x = [1,2,3,4,5]
y = [1,2,3,4,5]
plt.scatter(x,y)
a = [0,10]
b = [3.3]
plt.axvline(3,0,10,c='red')
plt.axvline(1,0,10,c='blue')
plt.axvline(10,0,10,c='green')
plt.show()