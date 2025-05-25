import csv


def write_contacts_to_file(filename, contacts):
    with open(filename, "w", newline='') as f:
        if len(contacts) > 0:
            field_names = contacts[0].keys()
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(contacts)


def read_contacts_from_file(filename):
    with open(filename, "r", newline='') as f:
        reader = csv.DictReader(f)
        contacts = [r for r in reader]
        for c in contacts:
            c["favorite"] = True if c["favorite"] == 'True' else False
    return contacts

write_contacts_to_file("contacts.csv", [{
    "name": "Allen Raymond",
    "email": "nulla.ante@vestibul.co.uk",
    "phone": "(992) 914-3792",
    "favorite": False,
}])

contacts = read_contacts_from_file("contacts.csv")
print(contacts)

        
            
            
           