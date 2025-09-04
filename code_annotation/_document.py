from pathlib import Path
from typing import Optional
from code_annotation._comparison import is_isomorphic
from easy_prompting.prebuilt import Prompter, IContainer, IList, IItem, IData, ICode, delimit_code, If, list_text

def annotate_code(prompter: Prompter, code: str, types: bool = True, docs: bool = True, comments: bool = False,
                  format: bool = False, delete: bool = False, instruction: Optional[str] = None) -> str:
    [code_out] = prompter.get_copy()\
        .add_message(
            f"You are a Python expert. Follow the instructions of the user.",
            role="developer"
        )\
        .add_message(
            f"Please apply the following modification to the following Python code"
            +
            list_text(
                If(
                    types,
                    If(
                        not delete,
                        f"add type annotations whenever necessary.",
                        f"remove type annotations whenever possible.",
                    ),
                    None
                ),
                If(
                    docs,
                    If(
                        not delete,
                        f"add google style doc-strings whenever necessary.",
                        f"remove doc-strings whenever possible."
                    ),
                    None
                ),
                If(
                    comments,
                    If(
                        not delete,
                        f"add comments that explain the code whenever necessary.",
                        f"remove comments whenever possible."
                    ),
                    None
                ),
                If(
                    format,
                    If(
                        not delete,
                        f"improve the formatting of the code whenever necessary.",
                        None
                    ),
                    None
                ),
                f"leave everything else exactly as it is, including any kind of mistake or bad code.",
                f"do not add any kind of missing implementation or imports, they will be handled later.",
                instruction,
                scope=True
            )
        )\
        .add_message(
            f"Here is the code:\n"
            +
            delimit_code(code, "python")
        )\
        .get_data(
            IContainer(
                "Do the following",
                IList(
                    IItem("think", IData("Explain what you should do and what the code does"), no_extract=True),
                    IItem("code", ICode("Write the improved version of the code")),
                    add_stop=True
                )
            )
        )
    return code_out

def annotate_file(prompter: Prompter, file_path: Path, types: bool = True, docs: bool = True,
                  comments: bool = False, format: bool = False, delete: bool = False, instruction: Optional[str] = None) -> None:
    assert file_path.exists(), f"The given path does not exists: \"{file_path.absolute()}\""

    code = file_path.read_text()
    new_code = annotate_code(
        prompter=prompter,
        code=code,
        types=types,
        docs=docs,
        comments=comments,
        format=format,
        delete=delete,
        instruction=instruction
    )
    prefix = "safe." if is_isomorphic(code, new_code) else "unsafe."
    typed_file_path = file_path.parent / (prefix + file_path.name)
    typed_file_path.write_text(new_code)

def annotate_directory(prompter: Prompter, path: Path, recursive: bool = False, types: bool = True, docs: bool = True, comments: bool = False,
                       format: bool = False, delete: bool = False, instruction: Optional[str] = None, depth: int = 0) -> None:
    assert path.exists(), f"The given path does not exists: \"{path.absolute()}\""

    path = Path(path)
    if path.is_file() and path.name.endswith(".py"):
        annotate_file(
            prompter=prompter,
            file_path=path,
            types=types,
            docs=docs,
            comments=comments,
            format=format,
            delete=delete,
            instruction=instruction
        )
    elif path.is_dir() and (depth == 0 or recursive):
        for sub_path in tuple(path.iterdir()):
            annotate_directory(
                prompter=prompter,
                path=sub_path,
                recursive=recursive,
                types=types,
                docs=docs,
                comments=comments,
                format=format,
                delete=delete,
                instruction=instruction,
                depth=depth+1
            )