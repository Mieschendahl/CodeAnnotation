import argparse
from pathlib import Path
import sys
from typing import Optional

from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT, PrintLogger

from code_annotation import annotate_directory, replace_directory

def run_annotation(path: str, recursive: bool, model_name: str, temperature: int, interactive: bool, cache_path: str,
                         types: bool, docs: bool, comments: bool, format: bool, delete: bool, instruction: Optional[str], include_artifacts: bool) -> None:
    prompter = Prompter(GPT(model=model_name, temperature=temperature))\
        .set_loggers(PrintLogger(sys.stdout).set_max_lines(15))\
        .set_cache_path(cache_path)\
        .set_interaction("user" if interactive else None)

    annotate_directory(
        prompter=prompter,
        path=Path(path),
        recursive=recursive,
        types=types,
        docs=docs,
        comments=comments,
        format=format,
        delete=delete,
        instruction=instruction,
        include_artifacts=include_artifacts
    )

def run_replace(path: str, recursive: bool, exclude_safe: bool, exclude_unsafe: bool) -> None:
    replace_directory(
        path=Path(path),
        recursive=recursive,
        exclude_safe=exclude_safe,
        exclude_unsafe=exclude_unsafe
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="code_annotation",
        description="Annotate code or replace originals with annotated versions."
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    # -----------------------------
    # annotate subcommand
    # -----------------------------
    p_annotate = subparsers.add_parser(
        "annotate",
        help="Annotate a file or directory of code using an OpenAI model.",
        description="Annotate a file or directory of code using an OpenAI model. The annotated files will start with safe./unsafe."
    )
    p_annotate.add_argument("path", help="The path to the file or directory to annotate")
    p_annotate.add_argument(
        "--model-name",
        default="gpt-4o-mini",
        metavar="NAME",
        help=("OpenAI model to use (e.g. gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-3.5-turbo). "
              "Default: gpt-4o-mini.")
    )
    p_annotate.add_argument(
        "--temperature",
        type=int,
        default=0,
        metavar="VALUE",
        help="Sampling temperature for generation (default: 0)"
    )
    p_annotate.add_argument(
        "--recursive",
        action="store_true",
        help="Apply annotation recursively to sub directories"
    )
    p_annotate.add_argument(
        "--cache-path",
        metavar="PATH",
        default="./completions",
        help="Cache LLM responses in PATH (default: ./completions)"
    )
    p_annotate.add_argument(
        "--interactive",
        action="store_true",
        help="Interact with the LLM interactively"
    )
    p_annotate.add_argument(
        "--no-types",
        action="store_true",
        help="Exclude type annotations"
    )
    p_annotate.add_argument(
        "--no-docs",
        action="store_true",
        help="Exclude docstrings"
    )
    p_annotate.add_argument(
        "--comments",
        action="store_true",
        help="Include comments"
    )
    p_annotate.add_argument(
        "--format",
        action="store_true",
        help="Improve the formatting of the code"
    )
    p_annotate.add_argument(
        "--delete",
        action="store_true",
        help="Delete instead of include annotations"
    )
    p_annotate.add_argument(
        "--instruction",
        metavar="TEXT",
        default=None,
        help="Give additional instructions to the LLM"
    )
    p_annotate.add_argument(
        "--include-artifacts",
        action="store_true",
        help="Whether files with the safe./unsafe. prefix should also be annotated"
    )

    # -----------------------------
    # replace subcommand
    # -----------------------------
    p_replace = subparsers.add_parser(
        "replace",
        help="Replace original code with annotated code (safe./unsafe. versions).",
        description="Replace original code with annotated code (safe./unsafe. versions)."
    )
    p_replace.add_argument("path", help="The path to the file or directory to process")
    p_replace.add_argument(
        "--recursive",
        action="store_true",
        help="Apply replacement recursively to sub directories"
    )
    p_replace.add_argument(
        "--exclude-unsafe",
        action="store_true",
        help="Does not replace originals with unsafe versions"
    )
    p_replace.add_argument(
        "--exclude-safe",
        action="store_true",
        help="Does not replace originals with safe versions"
    )

    args = parser.parse_args()

    if args.command == "annotate":
        run_annotation(
            path=args.path,
            recursive=args.recursive,
            model_name=args.model_name,
            temperature=args.temperature,
            interactive=args.interactive,
            cache_path=args.cache_path,
            types=not args.no_types,
            docs=not args.no_docs,
            comments=args.comments,
            format=args.format,
            delete=args.delete,
            instruction=args.instruction,
            include_artifacts=args.include_artifacts
        )

    elif args.command == "replace":
        run_replace(
            path=args.path,
            recursive=args.recursive,
            exclude_safe=args.exclude_safe,
            exclude_unsafe=args.exclude_unsafe
        )
    else:
        parser.error("Unknown command")