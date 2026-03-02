import sys
import ast

# i'm thinking of a hardcoded table for the characters but like it's fine rn
def generate_brainfuck_table():
    table = {}
    for i in range(256):
        char = chr(i)
        # simplistic approach: + for each value, . to print, [-] to clear
        code = ('+' * i) + '. [-]'
        table[char] = code
    return table

BRAINFUCK_TABLE = generate_brainfuck_table()

def convert_to_brainfuck(text):
    result = []
    for char in text:
        if char in BRAINFUCK_TABLE:
            result.append(BRAINFUCK_TABLE[char])
        else:
            pass 
    return "".join(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python converter.py <python_file>")
        sys.exit(1)
        
    input_file_path = sys.argv[1]
    
    try:
        with open(input_file_path, 'r') as f:
            code_content = f.read()

        try:
            tree = ast.parse(code_content)
        except SyntaxError as e:
            print(f"Error parsing Python file: {e}")
            sys.exit(1)

        bf_code_parts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                if node.args:
                    arg = node.args[0]
                    text_to_print = ""
                    
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        text_to_print = arg.value
                    elif isinstance(arg, ast.Str):
                        text_to_print = arg.s
                        
                    if text_to_print:
                        bf_code_parts.append(convert_to_brainfuck(text_to_print + "\n"))

        full_bf_code = "".join(bf_code_parts)
        
        with open("output.bf", "w") as f:
            f.write(full_bf_code)
            
        print(f"Success! Compiled '{input_file_path}' to 'output.bf'.")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
