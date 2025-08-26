from pathlib import Path
from typing import Optional
from easy_prompting.prebuilt import extract_code, delimit_code, If, Prompter, Message
from code_annotation._comparison import is_isomorphic

# TODO: explicitely handle __init__ case where implementations are hallucinated?

def annotate_code(prompter: Prompter, code: str, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False) -> str:
    new_code = prompter.get_copy()\
        .add_message(
            f"Please apply the following modification to the following python code"
            +
            Message.create_list(
                If(
                    types,
                    If(
                        not delete,
                        f"Add type annotations whenever necessary.",
                        f"Remove type annotations whenever possible.",
                    ),
                    None
                ),
                If(
                    docs,
                    If(
                        not delete,
                        f"Add google style doc-strings whenever necessary.",
                        f"Remove doc-strings whenever possible."
                    ),
                    None
                ),
                If(
                    comments,
                    If(
                        not delete,
                        f"Add comments that explain the code whenever necessary.",
                        f"Remove comments whenever possible."
                    ),
                    None
                ),
                If(
                    format,
                    If(
                        not delete,
                        f"Improve the formatting of the code whenever necessary.",
                        None
                    ),
                    None
                ),
                f"Leave everything else exactly as it is, including any kind of mistake or bad code.",
                scope = True
            )
        )\
        .add_message(
            f"Here is the code:\n{delimit_code(code, "python")}"
        )\
        .get_completion()
    return extract_code(new_code)

def annotate_file(prompter: Prompter, file_path: str | Path, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False) -> None:
    file_path = Path(file_path)
    code = file_path.read_text()
    new_code = annotate_code(prompter, code, delete, types, docs, comments, format)
    prefix = "safe." if is_isomorphic(code, new_code) else "unsafe."
    typed_file_path = file_path.parent / (prefix + file_path.name)
    typed_file_path.write_text(new_code)

def annotate_directory(prompter: Prompter, path: str | Path, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False, max_depth: Optional[int] = None, depth: int = 0) -> None:
    if max_depth is not None and depth >= max_depth:
        return
    path = Path(path)
    if path.is_file() and path.name.endswith(".py"):
        annotate_file(prompter, path, delete, types, docs, comments, format)
    elif path.is_dir():
        for _path in tuple(path.iterdir()):
            annotate_directory(prompter, _path, delete, types, docs, comments, format, max_depth, depth + 1)