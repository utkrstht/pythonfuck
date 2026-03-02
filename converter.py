import sys
import ast

def convert_to_brainfuck(text):
    if not text:
        return ""

    result = []
    
    first_char_code = ord(text[0])

    if first_char_code > 10:
        import math
        factor = int(math.sqrt(first_char_code))
        loop_count = first_char_code // factor
        remainder = first_char_code % factor
        
        # cell 0: outer loop counter (factor)
        # cell 1: result accumulator (starts at 0)
        
        init_loop = (
            f"{'+' * factor}"       # Set cell 0 = factor
            "["                     # Start loop (while cell 0 > 0)
            ">"                     # Move to cell 1
            f"{'+' * loop_count}"   # Add loop_count to cell 1
            "<"                     # Move back to cell 0
            "-"                     # Decrement cell 0
            "]"                     # End loop
            ">"                     # Move pointer to cell 1 (result is generally here now)
        )
        
        result.append(init_loop)
        
        if remainder > 0:
            result.append('+' * remainder)
            
        current_value = first_char_code
    else:
        result.append('+' * first_char_code)
        current_value = first_char_code

    result.append('.')
    
    for char in text[1:]:
        target_value = ord(char)
        diff = target_value - current_value
        
        if diff > 0:
            result.append('+' * diff)
        elif diff < 0:
            result.append('-' * abs(diff))
            
        result.append('.')
        current_value = target_value
        
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
