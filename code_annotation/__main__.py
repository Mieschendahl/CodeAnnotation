import argparse
import sys
from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT
from code_annotation import annotate_directory

def main():
    parser = argparse.ArgumentParser(
        description="Annotate a directory of code using an OpenAI model."
    )
    parser.add_argument(
        "path",
        help="The path to the directory or file to annotate"
    )
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help=(
            "The OpenAI model name to use (default: gpt-4o-mini). "
            "Common options: gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-3.5-turbo"
        )
    )
    parser.add_argument(
        "-d", "--delete",
        action="store_true",
        help="Delete existing annotations instead of adding new ones"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for the model (default: 0.0)"
    )

    args = parser.parse_args()

    llm = GPT(model=args.model, temperature=args.temperature)
    prompter = Prompter(llm)\
        .set_cache_path("__cache__")\
        .set_logger(sys.stdout)

    if args.interactive:
        prompter.set_interaction("user")

    annotate_directory(prompter, args.path, delete=args.delete)

if __name__ == "__main__":
    main()
