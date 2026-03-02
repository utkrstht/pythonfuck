import sys
import ast

def convert_to_brainfuck(text, current_value=0):
    if not text:
        return "", current_value

    result = []
    
    first_char_code = ord(text[0])
    
    if current_value == 0:
        if first_char_code > 10:
            import math
            factor = int(math.sqrt(first_char_code))
            loop_count = first_char_code // factor
            remainder = first_char_code % factor
            
            # cell 0: outer loop counter
            # cell 1: result accumulator
            
            init_loop = (
                f"{'+' * factor}"       # Set cell 0 = factor
                "["                     # Start loop
                ">"                     # Move to cell 1
                f"{'+' * loop_count}"   # Add loop_count to cell 1
                "<"                     # Move back to cell 0
                "-"                     # Decrement cell 0
                "]"                     # End loop
                ">"                     # Move pointer to cell 1
            )
            
            result.append(init_loop)
            
            if remainder > 0:
                result.append('+' * remainder)
            
            current_value = first_char_code
        else:
            result.append('+' * first_char_code)
            current_value = first_char_code
            
        result.append('.')
    else:
        diff = first_char_code - current_value
        if diff > 0:
            result.append('+' * diff)
        elif diff < 0:
            result.append('-' * abs(diff))
        result.append('.')
        current_value = first_char_code
    
    for char in text[1:]:
        target_value = ord(char)
        diff = target_value - current_value
        
        if diff > 0:
            result.append('+' * diff)
        elif diff < 0:
            result.append('-' * abs(diff))
            
        result.append('.')
        current_value = target_value
        
    return "".join(result), current_value

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
        current_cell_value = 0

        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Name):
                    func_name = call.func.id
                    
                    if func_name == 'print':
                        if call.args:
                            arg = call.args[0]
                            text_to_print = ""
                            
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                text_to_print = arg.value
                            elif isinstance(arg, ast.Str):
                                text_to_print = arg.s
                                
                            if text_to_print:
                                code_segment, current_cell_value = convert_to_brainfuck(text_to_print + "\n", current_cell_value)
                                bf_code_parts.append(code_segment)

                    elif func_name == 'input':
                        if call.args:
                            arg = call.args[0]
                            prompt_text = ""
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                prompt_text = arg.value
                            elif isinstance(arg, ast.Str):
                                prompt_text = arg.s
                            
                            if prompt_text:
                                code_segment, current_cell_value = convert_to_brainfuck(prompt_text, current_cell_value)
                                bf_code_parts.append(code_segment)
                        
                        bf_code_parts.append(',----------[,----------]')
                        
                        current_cell_value = 0

        full_bf_code = "".join(bf_code_parts)
        
        with open("output.bf", "w") as f:
            f.write(full_bf_code)
            
        print(f"Success! Compiled '{input_file_path}' to 'output.bf'.")

        
    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
