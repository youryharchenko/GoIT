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

contacts = Contacts()

