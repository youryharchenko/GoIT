class Animal:
    color = "white"

    def __init__(self, nickname, weight):
        self.nickname = nickname
        self.weight = weight

    def say(self):
        pass

    def change_weight(self, weight):
        self.weight = weight

    def change_color(self, color):
        Animal.color = color

class Cat(Animal):

    def say(self):
        return 'Meow'
    
class Dog(Animal):

    def __init__(self, nickname, weight, breed, owner):
        super().__init__(nickname, weight)
        self.breed = breed
        self.owner = owner

    def say(self):
        return 'Woof'
    
    def who_is_owner(self):
        return self.owner.info()
    
class Owner:
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address

    def info(self):
        return {"name": self.name, "age": self.age, "address": self.address}


cat = Cat('Simon', 10)
print(f"Cat {cat.color} {cat.nickname} {cat.weight} {cat.say()}")

dog = Dog("Barbos", 23, "labrador", Owner('Me', 64, 'jhkhkjh'))
print(f"Dog {dog.color} {dog.nickname} {dog.weight} {dog.say()} {dog.owner.info()}")

first_animal = Animal("First", 3)
second_animal = Animal("Second", 4)
print(first_animal.color)
second_animal.change_color('red')
print(first_animal.color)


