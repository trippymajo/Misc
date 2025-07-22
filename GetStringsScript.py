import argparse
import os

FILE_EXTENSIONS = ['.cpp', '.h', '.c', '.ui']
FUNCTIONS_ROLES = {'str', 'ctx'}

def proc_parsing(files_list, funcs_list)
    """
    Parses strings from functions in provided files

    Args:
        files_list (string_list): All full file paths to be parsed
        funcs_list (tuples_list): Functions with roles with positions to search their content in
    """
    

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

            has_func = False
            full_file_path = os.path.join(dirpath, filename)
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
    if ':' in arg_func_str:
        func, params = arg_func_str.split(':')
        func = func.strip()

        # Validate func name
        if not func:
            raise ValueError(f"Incorrect name of the string: {func}")

        # Create a dictionary for str/ctx with position
        params_roles = {}
        for param in params.split(',', 1):
            param = param.strip()

            # Validate param
            if not param:
                continue
            if '=' not in param:
                raise ValueError(f"Incorrect param {param} for function {func}")

            role, pos = param.split('=', 1)
            role = role.strip()
            pos = int(pos.strip())

            # Validate role and pos
            if role not in FUNCTIONS_ROLES:
                raise ValueError(f"Unknown key '{role}' (allowed: str, ctx)")
            if (pos < 1 or pos > 17) or (not role):
                raise ValueError(f"Incorrect parameter {param} to read from function: {func}")

            params_roles[role] = int(pos)

        # Validations regarding roles provided
        if not ('str' in params_roles):
            raise ValueError("You must specify at least 'str' parameter")
        #if len(params_roles) > 2:
        #    raise ValueError("Too many parameters for function. Only 'str' and optionally 'ctx' allowed")

        return func, params_roles
    else:
        func = arg_func_str.strip()

        if not func:
            raise ValueError("Function name is required.")

        return func, {'str': 1}

def main():
    parser = argparse.ArgumentParser(
                        prog='GetStringsScript',
                        description='Extract strings from functions of the source path',
                        epilog='by Trippy Majo')

    parser.add_argument(
            'src_path',
            help='Path to source folder')

    parser.add_argument(
            '--funcs',
            nargs='+',
            required=True,
            help='Functions to get strings from e.g. "translate:ctx=1,str=2, tr:str=1", "doTranslate" ')

    parser.add_argument(
            '--debug',
            help='Activates debug state of the script, allowing to show some output info',
            action='store_true')

    args = parser.parse_args()

    # Populate list of functions (funcs with roles and position information)
    funcs_list = []
    for arg in args.funcs:
        funcs_list.append(parse_func_arg(arg))

    # Read all files in to list. Save them as .txt
    func_names = [f[0] for f in funcs_list]
    files_list = get_files_to_parse(args.src_path, func_names, args.debug)


# Entry Point
if __name__ == "__main__":
    main()