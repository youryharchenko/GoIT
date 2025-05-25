from random import randrange

class Point:

    def __init__(self, x, y):
        self.__x = None
        self.__y = None
        self.x = x
        self.y = y

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, v):
        if type(v) == int or type(v) == float:
            self.__x = v
            
    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self, v):
        if type(v) == int or type(v) == float:
            self.__y = v

    def __str__(self):
        return f"Point({self.x},{self.y})"

class Vector:
    def __init__(self, coordinates: Point):
        self.coordinates = coordinates

    def __setitem__(self, index, value):
        if index == 0:
            self.coordinates.x = value
        elif index == 1:
            self.coordinates.y = value
   
    def __getitem__(self, index):
        if index == 0:
            return self.coordinates.x
        elif index == 1:
            return self.coordinates.y
        
    def __call__(self, value=None):
        if value == None:
            return (self.coordinates.x, self.coordinates.y)
        elif type(value) == int or type(value) == float:
            return (self.coordinates.x * value, self.coordinates.y * value)
        
    def __add__(self, vector):
        return Vector(Point(self[0]+vector[0], self[1]+vector[1]))
        

    def __sub__(self, vector):
        return Vector(Point(self[0]-vector[0], self[1]-vector[1]))
    
    def __mul__(self, vector):
        return self[0]*vector[0] + self[1]*vector[1]
    
    def len(self):
        return (self[0]*self[0] + self[1]*self[1]) ** (1/2)
    
    def __eq__(self, vector):
        return self.len() == self.len()

    def __ne__(self, vector):
        return self.len() != vector.len()

    def __lt__(self, vector):
        return self.len() < vector.len()

    def __gt__(self, vector):
        return self.len() > vector.len()

    def __le__(self, vector):
        return self.len() <= vector.len()

    def __ge__(self, vector):
        return self.len() >= vector.len()
        
    def __str__(self):
        return f"Vector({self.coordinates.x},{self.coordinates.y})"
    
class Iterable:
    def __init__(self, max_vectors, max_points):
        self.current_index = 0
        self.vectors = [Vector(Point(randrange(0, max_points), randrange(0, max_points))) for i in range(max_vectors)]
        self.max_vectors = max_vectors
        self.max_points = max_points

    def __next__(self):
        i = self.current_index 
        if i < self.max_vectors:
            self.current_index += 1
            return self.vectors[i]
        raise StopIteration
        
class RandomVectors:
    def __init__(self, max_vectors=10, max_points=50):
        self.max_vectors = max_vectors
        self.max_points = max_points

    def __iter__(self):
        return Iterable(self.max_vectors, self.max_points)
            
p = Point(0, 0)
print(f"{p.x} {p.y}")
print(p)

p.x = 1
p.y = 2
print(f"{p.x} {p.y}")

# p.x = 'a'

p1 = Point('a', 'b')
print(f"{p1.x} {p1.y}")

v = Vector(Point(1, 10))
print(f"{v[0]} {v[1]}")
v[0] = 10
print(f"{v[0]} {v[1]}")
print(v)
print(v())
print(v(5))

vectors = RandomVectors(5, 10)

for vector in vectors:
    print(vector)


