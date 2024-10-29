from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def chess():
    chess_html = """
    <table>
    {% for i in range(8) %}
        <tr>
        {% for j in range(8) %}
            {% if (i+j)%2 == 0 %}
                <td style="width:20px;height:20px;background-color:black;"></td>
            {% else %}
                <td style="width:20px;height:20px;background-color:white;"></td>
            {% endif %}
        {% endfor %}
        </tr>
    {% endfor %}
    </table>
    """
    return render_template_string(chess_html)