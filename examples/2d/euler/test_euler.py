import matplotlib.pyplot as plt

from euler import create_model

model = create_model((100, 100), 200)
u = model.solve(1.4)
ani = model.visualize(u)
plt.show()
