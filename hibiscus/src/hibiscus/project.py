from __future__ import annotations

import pathlib
import pandas as pd

class Project:

    def __init__(self, path: pathlib.Path, data: dict) -> None:
        self.path = path
        self.data = data
        self.name: str = data.get("name", "noname")
        self.works: list[Work] = data.get("works", [])
        self.data_frames: list[Data] = data.get("data_frames", [])

    def set_name(self, name: str):
        self.name = name
        self.data["name"] = name

    def set_works(self, works: list[Work]):
        self.works = works
        self.data["works"] = works

    def add_work(self, work: Work):
        self.works.append(work)
        self.data["works"] = self.works

    def add_data(self, data: Data):
        self.data_frames.append(data)
        self.data["data_frames"] = self.data_frames


    def get_work(self, name) -> Work | None:
        for work in self.works:
            if work.name == name:
                #print(f"Get work OK: {work.name} == {name}")
                return work 
        return None
    
    def get_data_frame(self, name) -> Data | None:
        for data in self.data_frames:
            if data.name == name:
                #print(f"Get work OK: {work.name} == {name}")
                return data 
        return None

class Work:
     
    def __init__(self, name: str, code: str) -> None:
        self.code = code
        self.name = name

    def __str__(self):
        return f"Work({self.name}, {self.code})"
    
    def __repr__(self):
        return f"Work(name='{self.name}', code='{self.code}')"

class Data:
     
    def __init__(self, name: str, data_frame: pd.DataFrame) -> None:
        self.data_frame = data_frame
        self.name = name

    def __str__(self):
        return f"Work({self.name}, {self.data_frame})"
    
    def __repr__(self):
        return f"Work(name='{self.name}', data_frame='{self.data_frame}')"


