import sys
from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT
from code_annotation import annotate_directory

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Expecting arguments: <openai model name e.g. gpt-4o-mini> <file path> [-d for deleting annotation] [-i for interactive mode]")
        exit(0)

    llm = GPT(model=args[0], temperature=0)
    prompter = Prompter(llm)\
        .set_cache_path("__cache__")\
        .set_logger(sys.stdout)\
        .set_interaction("user" if "-i" in args else None)
    
    annotate_directory(prompter, args[1], delete="-d" in args)