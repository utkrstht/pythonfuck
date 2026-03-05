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
        self.code.append('[-]' + '+' * (target_value % 256))
        self.cells[self.pointer] = target_value % 256

    def zero_current_cell(self):
        self.code.append('[-]')
        self.cells[self.pointer] = 0

    def print_number(self, cell_idx):
        val = self.next_free_cell
        hundreds = self.next_free_cell + 1
        tens = self.next_free_cell + 2
        ones = self.next_free_cell + 3
        is_printing = self.next_free_cell + 4
        temp = self.next_free_cell + 5
        rem = self.next_free_cell + 6
        self.next_free_cell += 7
        
        self.move_to(hundreds); self.zero_current_cell()
        self.move_to(tens); self.zero_current_cell()
        self.move_to(ones); self.zero_current_cell()
        self.move_to(is_printing); self.zero_current_cell()
        self.move_to(temp); self.zero_current_cell()
        self.move_to(rem); self.zero_current_cell()
        
        self.copy_cell(cell_idx, val)
        
        self.move_to(val)
        self.code.append('[')
        
        # ones++
        self.move_to(ones); self.code.append('+')
        
        self.move_to(rem); self.zero_current_cell()
        self.copy_cell(ones, rem)
        self.move_to(rem); self.code.append('----------')
        
        self.move_to(temp); self.zero_current_cell(); self.code.append('+')
        
        self.move_to(rem)
        self.code.append('[')
        self.move_to(temp); self.code.append('-') # flag = 0
        self.move_to(rem); self.code.append('[-]') 
        self.code.append(']')
        
        self.move_to(temp)
        self.code.append('[')
        self.move_to(ones); self.zero_current_cell()
        self.move_to(tens); self.code.append('+')
        
        self.move_to(rem); self.zero_current_cell()
        self.copy_cell(tens, rem)
        self.move_to(rem); self.code.append('----------')
        
        self.move_to(is_printing); self.zero_current_cell(); self.code.append('+')
        
        self.move_to(rem)
        self.code.append('[')
        self.move_to(is_printing); self.code.append('-') # flag2 = 0
        self.move_to(rem); self.code.append('[-]')
        self.code.append(']')
        
        self.move_to(is_printing)
        self.code.append('[')
        self.move_to(tens); self.zero_current_cell()
        self.move_to(hundreds); self.code.append('+')
        self.move_to(is_printing); self.code.append('-')
        self.code.append(']')
        
        self.move_to(temp); self.code.append('-') # finish outer flag
        self.code.append(']')
        
        self.move_to(val); self.code.append('-')
        self.code.append(']')
        
        self.move_to(is_printing); self.zero_current_cell()
        
        self.move_to(hundreds)
        self.code.append('[') 
        self.move_to(is_printing); self.code.append('[-]+') 
        self.move_to(hundreds)
        self.code.append('++++++++++++++++++++++++++++++++++++++++++++++++.')
        self.zero_current_cell() 
        self.code.append(']')
        
        self.move_to(temp); self.zero_current_cell()
        self.copy_cell(tens, temp)
        self.add_cell(is_printing, temp)
        
        self.move_to(temp)
        self.code.append('[')
        self.move_to(tens)
        self.code.append('++++++++++++++++++++++++++++++++++++++++++++++++.')
        self.move_to(is_printing); self.code.append('[-]+') 
        self.move_to(temp); self.zero_current_cell()
        self.code.append(']')
        
        self.move_to(ones)
        self.code.append('++++++++++++++++++++++++++++++++++++++++++++++++.')
        
        self.next_free_cell -= 7

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
            self.visit_If(node)

    def visit_If(self, node):
        condition_cell = self.next_free_cell
        self.next_free_cell += 1
        
        self.evaluate_expression(node.test, condition_cell)
        
        if_flag = self.next_free_cell
        else_flag = self.next_free_cell + 1
        self.next_free_cell += 2
        
        self.move_to(if_flag); self.zero_current_cell()
        self.move_to(else_flag); self.zero_current_cell(); self.code.append('+') # else_flag = 1

        self.move_to(condition_cell)
        self.code.append('[')
        self.move_to(if_flag); self.code.append('+')
        self.move_to(else_flag); self.zero_current_cell() # if condition is true, else_flag = 0
        self.move_to(condition_cell); self.code.append('-')
        self.code.append(']')
        
        self.move_to(if_flag)
        self.code.append('[')
        for child in node.body:
             self.visit(child)
        self.move_to(if_flag); self.zero_current_cell()
        self.code.append(']')
        
        if node.orelse:
            self.move_to(else_flag)
            self.code.append('[')
            for child in node.orelse:
                 self.visit(child)
            self.move_to(else_flag); self.zero_current_cell()
            self.code.append(']')

        self.next_free_cell -= 3 # if_flag, else_flag, condition_cell
        self.move_to(condition_cell); self.zero_current_cell()
        if condition_cell in self.cells: del self.cells[condition_cell]

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

    def compare_string_eq(self, cell1, cell2, target):
        self.move_to(target); self.zero_current_cell(); self.code.append('+') # Default success = 1
        
        diff = self.next_free_cell
        temp_val1 = self.next_free_cell + 1
        temp_val2 = self.next_free_cell + 2
        any_nonzero = self.next_free_cell + 3
        self.next_free_cell += 4
        
        for i in range(32):
             self.move_to(any_nonzero); self.zero_current_cell()
             self.copy_cell(cell1 + i, temp_val1)
             self.move_to(temp_val1)
             self.code.append('[')
             self.move_to(any_nonzero); self.code.append('+')
             self.move_to(temp_val1); self.code.append('[-]')
             self.code.append(']')
             
             self.copy_cell(cell2 + i, temp_val2)
             self.move_to(temp_val2)
             self.code.append('[')
             self.move_to(any_nonzero); self.code.append('+')
             self.move_to(temp_val2); self.code.append('[-]')
             self.code.append(']')
             
             self.move_to(diff); self.zero_current_cell()
             self.copy_cell(cell1 + i, temp_val1)
             self.copy_cell(cell2 + i, temp_val2)
             
             self.copy_cell(temp_val1, diff)
             self.sub_cell(temp_val2, diff)
             
             self.move_to(diff)
             self.code.append('[')
             self.move_to(target); self.zero_current_cell()
             self.move_to(diff); self.code.append('[-]') 
             self.code.append(']')
             
        self.next_free_cell -= 4

    def compare_eq(self, cell1, cell2, target):
        self.move_to(target); self.zero_current_cell(); self.code.append('+') # Default true
        
        diff = self.next_free_cell; self.next_free_cell += 1
        self.move_to(diff); self.zero_current_cell()
        self.copy_cell(cell1, diff)
        self.sub_cell(cell2, diff) # diff = cell1 - cell2
        
        self.move_to(diff)
        self.code.append('[')
        self.move_to(target); self.code.append('-')
        self.move_to(diff); self.code.append('[-]') 
        self.code.append(']')
        
        self.next_free_cell -= 1

    def compare_neq(self, cell1, cell2, target):
        self.move_to(target); self.zero_current_cell()
        
        diff = self.next_free_cell; self.next_free_cell += 1
        self.move_to(diff); self.zero_current_cell()
        self.copy_cell(cell1, diff)
        self.sub_cell(cell2, diff)
        
        self.move_to(diff)
        self.code.append('[')
        self.move_to(target); self.code.append('+')
        self.move_to(diff); self.code.append('[-]')
        self.code.append(']')
        
        self.next_free_cell -= 1

    def compare_gt(self, cell1, cell2, target):
        t1 = self.next_free_cell
        t2 = self.next_free_cell + 1
        temp = self.next_free_cell + 2
        flag = self.next_free_cell + 3
        self.next_free_cell += 4
        
        self.move_to(t1); self.zero_current_cell(); self.copy_cell(cell1, t1)
        self.move_to(t2); self.zero_current_cell(); self.copy_cell(cell2, t2)
        
        self.move_to(t2)
        self.code.append('[')
        
        self.move_to(flag); self.zero_current_cell()
        self.move_to(temp); self.zero_current_cell()
        
        self.move_to(t1)
        self.code.append('[')
        self.move_to(temp); self.code.append('+')
        self.move_to(flag); self.zero_current_cell(); self.code.append('+')
        self.move_to(t1); self.code.append('-')
        self.code.append(']')
        
        self.move_to(temp)
        self.code.append('[')
        self.move_to(t1); self.code.append('+')
        self.move_to(temp); self.code.append('-')
        self.code.append(']')
        
        self.move_to(flag)
        self.code.append('[')
        self.move_to(t1); self.code.append('-')
        self.move_to(flag); self.code.append('-')
        self.code.append(']')
        
        self.move_to(t2); self.code.append('-')
        self.code.append(']')
        
        self.move_to(target); self.zero_current_cell()
        self.move_to(t1)
        self.code.append('[')
        self.move_to(target); self.zero_current_cell(); self.code.append('+')
        self.move_to(t1); self.code.append('[-]')
        self.code.append(']')
        
        self.next_free_cell -= 4

    def compare_lt(self, cell1, cell2, target):
        self.compare_gt(cell2, cell1, target)

    def evaluate_expression(self, node, target_cell):
        if isinstance(node, ast.Constant):
            val = node.value
            int_val = 0
            if isinstance(val, int):
                self.move_to(target_cell)
                self.set_cell_value(val % 256)
            elif isinstance(val, str):
                if len(val) == 1:
                    int_val = ord(val)
                    self.move_to(target_cell)
                    self.set_cell_value(int_val)
                else:
                    for i, char in enumerate(val):
                        self.move_to(target_cell + i)
                        self.set_cell_value(ord(char))
                    self.move_to(target_cell + len(val))
                    self.set_cell_value(0)
            
        elif isinstance(node, ast.Name):
            src_var = node.id
            if src_var in self.variables:
                var_info = self.variables[src_var]
                src_cell = var_info['address']
                length = var_info.get('length', 1)
                
                for i in range(length):
                    if target_cell + i == src_cell + i:
                        pass
                    else:
                        self.copy_cell(src_cell + i, target_cell + i)
                    
        elif isinstance(node, ast.BinOp):
            self.evaluate_expression(node.left, target_cell)
            self.apply_operation(node.op, node.right, target_cell)

        elif isinstance(node, ast.Compare):
             left = node.left
             op = node.ops[0]
             comparator = node.comparators[0]
             
             is_string_comparison = False
             
             if isinstance(left, ast.Name) and left.id in self.variables:
                 if self.variables[left.id]['type'] == 'string':
                     is_string_comparison = True
             elif isinstance(left, ast.Constant) and isinstance(left.value, str) and len(left.value) > 1:
                     is_string_comparison = True

             if isinstance(comparator, ast.Name) and comparator.id in self.variables:
                 if self.variables[comparator.id]['type'] == 'string':
                     is_string_comparison = True
             elif isinstance(comparator, ast.Constant) and isinstance(comparator.value, str) and len(comparator.value) > 1:
                     is_string_comparison = True
             
             left_cell = self.next_free_cell
             if is_string_comparison: self.next_free_cell += 32
             else: self.next_free_cell += 1
             
             self.evaluate_expression(left, left_cell)
             
             right_cell = self.next_free_cell
             if is_string_comparison: self.next_free_cell += 32
             else: self.next_free_cell += 1
             
             self.evaluate_expression(comparator, right_cell)
             
             if is_string_comparison:
                  self.compare_string_eq(left_cell, right_cell, target_cell)
             else:
                 if isinstance(op, ast.Eq):
                     self.compare_eq(left_cell, right_cell, target_cell)
                 elif isinstance(op, ast.NotEq):
                     self.compare_eq(left_cell, right_cell, target_cell)
                     self.move_to(target_cell)
                     temp = self.next_free_cell; self.next_free_cell += 1
                     self.move_to(temp); self.zero_current_cell()
                     self.code.append('+') # temp = 1
                     
                     self.move_to(target_cell)
                     self.code.append('[') 
                     self.move_to(temp); self.code.append('-') # temp = 0
                     self.move_to(target_cell); self.code.append('[-]') 
                     self.code.append(']')
                     
                     self.move_to(temp)
                     self.code.append('[')
                     self.move_to(target_cell); self.code.append('+')
                     self.move_to(temp); self.code.append('-')
                     self.code.append(']')
                     
                     self.next_free_cell -= 1

                 elif isinstance(op, ast.Lt):
                     self.compare_lt(left_cell, right_cell, target_cell)
                 elif isinstance(op, ast.Gt):
                     self.compare_gt(left_cell, right_cell, target_cell)
                 
             if is_string_comparison: self.next_free_cell -= 64
             else: self.next_free_cell -= 2 
            
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'input':
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    self.print_string(arg.value)
            
            sentinel_cell = target_cell - 1
            if sentinel_cell < 1: 
                sentinel_cell = 1
            
            save_loc = self.next_free_cell
            self.next_free_cell += 1
            self.move_to(save_loc); self.zero_current_cell()
            self.copy_cell(sentinel_cell, save_loc)
            
            self.move_to(sentinel_cell); self.zero_current_cell()
            
            self.move_to(target_cell)
            self.zero_current_cell()
            
            self.code.append(',----------[++++++++++>,----------]')
            
            self.code.append('<[<]>') 
            self.copy_cell(save_loc, sentinel_cell)
            self.move_to(save_loc); self.zero_current_cell()
            self.next_free_cell -= 1
            
            self.move_to(target_cell)
            
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
                src_cell = self.variables[src_var]['address']
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
        
        value_type = 'int'
        value_length = 1
        
        if isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                if len(node.value.value) > 1:
                    value_type = 'string'
                    value_length = len(node.value.value) + 1 
                else: 
                    value_type = 'char'
        elif isinstance(node.value, ast.Name):
            if node.value.id in self.variables:
                src_info = self.variables[node.value.id]
                value_type = src_info.get('type', 'int')
                value_length = src_info.get('length', 1)
        elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'input':
             value_type = 'string'
             value_length = 32

        self.variables[var_name] = {
            'type': value_type,
            'length': value_length,
            'address': self.next_free_cell
        }
        
        cell_idx = self.variables[var_name]['address']
        self.next_free_cell += value_length
        
        self.evaluate_expression(node.value, cell_idx)



    def handle_print(self, node):
        if not node.args:
            self.print_string("\n")
            return

        arg = node.args[0]
        
        if isinstance(arg, ast.Name):
            var_name = arg.id
            if var_name in self.variables:
                var_info = self.variables[var_name]
                cell_idx = var_info['address']
                var_type = var_info.get('type', 'int')
                
                if var_type == 'string':
                     length = var_info.get('length', 1)
                     start_cell = cell_idx
                     sentinel_cell = start_cell - 1
                     if sentinel_cell < 1: sentinel_cell = 1
                     
                     save_loc = self.next_free_cell; self.next_free_cell += 1
                     self.move_to(save_loc); self.zero_current_cell()
                     self.copy_cell(sentinel_cell, save_loc)
                     
                     self.move_to(sentinel_cell); self.zero_current_cell()
                     
                     self.move_to(start_cell)
                     self.code.append('[.>]<[<]>')
                     self.pointer = start_cell
                     
                     self.copy_cell(save_loc, sentinel_cell)
                     self.move_to(save_loc); self.zero_current_cell()
                     self.next_free_cell -= 1

                elif var_type == 'int':
                    self.print_number(cell_idx)
                else:
                    self.move_to(cell_idx)
                    self.code.append('.')
                
                self.print_string("\n")
        
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            self.print_string(arg.value + "\n")
            
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, int):
             self.print_string(chr(arg.value % 256) + "\n")
        
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
