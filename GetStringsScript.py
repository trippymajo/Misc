import argparse
import os
import re

from typing import TextIO
from collections import defaultdict

FILE_EXTENSIONS = [".cpp", ".h", ".c", ".hpp" , ".ui"]
FUNCTIONS_ROLES = {"str", "ctx"} # Change this to enum later

def is_whitespace(s: str) -> bool:
    """
    Check whether string parsed from params is whitespaced

    Args:
        s (str): String to check
    Returns:
        bool (bool): True - Whitespaced. False - No whitespaced only.
    """
    try:
        decoded = s.encode('utf-8').decode('unicode_escape')
        return not decoded.strip()
    except UnicodeDecodeError:
        return False

def split_params(params_str:str) -> list[str]:
    """
    Split function's params in different strings

    Args:
        params_str (str): Content of the file to parse
    Returns:
        splitted_params (list[str]): Splitted in list params of the function
    """
    splitted_params = []
    current_str = ''
    depth = 0
    in_quotes = False
    quote_ch = ''
    escape = False
    for ch in params_str:
        if escape:
            current_str += ch
            escape = False
            continue

        if ch == '\\':
            current_str += ch
            escape = True
            continue

        if ch in ('"', "'"):
            if not in_quotes:
                in_quotes = True
                quote_ch = ch
                continue
            elif in_quotes and ch == quote_ch:
                in_quotes = False
                continue

            current_str += ch
            continue

        if in_quotes:
            current_str += ch
            continue

        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ',' and depth == 0:
            if not is_whitespace(current_str): # check if whitespaces passed
                splitted_params.append(current_str)
            current_str = ''
            continue

        #current_str += ch

    # Dont forget last param
    if not is_whitespace(current_str):
        splitted_params.append(current_str)

    return splitted_params


def find_closing_parenthesis(file_contents: str, opening_pos: int) -> int:
    """
    Find position of closing parenthesis '(' ')'

    Args:
        file_contents (str): Content of the file to parse
        opening_pos (int): Position of opening parenthesis
    Returns:
        pos (int): Closing position of the ')' parenthesis
    """
    parenth_opened = 0
    in_quotes = False
    quote_char = ""
    escape = False

    for pos in range(opening_pos, len(file_contents)):
        ch = file_contents[pos]
        if escape:
            escape = False
            continue

        if ch == "\\":
            escape = True
            continue

        if ch in ('"', "'"):
            if in_quotes and ch == quote_char:
                in_quotes = False
            elif not in_quotes:
                in_quotes = True
                quote_char = ch
            continue

        if in_quotes:
            continue

        if ch == "(":
            parenth_opened += 1
        elif ch == ")":
            parenth_opened -= 1
            if parenth_opened == 0:
                return pos # Ending position

    return -1 # Not Found. May be Error...


def find_func_calls(file_contents: str, func_to_find: str) -> list[str]:
    """
    Parsing code files for functions and strings in it as params

    Args:
        file_contents (str): Content of the file to parse
        func_to_find (str): Function name to find in code
    Returns:
        matches (list[str]): List of strings with parameters of the matching function name
    """
    # Finding exact function
    matches = []
    pattern = re.compile(rf"\b{re.escape(func_to_find)}\s*\(")

    for match in pattern.finditer(file_contents):
        start_pos = match.end()  # Position after first '('
        end_pos = find_closing_parenthesis(file_contents, start_pos - 1)

        if end_pos == -1:
            continue

        params_str = file_contents[start_pos:end_pos]
        matches.append(params_str)

    return matches

def parse_code(file_path_to_parse: str,
                funcs_dict: dict[str, list[dict[str, int]]]) -> list[str]:
    """
    Parsing code files for functions and strings in it as params

    Args:
        file_path_to_parse (str): Full file path to the code file to parse
        funcs_list (dict[str, list[dict[str, int]]]): Functions with roles with positions to search their content in

    Returns:
        strs_list (list[str]): List with parsed strings from code files
    """
    strs_set = set()

    with open(file_path_to_parse, "r", errors="ignore") as file:
        content = file.read()
        for func_name, pattern_list in funcs_dict.items():
            # Sort patterns for each function
            with_ctx = [p for p in pattern_list if 'ctx' in p]
            without_ctx = [p for p in pattern_list if 'ctx' not in p]
            with_ctx_sorted = sorted(with_ctx, key=lambda p: p['ctx'], reverse=True)
            ordered_patterns = with_ctx_sorted + without_ctx

            for found_params in find_func_calls(content, func_name):
                splited_params = split_params(found_params)

                for pattern in ordered_patterns:
                    # Write str, ctx as output string
                    # Can be None?
                    str_idx = pattern.get('str')
                    ctx_idx = pattern.get('ctx')

                    # Validate idx of the params
                    if (str_idx is None
                        or str_idx < 1
                        or str_idx > len(splited_params)):
                        continue

                    if ctx_idx is None:
                        ctx_out = ""
                    elif ctx_idx > len(splited_params):
                        continue
                    else:
                        ctx_out = splited_params[ctx_idx - 1] # Get psition of the context in params
                        ctx_out += ":"

                    str_out = splited_params[str_idx - 1] # Get psition of the string in params

                    strs_set.add(f"\"{ctx_out}{str_out}\"")
                    break

    return [s + "\n\n" for s in strs_set]


