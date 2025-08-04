import sys
from easy_prompt import Prompter
from easy_prompt.prebuilt import gpt_4o_mini as llm
from code_annotation import annotate_directory, set_prompter

if __name__ == "__main__":
    prompter = Prompter(llm)\
        .set_cache_path("__cache__")\
        .set_logger(sys.stdout)
    set_prompter(prompter)
    
    args = sys.argv[1:]
    annotate_directory(args[0], delete="-d" in args)