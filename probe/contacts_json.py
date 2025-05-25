import json

def write_contacts_to_file(filename, contacts):
    with open(filename, "w") as f:
        json.dump({"contacts": contacts}, f)
        


def read_contacts_from_file(filename):
    with open(filename, "r") as f:
        contacts = json.load(f)
    return contacts["contacts"]

write_contacts_to_file("contacts.json", [{
    "name": "Allen Raymond",
    "email": "nulla.ante@vestibul.co.uk",
    "phone": "(992) 914-3792",
    "favorite": False,
}])

contacts = read_contacts_from_file("contacts.json")
print(contacts)