def parse_ui(file_path_to_parse: str) -> list[str]:
    """
    Parsing .ui files for strings in it.

    Args:
        file_path_to_parse (string): Full file path to the .ui file to parse

    Returns:
        strs_list (list[str]): List with parsed strings from .ui files
    """
    strs_set = set()

    with open(file_path_to_parse, "r", errors="ignore") as file:
        content = file.read()
        matches = re.findall(r"<string>(.*?)</string>", content)
        for match in matches:
            strs_set.add(f"{match}\n\n")


    return [s + "\n\n" for s in strs_set]


def proc_parsing(module: str,
                files_path_list: list[str],
                funcs_dict: dict[str, list[dict[str, int]]], 
                out_file: TextIO):
    """
    Orchestrator for Parsing strings from functions in provided files

    Args:
        module (str): Current module name
        files_path_list (list[str]): All full file paths to be parsed
        funcs_dict (dict[str, list[dict[str, int]]]): Functions with roles with positions to search their content in
        out_file (TextIOWrapper): Output file where to write results
    """
    strs_list = []

    for file_path in files_path_list:
        if file_path.endswith(".ui"):
            strs_list.extend(parse_ui(file_path))
        else:
            strs_list.extend(parse_code(file_path, funcs_dict))

    if strs_list:
        out_file.write(f"### Begin Module ({module})###\n\n")
        out_file.writelines(strs_list)
        out_file.write(f"### End Module ({module}) ###\n\n")


def get_files_to_parse(src_path: str, func_names: list[str], is_qtui: bool = False, is_debug: bool = False) -> list[str]:
    """
    Gets list of files to parse

    Args:
        src_path (str): Path for recursive scanning
        func_names (list[str]): Functions to get strings from
        is_qtui (bool): Flag to scan .ui files
        is_debug (bool): special flag to provide extra output

    Returns:
        files_list (list[str]): List with paths of the files to scan
    """
    files_list = []

    for dirpath, dirnames, filenames in os.walk(src_path):
        for filename in filenames:
            # Check if extension is good
            if not any(filename.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                continue

            full_file_path = os.path.join(dirpath, filename)

            # If .ui file, it is another kind of parsing,
            # and no need to check function name in content
            if is_qtui and filename.lower().endswith(".ui"):
                files_list.append(full_file_path)
                continue

            pattern = re.compile(rf"\b({'|'.join(map(re.escape, func_names))})\s*\(")

            with open(full_file_path, "r", errors="ignore") as f:
                for line in f:
                    if pattern.search(line):
                        files_list.append(full_file_path)
                        break

    # Showing debug info
    if is_debug:
        for filepath in files_list:
            print(filepath)

    return files_list


def parse_func_arg(arg_func_str: str) -> tuple[str, dict[str, int]]:
    """
    Validates and provides data for argument passed in format function:parameter_to_parse

    Args:
        arg_func_str (str): Argument passed by user

    Returns:
        parsed_arg (func_name, {role1: num1, role2: num2, ...}): parsed argument
    """
    if ":" in arg_func_str:
        func, params = arg_func_str.split(":")
        func = func.strip()

        # Validate func name
        if not func:
            raise ValueError(f"Incorrect name of the string: {func}")

        # Create a dictionary for str/ctx with position
        params_roles = {}
        for param in params.split(",", 1):
            param = param.strip()

            # Validate param
            if not param:
                continue
            if "=" not in param:
                raise ValueError(f"Incorrect param {param} for function {func}")

            role, pos = param.split("=", 1)
            role = role.strip()
            pos = int(pos.strip())

            # Validate role and pos
            if role not in FUNCTIONS_ROLES:
                raise ValueError(f"Unknown key '{role}' (allowed: str, ctx)")
            if (pos < 1 or pos > 17) or (not role):
                raise ValueError(f"Incorrect parameter {param} to read from function: {func}")

            params_roles[role] = int(pos)

        # Validations regarding roles provided
        if not ("str" in params_roles):
            raise ValueError("You must specify at least 'str' parameter")
        #if len(params_roles) > 2:
        #    raise ValueError("Too many parameters for function. Only "str" and optionally "ctx" allowed")

        return func, params_roles
    else:
        func = arg_func_str.strip()

        if not func:
            raise ValueError("Function name is required.")

        return func, {"str": 1}


def main():
    parser = argparse.ArgumentParser(
                        prog="GetStringsScript",
                        description="Extract strings from functions of the source path",
                        epilog="by Trippy Majo")

    parser.add_argument(
            "src_path",
            help="Path to source folder")

    parser.add_argument(
            "--funcs",
            nargs="+",
            required=True,
            help="Functions to get strings from e.g. 'translate:ctx=1,str=2, tr:str=1', 'doTranslate' ")

    parser.add_argument(
            "--qtui",
            help="Activated qt ui files scannning",
            action="store_true")

    parser.add_argument(
            "--debug",
            help="Activates debug state of the script, allowing to show some output info",
            action="store_true")

    args = parser.parse_args()

    # Populate dict of functions (funcs with roles and position information)
    funcs_patterns = defaultdict(list)
    for arg in args.funcs:
        func_name, roles = parse_func_arg(arg)
        funcs_patterns[func_name].append(roles)

    with open("CodeStrings.txt", "w+") as out_file:
        for module in os.listdir(args.src_path):
            module_path = os.path.join(args.src_path, module)
            if not os.path.isdir(module_path):
                continue

            # Read all files into list
            func_names = list(funcs_patterns.keys())
            files_list = get_files_to_parse(module_path, func_names, args.qtui, args.debug)

            # Parse everything with output in file
            proc_parsing(os.path.basename(module_path), files_list, funcs_patterns, out_file)


# Entry Point
if __name__ == "__main__":
    main()