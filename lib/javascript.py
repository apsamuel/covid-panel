import os, sys, glob 

def script_array(name):
    if os.path.exists(os.path.join('lib','snippets', f"{name}.js")):
        javascripts = glob.glob('lib/snippets/*.js')
        script_name = os.path.join('lib', 'snippets', f"{name}.js")
        if script_name in javascripts:
            with open(script_name, 'r') as file: 
                script_lines = file.readlines()
                return script_lines
    else:
        return None

def script_string(name):
    a = script_array(name)
    return "\n".join(a)