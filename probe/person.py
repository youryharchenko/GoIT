import pickle
import copy

class Person:
    def __init__(self, name: str, email: str, phone: str, favorite: bool):
        self.name = name
        self.email = email
        self.phone = phone
        self.favorite = favorite

    def __copy__(self):
        return Person(self.name, self.email, self.phone, self.favorite)

class Contacts:
    def __init__(self, filename: str, contacts: list[Person] = []):
        self.filename = filename
        self.contacts = contacts
        self.count_save = 0
        self.is_unpacking = False

    def save_to_file(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self, f)
            

    def read_from_file(self):
        with open(self.filename, "rb") as f:
            contacts = pickle.load(f)
        return contacts
    
    def __getstate__(self):
        state = self.__dict__.copy() 
        state['count_save'] += 1
        return state
    
    def __setstate__(self, value):
        self.__dict__ = value
        self.is_unpacking = True

    def __copy__(self):
        contacts = Contacts(self.filename, self.contacts)
        contacts.count_save = self.count_save
        contacts.is_unpacking = self.is_unpacking
        return contacts
    
    def __deepcopy__(self, memo):
        contacts = Contacts(self.filename, copy.deepcopy(self.contacts, memo))
        contacts.count_save = self.count_save
        contacts.is_unpacking = self.is_unpacking
        return contacts

def copy_class_person(person):
    return copy.copy(person)

def copy_class_contacts(contacts):
    return copy.deepcopy(contacts)


contacts = [
    Person(
        "Allen Raymond",
        "nulla.ante@vestibul.co.uk",
        "(992) 914-3792",
        False,
    ),
    Person(
        "Chaim Lewis",
        "dui.in@egetlacus.ca",
        "(294) 840-6685",
        False,
    ),
]

persons = Contacts("user_class.picle", contacts)
persons.save_to_file()
person_from_file = persons.read_from_file()


print(persons == person_from_file)  # False
print(persons.contacts[0] == person_from_file.contacts[0])  # False
print(persons.contacts[0].name == person_from_file.contacts[0].name)  # True
print(persons.contacts[0].email == person_from_file.contacts[0].email)  # True
print(persons.contacts[0].phone == person_from_file.contacts[0].phone)  # True

first = persons.read_from_file()
first.save_to_file()
second = first.read_from_file()
second.save_to_file()
third = second.read_from_file()

print(persons.count_save)  # 0
print(first.count_save)  # 1
print(second.count_save)  # 2
print(third.count_save)  # 3

print(persons.is_unpacking)  # False
print(person_from_file.is_unpacking)  # True


person = Person(
    "Allen Raymond",
    "nulla.ante@vestibul.co.uk",
    "(992) 914-3792",
    False,
)
copy_person = copy_class_person(person)
print(copy_person == person)  # False
print(copy_person.name == person.name)  # True

new_persons = copy_class_contacts(persons)
new_persons.contacts[0].name = "Another name"
print(persons.contacts[0].name)  # Allen Raymond
print(new_persons.contacts[0].name)  # Another name
