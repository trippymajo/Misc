import argparse
import os

FILE_EXTENSIONS = ['.cpp', '.h', '.c', '.ui']

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

            with open(os.path.join(src_path, filename)) as f:
                f.
            print()



    return files_list

def parse_func_arg(arg_func_str):
    """
    Validates and provides data for argument passed in format function:parameter_to_parse

    Args:
        arg_func_str (string): Argument passed by user

    Returns:
        function:parameter_to_parse (touple)
    """
    if ':' in arg_func_str:
        func, params = arg_func_str.split(':')
        func = func.strip()
        try:
            if param_num < 1 and param_num > 17: # Its an egg
                raise ValueError
        except:
            raise ValueError(f"Incorrect number of parameter to read: {s}")

    else:
        func, param_num = arg_func_str, 1
    return data, data

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
            help='Functions to get strings from e.g. translate:ctx=1,str=2, tr:str=1')

    parser.add_argument(
            '--debug',
            help='Activates debug state of the script, allowing to save some output info',
            action='store_true')

    args = parser.parse_args()

    funcs_list = []
    for arg in args.funcs:
        funcs_list.append(parse_func_arg(arg))

    # Check funcs argument
    if (args.funcs.)

    # Read all files in to list. Save them as .txt
    files_list = get_files_to_parse(args.src_path, args.funcs, args.debug)


# Entry Point
if __name__ == "__main__":
    main()