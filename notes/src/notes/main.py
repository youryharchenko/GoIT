import pathlib
import sys
import shlex

from rich.console import Console

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

from appdirs import user_data_dir

from typing import Dict, Tuple, List

from notes.db import DB

app_name = "Notes"
app_author = "YouryHarchenko"


def main() -> None:

    commands = {
        "all-persons": 0,
        "add-person": 1,
        "table-info": 1,
        "show-tables": 0,
        "kuzu-version": 0,
        "help": 0,
        "hello": 0,
        "quit": 0,
    }

    console = Console()

    def validate(func):
        def inner(msg_prompt: str) -> List[str]:
            res: List[str] = func(msg_prompt)
            if len(res) > 0:
                res[0] = res[0].strip().lower()
                arity = len(res) - 1
                if res[0] in commands:
                    if commands[res[0]] == arity:
                        for i in range(arity):
                            res[i+1] = res[i+1].strip()
                    else:
                        console.print(f"[bold red]Command '{res[0]}' expected {commands[res[0]]}, but takes {arity} parameter(s)[/bold red]")
                        res = ['error']
                else:
                    console.print(f"[bold red]Unexpected command: {' '.join(res)}[/bold red]")
                    res = ['error']
            else:
                res = ['error']

            return res
                        
        return inner    

    data_path = pathlib.Path(user_data_dir(app_name, app_author))
    if not data_path.exists():
        data_path.mkdir()
    elif not data_path.is_dir():
        console.print(f"[bold red]Path {data_path} is not dir![/bold red]")
        sys.exit(1)


    history_path = data_path.joinpath('.history')
    history = FileHistory(history_path) 
    completer = WordCompleter(list(commands.keys()))

    db_path = data_path.joinpath('db.kuzu')
    db = DB(db_path)
    try:
        if db_path.exists():    
            db.open()
            console.print(f"[bold green]Open database {db_path}.[/bold green]")
        else:
            db.new()
            console.print(f"[bold yellow]New database {db_path}.[/bold yellow]")
    except Exception as ex:
        console.print(f"[bold red]{ex}[/bold red]")
        sys.exit(2)

    @validate
    def parse_input(msg_prompt: str) -> List[str]: 
        msg = session.prompt(msg_prompt)
        #cmd = msg.split() 
        cmd = shlex.split(msg)
        return cmd
    
    def print_help():
        console.print("Available commands and their arities:")
        for k, v in commands.items():
            console.print(f"    {k}/{v}")
    
    
    
    session = PromptSession(history=history, completer=completer, reserve_space_for_menu=True)

    console.print("[bold green]Welcome to the data assistant bot![/bold green]")
    console.print("Type 'help' for available commands or 'quit' to quit.")
    console.print("Press [yellow]Tab[/yellow] for auto-completion.")

    while True:
        repl = parse_input("Enter a command: ")
        try:
            match repl:
                case ['all-persons']:
                    console.print(db.all_persons())
                case ['add-person', name]:
                    console.print(db.add_person(name))
                case ['table-info', name]:
                    console.print(db.table_info(name))
                case ['show-tables']:
                    console.print(db.show_tables())
                case ['kuzu-version']:
                    console.print(db.get_version())
                case ['quit']:
                    console.print("[bold green]Good bye![/bold green]")
                    break
                case ['hello']:
                    console.print("[bold green]How can I help you?[/bold green]")
                case ['help']:
                    print_help()
                case ['error']:
                    console.print("")    
                case _:
                    console.print(f"[bold red]Unexpected command: {' '.join(repl)}[/bold red]")
        except Exception as ex:
            console.print(f"[bold red]{ex}[/bold red]")
    

    