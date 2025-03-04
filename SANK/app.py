from flask import Flask, request, redirect, url_for
import os
import pandas as pd
import matplotlib.pyplot as plt

# Initialize Flask app
app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Home route with styled index page
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sales Data Analysis</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #007bff;
                color: #fff;
                padding: 20px;
                text-align: center;
            }
            main {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 80vh;
                text-align: center;
            }
            .upload-box {
                background: #fff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                width: 400px;
            }
            .upload-box h1 {
                font-size: 24px;
                margin-bottom: 20px;
            }
            .upload-box form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .upload-box input[type="file"] {
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                width: 100%;
            }
            .upload-box button {
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .upload-box button:hover {
                background-color: #0056b3;
            }
            footer {
                background-color: #333;
                color: #fff;
                text-align: center;
                padding: 10px;
                position: fixed;
                bottom: 0;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Welcome to the Sales Data Analysis App</h1>
        </header>
        <main>
            <div class="upload-box">
                <h1>Upload Your Sales Data</h1>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv,.xlsx" required>
                    <button type="submit">Upload</button>
                </form>
            </div>
        </main>
        <footer>
            &copy; 2025 Sales Data Analysis App | All Rights Reserved
        </footer>
    </body>
    </html>
    '''

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('graph_options', filename=file.filename))
    return "No file uploaded!", 400

# Graph options route
@app.route('/graph_options/<filename>', methods=['GET', 'POST'])
def graph_options(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            return "Unsupported file format!", 400
    except Exception as e:
        return f"Error reading file: {str(e)}", 400

    # Detect numeric columns
    numeric_columns = df.select_dtypes(include=['number']).columns

    if request.method == 'POST':
        selected_column = request.form.get('column')
        graph_type = request.form.get('graph_type')
        return redirect(
            url_for('generate_graph', filename=filename, column=selected_column, graph_type=graph_type)
        )

    # Render HTML for column and graph type selection
    columns_options = ''.join([f'<option value="{col}">{col}</option>' for col in numeric_columns])
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Select Graph Options</title>
    </head>
    <body>
        <h1>Select Graph Options</h1>
        <form method="POST">
            <label for="column">Choose a column:</label>
            <select name="column" required>
                {columns_options}
            </select>
            <br><br>
            <label for="graph_type">Choose a graph type:</label>
            <select name="graph_type" required>
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="histogram">Histogram</option>
            </select>
            <br><br>
            <button type="submit">Generate Graph</button>
        </form>
    </body>
    </html>
    '''

# Graph generation route
@app.route('/generate_graph/<filename>')
def generate_graph(filename):
    column = request.args.get('column')
    graph_type = request.args.get('graph_type')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            return "Unsupported file format!", 400
    except Exception as e:
        return f"Error reading file: {str(e)}", 400

    # Generate the requested graph
    plt.figure(figsize=(10, 6))
    if graph_type == 'line':
        df[column].plot(kind='line', title=f'Line Chart - {column}')
        plt.ylabel(column)
    elif graph_type == 'bar':
        df[column].value_counts().plot(kind='bar', title=f'Bar Chart - {column}')
        plt.ylabel('Frequency')
    elif graph_type == 'histogram':
        df[column].plot(kind='hist', title=f'Histogram - {column}', bins=20)
        plt.ylabel('Frequency')

    plt.xlabel(column)
    plt.grid(True)

    # Save the plot
    plot_path = os.path.join(app.config['STATIC_FOLDER'], f'{column}_{graph_type}.png')
    plt.savefig(plot_path)
    plt.close()

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Graph</title>
    </head>
    <body>
        <h1>Generated Graph</h1>
        <img src="/static/{column}_{graph_type}.png" alt="{graph_type} of {column}">
        <br><br>
        <a href="/">Go Back</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
