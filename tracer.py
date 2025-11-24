import sys
from typing import List 

class CodeTracer:
    def __init__(self):
        self.log = []

    def _trace_lines(self, frame, event, arg):
        if event == 'line':
            # Record line number and local variables
            clean_vars = {k:repr(v) for k,v in frame.f_locals.items() if not k.startswith('_') and k != 'self'}
            self.log.append({
                "line": frame.f_lineno, 
                "vars": clean_vars
            })
        return self._trace_lines

    def run(self, code_str, func_name, args, is_class=False):
        self.log = [] # Reset log
        
        # Sandbox environment
        sandbox = {"List": List} 
        
        try:
            # 1. Compile the string into real code
            exec(code_str, sandbox)
            
            # 2. Start Recording
            sys.settrace(self._trace_lines)
            
            # 3. Execute
            if is_class:
                # Logic: instance = Solution(); instance.func()
                instance = sandbox['Solution']()
                method = getattr(instance, func_name)
                result = method(*args)
            else:
                # Logic: func()
                func = sandbox[func_name]
                result = func(*args)
                
            # 4. Stop Recording
            sys.settrace(None)
            return result, self.log
            
        except Exception as e:
            sys.settrace(None)
            return f"Error: {e}", self.log