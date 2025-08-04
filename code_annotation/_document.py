from pathlib import Path
from typing import Optional
from easy_prompt import Prompter
from easy_prompt.prebuilt import extract_code, If
from code_annotation._comparison import is_safe

_prompter: Optional[Prompter] = None

def set_prompter(prompter: Optional[Prompter]) -> None:
    global _prompter
    _prompter = prompter

def get_prompter() -> Optional[Prompter]:
    return _prompter

def annotate_code(code: str, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False) -> str:
    assert _prompter is not None, "Prompter has not been set"
    new_code = _prompter.get_copy()\
        .add_message(
            f"Please apply the following modification to the following Python code:"
            +
            If(
                types,
                If(
                    not delete,
                    f"\n- Add type annotations whenever necessary.",
                    f"\n- Remove type annotations whenever possible.",
                )
            )
            +
            If(
                docs,
                If(
                    not delete,
                    f"\n- Add google style doc-strings whenever necessary.",
                    f"\n- Remove doc-strings whenever possible."
                )
            )
            +
            If(
                comments,
                If(
                    not delete,
                    f"\n- Add comments that explain the code whenever necessary.",
                    f"\n- Remove comments whenever possible."
                )
            )
            +
            If(
                format,
                If(
                    not delete,
                    f"\n- Improve the formatting of the code whenever necessary."
                )
            )
            +
            f"\n- Leave everything else exactly as it is, including any kind of mistake or bad code."
            f"\nHere is the code:\n```python\n{code}\n```"
        )\
        .get_completion()
    return extract_code(new_code)

def annotate_file(file_path: str | Path, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False) -> None:
    file_path = Path(file_path)
    code = file_path.read_text()
    new_code = annotate_code(code, delete, types, docs, comments, format)
    prefix = "safe." if is_safe(code, new_code) else "unsafe."
    typed_file_path = file_path.parent / (prefix + file_path.name)
    typed_file_path.write_text(new_code)

def annotate_directory(path: str | Path, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False, max_depth: Optional[int] = None, depth: int = 0) -> None:
    if max_depth is not None and depth >= max_depth:
        return
    path = Path(path)
    if path.is_file() and path.name.endswith(".py"):
        annotate_file(path, delete, types, docs, comments, format)
    elif path.is_dir():
        for _path in tuple(path.iterdir()):
            annotate_directory(_path, delete, types, docs, comments, format, max_depth, depth + 1)