class Project:

    def __init__(self, data: dict) -> None:
        self.data = data
        self.name = data.get("name", "noname")

    def set_name(self, name: str):
        self.name = name
        self.data["name"] = name