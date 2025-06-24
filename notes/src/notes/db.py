import kuzu
import pathlib

from typing import Dict, Tuple, List

def res_to_str(res: kuzu.QueryResult | List[kuzu.QueryResult]) -> str:
    if isinstance(res, kuzu.QueryResult):
        s = ''
        while res.has_next():
            s += ' '.join(str(i) for i in res.get_next())
            s += '\n'
        return s.strip()
    elif isinstance(res, list):
        print(len(res))
        s = ''
        for item in res:
            while item.has_next():
                s += ' '.join(str(i) for i in item.get_next())
                s += '\n'
            s += '\n'
        return s.strip()
    else:
        return "None"
        

class DB:

    def __init__(self, path: pathlib.Path):
        self.path = path

    def init(self, conn: kuzu.Connection) -> None:
        conn.execute("CREATE NODE TABLE Person(name STRING, PRIMARY KEY (name))")
        conn.execute("CREATE NODE TABLE Note(id SERIAL, crt_at TIMESTAMP DEFAULT current_timestamp(), PRIMARY KEY (id))")

    def open(self):
        self.db = kuzu.Database(self.path)
        self.conn = kuzu.Connection(self.db)

    def new(self):
        self.db = kuzu.Database(self.path)
        self.conn = kuzu.Connection(self.db)
        self.init(self.conn)

    def all_persons(self):
        return res_to_str(self.conn.execute("MATCH (p:Person) RETURN p.*"))
    
    def add_person(self, name: str):
        return res_to_str(self.conn.execute("CREATE (a:Person {name: $name})", {"name": name}))

    def table_info(self, name: str):
        return res_to_str(self.conn.execute(f"CALL TABLE_INFO('{name}') RETURN *"))

    def show_tables(self):
        return res_to_str(self.conn.execute("CALL SHOW_TABLES() RETURN *"))
    
    def get_version(self):
        return res_to_str(self.conn.execute("CALL DB_VERSION() RETURN *"))
        
        
