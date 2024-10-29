from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
import subprocess
import sys
import re
import importlib.util
import subprocess



app = Flask(__name__)


load_dotenv()


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle user descriptions
@app.route('/generate', methods=['POST'])
def generate():
    description = request.form['description']
    print(f"Received description: {description}")

    if not description.strip():
        return jsonify({'error': 'Description cannot be empty.'}), 400
    
    # Placeholder for code generation logic
    code_blocks = process_description(description)
    return jsonify({'code_blocks': code_blocks})
    

def process_description(description):

    prompt = f"""
    Write only the Python Flask code for the following requirement:
    '{description}'

    - Do not include any explanations, comments, or code block delimiters.
    - Do not include the 'app.run()' statement.
    - Assume that 'app' will be run elsewhere.
    - Only use standard library modules and 'flask'.
    - Do not use any additional external libraries or modules like 'flask_session'.
    - Implement any additional functionality using standard libraries or basic Flask features.
    Provide the code only.
    """

    try:
        # Use OpenAI API to generate code
        response = client.chat.completions.create(
            model='gpt-4',  # You can choose a model suitable for code generation
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},  # optional system message
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=4000,
            n=1,
            stop=None
        )

        ai_message = response.choices[0].message.content
        code_match = re.search(r"```(?:python)?\n(.*?)```", ai_message, re.DOTALL)

        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            # If no code block delimiters, use the entire message
            generated_code = ai_message.strip()

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        generated_code = f"Error: {e}"

    print(generated_code)
    execution_result = execute_code(generated_code)


    # For simplicity, we'll return the generated code as one block
    return [
        {'title': 'Generated Code', 'code': generated_code},
        {'title': 'Execution Output', 'code': execution_result}
    ]



def execute_code(code):
    try:
        # Remove 'app.run()' if present
        code_without_run = '\n'.join(
            line for line in code.splitlines()
            if 'app.run' not in line.strip()
        )

        # Save code to 'temp_code.py'
        with open('temp_code.py', 'w') as f:
            f.write(code_without_run)

        # Extract imported modules from the code
        import re
        imports = re.findall(r'^import (\w+)', code_without_run, re.MULTILINE)
        imports += re.findall(r'^from (\w+) import', code_without_run, re.MULTILINE)

        # Remove standard library modules and 'flask' (since we assume it's installed)
        standard_libs = {'os', 'sys', 're', 'math', 'json', 'time', 'datetime'}
        required_modules = set(imports) - standard_libs - {'flask'}

        # Attempt to install required modules
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

        # Import the Flask app from 'temp_code.py'
        spec = importlib.util.spec_from_file_location("temp_code", "temp_code.py")
        temp_code = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(temp_code)

        app = getattr(temp_code, 'app', None)
        if app is None:
            return "No Flask app found in the code."

        # Use Flask's test client to simulate a request
        with app.test_client() as client:
            response = client.get('/')
            return response.data.decode('utf-8')  # Return the HTML content

    except Exception as e:
        return f"Error during execution: {e}"



if __name__ == '__main__':
    app.run(debug=True)
