import sys
import ast
import math

class BrainfuckCompiler:
    def __init__(self):
        self.code = []
        self.pointer = 0
        self.cells = {}  
        self.variables = {} 
        self.next_free_cell = 2

    def move_to(self, target_cell):
        diff = target_cell - self.pointer
        if diff > 0:
            self.code.append('>' * diff)
        elif diff < 0:
            self.code.append('<' * abs(diff))
        self.pointer = target_cell

    def get_current_value(self):
        return self.cells.get(self.pointer, None)

    def set_cell_value(self, target_value):
        current_value = self.get_current_value()
        
        if current_value is None:
            self.code.append('[-]')
            current_value = 0
            
        diff = target_value - current_value
        
        if diff > 0:
            self.code.append('+' * diff)
        elif diff < 0:
            self.code.append('-' * abs(diff))
            
        self.cells[self.pointer] = target_value

    def zero_current_cell(self):
        if self.get_current_value() == 0:
            return
        
        self.code.append('[-]')
        self.cells[self.pointer] = 0

    def print_string(self, text):
        if not text:
            return

        self.move_to(1)
        if self.get_current_value() is None:
             self.code.append('[-]')
             self.cells[1] = 0
        current_val = self.cells[1]

        for i, char in enumerate(text):
            char_code = ord(char)
            
            if i == 0 and current_val == 0 and char_code > 10:
                factor = int(math.sqrt(char_code))
                loop_count = char_code // factor
                remainder = char_code % factor
                
                self.move_to(0)
                self.zero_current_cell()
                self.set_cell_value(factor)
                
                self.code.append('[')
                self.move_to(1)
                self.code.append('+' * loop_count)
                self.move_to(0)
                self.code.append('-')
                self.cells[0] -= 1
                self.code.append(']')
                
                self.cells[0] = 0 
                
                self.move_to(1)
                self.cells[1] = factor * loop_count
                
                self.set_cell_value(char_code)
                current_val = char_code
            else:
                self.set_cell_value(char_code)
                current_val = char_code
            
            self.code.append('.')
            
        self.cells[1] = current_val

    def compile(self, tree):
        self.cells[0] = 0
        self.cells[1] = 0
        for node in tree.body:
            self.visit(node)
        return "".join(self.code)

    def visit(self, node):
        if isinstance(node, ast.Expr):
            self.visit_Expr(node)
        elif isinstance(node, ast.Assign):
            self.visit_Assign(node)
        elif isinstance(node, ast.If):
            pass

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.visit_Call(node.value)

    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        
        if func_name == 'print':
            self.handle_print(node)
        elif func_name == 'input':
            self.handle_input_void(node)


    def copy_cell(self, src, dest, zero_dest=True):
        self.move_to(0); self.zero_current_cell()
        if zero_dest:
            self.move_to(dest); self.zero_current_cell()
        
        self.move_to(src)
        self.code.append('[')
        self.move_to(dest); self.code.append('+')
        self.move_to(0); self.code.append('+')
        self.move_to(src); self.code.append('-')
        self.code.append(']')

        self.move_to(0)
        self.code.append('[')
        self.move_to(src); self.code.append('+')
        self.move_to(0); self.code.append('-')
        self.code.append(']')
        
        if dest in self.cells: del self.cells[dest]

    def add_cell(self, src, dest):
        self.copy_cell(src, dest, zero_dest=False)

    def sub_cell(self, src, dest):
        self.move_to(0); self.zero_current_cell()
        
        self.move_to(src)
        self.code.append('[')
        self.move_to(dest); self.code.append('-')
        self.move_to(0); self.code.append('+')
        self.move_to(src); self.code.append('-')
        self.code.append(']')
        
        self.move_to(0)
        self.code.append('[')
        self.move_to(src); self.code.append('+')
        self.move_to(0); self.code.append('-')
        self.code.append(']')
        
        if dest in self.cells: del self.cells[dest]

    def evaluate_expression(self, node, target_cell):
        if isinstance(node, ast.Constant):
            val = node.value
            int_val = 0
            if isinstance(val, int):
                int_val = val % 256
            elif isinstance(val, str) and len(val) == 1:
                int_val = ord(val)
            self.move_to(target_cell)
            self.set_cell_value(int_val)
            
        elif isinstance(node, ast.Name):
            src_var = node.id
            if src_var in self.variables:
                src_cell = self.variables[src_var]
                if src_cell == target_cell:
                    pass # x = x
                else:
                    self.copy_cell(src_cell, target_cell)
                    
        elif isinstance(node, ast.BinOp):
            self.evaluate_expression(node.left, target_cell)
            self.apply_operation(node.op, node.right, target_cell)
            
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'input':
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    self.print_string(arg.value)
            
            self.move_to(target_cell)
            self.zero_current_cell() 
            self.code.append(',')
            if target_cell in self.cells: del self.cells[target_cell]

    def mul_cell_real(self, src, dest):
        temp1 = self.next_free_cell; self.next_free_cell += 1
        
        self.move_to(temp1); self.zero_current_cell() 
        self.copy_cell(dest, temp1)
        
        self.move_to(dest); self.zero_current_cell()
        
        self.move_to(temp1)
        self.code.append('[')
        self.add_cell(src, dest)
        self.move_to(temp1)
        self.code.append('-')
        self.code.append(']')
        
        self.next_free_cell -= 1

    def div_cell_real(self, src, dest):
        numerator = self.next_free_cell; self.next_free_cell += 1
        rem = self.next_free_cell; self.next_free_cell += 1
        temp_diff = self.next_free_cell; self.next_free_cell += 1
        flag = self.next_free_cell; self.next_free_cell += 1
        
        self.move_to(numerator); self.zero_current_cell()
        self.copy_cell(dest, numerator)
        
        self.move_to(dest); self.zero_current_cell() 
        self.move_to(rem); self.zero_current_cell() 
        
        self.move_to(numerator)
        self.code.append('[')
        
        self.move_to(rem); self.code.append('+')
        
        self.move_to(temp_diff); self.zero_current_cell()
        self.copy_cell(rem, temp_diff)
        
        self.sub_cell(src, temp_diff)
        
        self.move_to(flag); self.code.append('[-]+')
        
        self.move_to(temp_diff)
        self.code.append('[')
        self.move_to(flag); self.code.append('-')
        self.move_to(temp_diff); self.code.append('[-]')
        self.code.append(']')
        
        self.move_to(flag)
        self.code.append('[')
        self.move_to(dest); self.code.append('+')
        self.move_to(rem); self.code.append('[-]')
        self.move_to(flag); self.code.append('-')
        self.code.append(']')
        
        self.move_to(numerator); self.code.append('-')
        self.code.append(']')
        
        self.move_to(flag); self.code.append('[-]')
        self.move_to(temp_diff); self.code.append('[-]')
        self.move_to(rem); self.code.append('[-]')
        self.move_to(numerator); self.code.append('[-]')
        
        # i have no idea what is happening here but if it works it works
        self.next_free_cell -= 4 
        pass
        
        self.move_to(flag); self.zero_current_cell()
        self.move_to(temp_diff); self.zero_current_cell()
        self.move_to(rem); self.zero_current_cell()
        self.move_to(numerator); self.zero_current_cell()
        
        self.next_free_cell -= 4

    def apply_operation(self, op, node, target_cell):
        if isinstance(node, ast.Constant):
            val = node.value
            if isinstance(val, int):
                self.move_to(target_cell)
                if isinstance(op, ast.Add):
                    self.code.append('+' * val)
                elif isinstance(op, ast.Sub):
                    self.code.append('-' * val)
                elif isinstance(op, ast.Mult):
                    temp = self.next_free_cell; self.next_free_cell += 1
                    self.move_to(temp); self.set_cell_value(val)
                    self.mul_cell_real(temp, target_cell)
                    self.move_to(temp); self.zero_current_cell()
                    self.next_free_cell -= 1
                elif isinstance(op, (ast.Div, ast.FloorDiv)):
                    temp = self.next_free_cell; self.next_free_cell += 1
                    self.move_to(temp); self.set_cell_value(val)
                    self.div_cell_real(temp, target_cell)
                    self.move_to(temp); self.zero_current_cell()
                    self.next_free_cell -= 1
                
                if target_cell in self.cells: del self.cells[target_cell]

        elif isinstance(node, ast.Name):
            src_var = node.id
            if src_var in self.variables:
                src_cell = self.variables[src_var]
                if isinstance(op, ast.Add):
                    self.add_cell(src_cell, target_cell)
                elif isinstance(op, ast.Sub):
                    self.sub_cell(src_cell, target_cell)
                elif isinstance(op, ast.Mult):
                    self.mul_cell_real(src_cell, target_cell)
                elif isinstance(op, (ast.Div, ast.FloorDiv)):
                    self.div_cell_real(src_cell, target_cell)
                if target_cell in self.cells: del self.cells[target_cell]
        
        elif isinstance(node, ast.BinOp):
            temp_cell = self.next_free_cell
            self.next_free_cell += 1
            
            self.evaluate_expression(node, temp_cell)
            
            if isinstance(op, ast.Add):
                self.add_cell(temp_cell, target_cell)
            elif isinstance(op, ast.Sub):
                self.sub_cell(temp_cell, target_cell)
            elif isinstance(op, ast.Mult):
                self.mul_cell_real(temp_cell, target_cell)
            elif isinstance(op, (ast.Div, ast.FloorDiv)):
                self.div_cell_real(temp_cell, target_cell)
            
            self.move_to(temp_cell)
            self.zero_current_cell()
            self.next_free_cell -= 1
            
            
            if target_cell in self.cells: del self.cells[target_cell]

    def visit_Assign(self, node):
        if len(node.targets) != 1: return
        target = node.targets[0]
        if not isinstance(target, ast.Name): return
        
        var_name = target.id
        if var_name not in self.variables:
            self.variables[var_name] = self.next_free_cell
            self.next_free_cell += 1
        
        cell_idx = self.variables[var_name]
        self.evaluate_expression(node.value, cell_idx)



    def handle_print(self, node):
        if not node.args:
            self.print_string("\n")
            return

        arg = node.args[0]
        
        if isinstance(arg, ast.Name):
            var_name = arg.id
            if var_name in self.variables:
                cell_idx = self.variables[var_name]
                
                self.move_to(cell_idx)
                if self.get_current_value() is None:
                    pass
                
                self.code.append('.')
                self.print_string("\n")
        
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            self.print_string(arg.value + "\n")
        
        elif isinstance(arg, ast.Str):
            self.print_string(arg.s + "\n")

    def handle_input_void(self, node):
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                self.print_string(arg.value)
        
        self.move_to(0)
        self.zero_current_cell()
        self.code.append(',----------[,----------]')
        self.cells[0] = 0

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

        compiler = BrainfuckCompiler()
        bf_code = compiler.compile(tree)
        
        with open("output.bf", "w") as f:
            f.write(bf_code)
            
        print(f"Success! Compiled '{input_file_path}' to 'output.bf'.")

    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
