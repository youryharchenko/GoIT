class Contacts:
    current_id = 1

    def __init__(self):
        self.contacts = []

    def list_contacts(self):
        return self.contacts

    def add_contacts(self, name, phone, email, favorite):
        self.contacts.append({"id": Contacts.current_id ,"name": name, "phone": phone, "email": email, "favorite": favorite})
        Contacts.current_id += 1

    def get_contact_by_id(self, id):
        for item in self.contacts:
            if item['id'] == id:
                return item
        return None
    
    def remove_contacts(self, id):
        for item in self.contacts:
            if item['id'] == id:
                break
        else:
            return
        self.contacts.remove(item)

import pickle

def write_contacts_to_file(filename, contacts):
    with open(filename, "wb") as f:
        pickle.dump(contacts, f)
        


def read_contacts_from_file(filename):
    with open(filename, "rb") as f:
        contacts = pickle.load(f)
    return contacts

write_contacts_to_file("contacts.picle", {
    "name": "Allen Raymond",
    "email": "nulla.ante@vestibul.co.uk",
    "phone": "(992) 914-3792",
    "favorite": False,
})

contacts = read_contacts_from_file("contacts.picle")
print(contacts)
