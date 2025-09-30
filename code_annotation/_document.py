from pathlib import Path
from typing import Optional
from easy_prompting.prebuilt import Prompter, IList, IItem, IData, ICode, delimit_code, list_text

from code_annotation._comparison import is_isomorphic

def If(condition: bool, then_text: Optional[str] = None, else_text: Optional[str] = None) -> Optional[str]:
    if condition:
        return then_text
    return else_text

def annotate_code(prompter: Prompter, code: str, types: bool = True, docs: bool = True, comments: bool = False,
                  format: bool = False, delete: bool = False, instruction: Optional[str] = None, tag: Optional[str] = None) -> str:
    [thoughts, code_out] = prompter.get_copy()\
        .set_tag(tag)\
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
                        f"Add type annotations whenever necessary",
                        f"Remove type annotations whenever possible",
                    ),
                    "Do not add or modify type annotations"
                ),
                If(
                    docs,
                    If(
                        not delete,
                        f"Add google style doc-strings whenever necessary (do not include type annotations in the doc-strings!)",
                        f"Remove doc-strings whenever possible"
                    ),
                    "Do not add or modify doc-strings"
                ),
                If(
                    comments,
                    If(
                        not delete,
                        f"Add comments that explain the code whenever necessary",
                        f"Remove comments whenever possible"
                    ),
                    f"Do not add or modify comments"
                ),
                If(
                    format,
                    If(
                        delete,
                        None,
                        f"Improve the formatting of the code whenever necessary"
                    ),
                    f"Do not modify the formatting of the code"
                ),
                f"Leave everything else exactly as it is, including any kind of mistake or bad code",
                f"Do not add any kind of missing implementation or imports, they will be handled later",
                instruction,
                add_scope=True
            )
        )\
        .add_message(
            f"Here is the code:\n"
            +
            delimit_code(code, "python")
        )\
        .get_data(
            IList(
                "Do the following",
                IItem("think", IData("Explain what you should do and what the code does")),
                IItem("code", ICode("Write the improved version of the code"))
            )
        )
    return code_out

def annotate_file(prompter: Prompter, file_path: Path, types: bool = True, docs: bool = True,
                  comments: bool = False, format: bool = False, delete: bool = False, instruction: Optional[str] = None, include_artifacts: bool = False) -> None:
    assert file_path.exists(), f"The given path does not exists: \"{file_path.absolute()}\""
    if not include_artifacts and (file_path.name.startswith("safe.") or file_path.name.startswith("unsafe.")):
        return
    code = file_path.read_text()
    new_code = annotate_code(
        prompter=prompter,
        code=code,
        types=types,
        docs=docs,
        comments=comments,
        format=format,
        delete=delete,
        instruction=instruction,
        tag=str(file_path)
    )
    prefix = "safe." if is_isomorphic(code, new_code) else "unsafe."
    typed_file_path = file_path.parent / (prefix + file_path.name)
    typed_file_path.write_text(new_code)

def annotate_directory(prompter: Prompter, path: Path, recursive: bool = False, types: bool = True, docs: bool = True, comments: bool = False,
                       format: bool = False, delete: bool = False, instruction: Optional[str] = None, depth: int = 0, include_artifacts: bool = False) -> None:
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
            instruction=instruction,
            include_artifacts=include_artifacts
        )
    elif path.is_dir() and (depth == 0 or recursive):
        for sub_path in sorted(tuple(path.iterdir())):
            if sub_path.exists():
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
                    depth=depth+1,
                    include_artifacts=include_artifacts
                )

def replace_file(file_path: Path, exclude_safe: bool = False, exclude_unsafe: bool = False) -> None:
    assert file_path.exists(), f"The given path does not exists: \"{file_path.absolute()}\""
    unsafe_file_path = file_path.parent / f"unsafe.{file_path.name}"
    if not exclude_unsafe and unsafe_file_path.is_file():
        file_path.write_text(unsafe_file_path.read_text())
        unsafe_file_path.unlink()
    safe_file_path = file_path.parent / f"safe.{file_path.name}"
    if not exclude_safe and safe_file_path.is_file():
        file_path.write_text(safe_file_path.read_text())
        safe_file_path.unlink()

def replace_directory(path: Path, recursive: bool = False, exclude_safe: bool = False, exclude_unsafe: bool = False, depth: int = 0) -> None:
    assert path.exists(), f"The given path does not exists: \"{path.absolute()}\""
    path = Path(path)
    if path.is_file() and path.name.endswith(".py"):
        replace_file(
            file_path=path,
            exclude_safe=exclude_safe,
            exclude_unsafe=exclude_unsafe
        )
    elif path.is_dir() and (depth == 0 or recursive):
        for sub_path in sorted(tuple(path.iterdir())):
            if sub_path.exists():
                replace_directory(
                    path=sub_path,
                    recursive=recursive,
                    exclude_safe=exclude_safe,
                    exclude_unsafe=exclude_unsafe,
                    depth=depth+1
                )