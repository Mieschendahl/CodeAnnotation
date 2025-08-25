from pathlib import Path
from typing import Optional
from easy_prompting.prebuilt import extract_code, delimit, If, Prompter
from code_annotation._comparison import is_isomorphic

def annotate_code(prompter: Prompter, code: str, delete: bool = False, types: bool = True, docs: bool = True, comments: bool = False, format: bool = False) -> str:
    new_code = prompter.get_copy()\
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
        )\
        .add_message(
            f"Here is the code:\n{delimit(code, "python")}"
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