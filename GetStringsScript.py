import argparse
import os
import re

FILE_EXTENSIONS = [".cpp", ".h", ".c", ".hpp" , ".ui"]
FUNCTIONS_ROLES = {"str", "ctx"}

def split_params(params):


def find_closing_parenthesis(file_contents, opening_pos):
    """
    Find position of closing parenthesis '(' ')'

    Args:
        file_contents (string): Content of the file to parse
        opening_pos (int): Position of opening parenthesis
    Returns:
        pos (int): Closing position of the ')' parenthesis
    """
    parenth_opened = 0
    in_quotes = False
    quote_char = ''
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

        if ch == '(':
            parenth_opened += 1
        elif ch == ')':
            parenth_opened -= 1
            if parenth_opened == 0:
                return pos # Ending position

    return -1 # Not Found. May be Error...


def find_func_calls(file_contents, func_to_find):
    """
    Parsing code files for functions and strings in it as params

    Args:
        file_contents (string): Content of the file to parse
        func_to_find (string): Function name to find in code
    Returns:
        matches (start_pos, end_pos, func_params): List of strings with parameters of the matching function name
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
        matches.append((match.start(), match.end(), params_str))

    return matches


def parse_code(parse_file, out_file, funcs_list):
    """
    Parsing code files for functions and strings in it as params

    Args:
        parse_file (string): Full file path to the .ui file to parse
        out_file (TextIOWrapper): Output file where to write results
        funcs_list (tuples_list): Functions with roles with positions to search their content in
    """
    parse_file = open("file", "r")
    content = parse_file.read()

    for func in funcs_list:
        func_params = find_func_calls(content, func[0])
        splited_params = split_params(func_params)


def parse_ui(parse_file, out_file):
    """
    Parsing .ui files for strings in it.

    Args:
        parse_file (string): Full file path to the .ui file to parse
        out_file (TextIOWrapper): Output file where to write results
    """
    parse_file = open("file", "r")
    content = parse_file.read()

    matches = re.findall(r"<string>(.*?)</string>", content)

    for match in matches:
        out_file.write(f"{match}\n\n")


def proc_parsing(module, files_list, funcs_list, out_file):
    """
    Orchestrator for Parsing strings from functions in provided files

    Args:
        module (string): Current module name
        files_list (string_list): All full file paths to be parsed
        funcs_list (tuples_list): Functions with roles with positions to search their content in
        out_file (TextIOWrapper): Output file where to write results
    """

    out_file.write("### Begin Module ({module})###\n\n")

    for file in files_list:
        if file.endswith(".ui"):
            parse_ui(file, out_file)
        else:
            parse_code(file, out_file, funcs_list)

    out_file.write("### End Module ###\n\n")


def get_files_to_parse(src_path, funcs, is_debug=False):
    """
    Gets list of files to parse

    Args:
        src_path (string): Path for recursive scanning
        funcs (string_list): Functions to get strings from
        is_debug (bool): special flag to provide extra output

    Returns:
        files_list (string_list): List with paths of the files to scan
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
            if filename.lower().endswith(".ui"):
                files_list.append(full_file_path)
                continue

            has_func = False
            with open(full_file_path) as f:
                content = f.read()

                for func in funcs:
                    if func in content:
                        has_func = True
                        break

            if not has_func:
                continue
            else:
                files_list.append(full_file_path)

    # Showing debug info
    if is_debug:
        for filepath in files_list:
            print(filepath)

    return files_list


def parse_func_arg(arg_func_str):
    """
    Validates and provides data for argument passed in format function:parameter_to_parse

    Args:
        arg_func_str (string): Argument passed by user

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
            "--debug",
            help="Activates debug state of the script, allowing to show some output info",
            action="store_true")

    args = parser.parse_args()

    # Populate list of functions (funcs with roles and position information)
    funcs_list = []
    for arg in args.funcs:
        funcs_list.append(parse_func_arg(arg))

    out_file = open("CodeStrings.txt", "a+")
    for dirpath, dirnames, filenames in os.walk(args.src_path):
        # Need to do module parsing, module = first subpath of the src
        for subpath in dirnames:
            # Read all files into list
            func_names = [f[0] for f in funcs_list]
            files_list = get_files_to_parse(args.src_path, func_names, args.debug)

            # Parse everything with output in file
            proc_parsing(subpath, files_list, func_names, out_file)


# Entry Point
if __name__ == "__main__":
    main()