import argparse
from pathlib import Path
import sys
from typing import Optional

from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT, FormatLogger

from code_annotation import annotate_directory

def run_from_commandline(path: str, recursive: bool, model_name: str, temperature: int, interactive: bool, cache_path: str,
                         types: bool, docs: bool, comments: bool, format: bool, delete: bool, instruction: Optional[str]):
    prompter = Prompter(GPT(model=model_name, temperature=temperature))\
        .set_loggers(FormatLogger(sys.stdout).set_max_lines(10))\
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
        instruction=instruction
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Annotate a file or directory of code using an OpenAI model."
    )
    parser.add_argument(
        "path",
        help="The path to the file or directory to annotate"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="If code annotation should be applied recursively to sub directories"
    )
    parser.add_argument(
        "--model-name",
        default="gpt-4o-mini",
        metavar="NAME",
        help="OpenAI model to use (i.g. gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-3.5-turbo) (default: gpt-4o-mini)."
    )
    parser.add_argument(
        "--temperature",
        type=int,
        default=0,
        metavar="VALUE",
        help=(
            "The temperature that the model should use for completion generation (default: 0)"
        )
    )
    parser.add_argument(
        "--cache-path",
        metavar="PATH",
        default="./completions",
        help="Cache LLM responses in PATH (default: ./completions)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interact with the LLM interactively"
    )
    parser.add_argument(
        "--no-types",
        action="store_true",
        help="Exclude type anntotaions"
    )
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Exclude doc-strings"
    )
    parser.add_argument(
        "--comments",
        action="store_true",
        help="Include comments"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Improve the formatting of the code"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete instead of include annotations"
    )
    parser.add_argument(
        "--instruction",
        metavar="TEXT",
        default=None,
        help="Give additional instructions to the LLM"
    )

    args = parser.parse_args()
    run_from_commandline(
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
        instruction=args.instruction
    )