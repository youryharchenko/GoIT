from __future__ import annotations

class Project:

    def __init__(self, data: dict) -> None:
        self.data = data
        self.name = data.get("name", "noname")
        self.works = data.get("works", [])

    def set_name(self, name: str):
        self.name = name
        self.data["name"] = name

    def set_works(self, works: list[Work]):
        self.works = works
        self.data["works"] = works

    def add_work(self, work: Work):
        self.works.append(work)
        self.data["works"] = self.works

    def get_work(self, name):
        
        for work in self.works:
            if work.name == name:
                #print(f"Get work OK: {work.name} == {name}")
                return work 
        return None

class Work:
     
    def __init__(self, name: str, code: str) -> None:
        self.code = code
        self.name = name

    def __str__(self):
        return f"Work({self.name}, {self.code})"
    
    def __repr__(self):
        return f"Work(name='{self.name}', code='{self.code}')"


