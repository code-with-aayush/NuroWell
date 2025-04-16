
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, session
import time
import pandas as pd
from groq import Groq
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import subprocess
import signal

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

df = pd.read_csv("sensor_data.txt", header=None)  

# Initialize Groq client
client = Groq(api_key="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")

# Global variables
reading_enabled = False
reading_start_time = None  # To track when reading started
sensor_data_history = {'bpm': [], 'timestamps': []}  # Use 'bpm' for consistency
latest_sensor_data = {'spo2': 'N/A', 'gsr': 'N/A', 'bpm': 'N/A', 'hrv': 'N/A'}
user_responses = {}
stress_level = 2  # Set to 2 based on sample (low stress)
user_name = "Aayush"  # Set to Aayush based on sample
user_age = 19       # Set to 19 based on sample
arduino_process = None  # To store the background process

@app.route('/', methods=['GET', 'POST'])
def index():
    global user_name, user_age
    if request.method == 'POST':
        user_name = request.form['name']
        user_age = int(request.form['age'])
        return redirect(url_for('next_page'))
    return render_template('index.html')

@app.route('/next-page')
def next_page():
    return render_template('next-page.html')

@app.route('/start_reading', methods=['POST'])
def start_reading():
    global reading_enabled, arduino_process, reading_start_time
    if not reading_enabled:
        reading_enabled = True
        reading_start_time = time.time()  # Record the start time
        # Run the sensor_reader.py file in the background
        arduino_process = subprocess.Popen(['python', 'sensor_reader.py'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
        return jsonify({'status': 'Reading started'})
    return jsonify({'status': 'Already reading'})

@app.route('/stop_reading', methods=['POST'])
def stop_reading():
    global reading_enabled, arduino_process, reading_start_time
    if reading_enabled and arduino_process:
        reading_enabled = False
        # Terminate the background process
        if arduino_process.poll() is None:  # Check if process is still running
            arduino_process.terminate()
            try:
                arduino_process.wait(timeout=5)  # Wait for clean termination
            except subprocess.TimeoutExpired:
                arduino_process.kill()  # Force kill if it doesn't terminate
        arduino_process = None
        reading_start_time = None  # Reset the start time
        return jsonify({'status': 'Reading stopped'})
    return jsonify({'status': 'Not reading'})

@app.route('/get_sensor_data')
def get_sensor_data():
    global reading_enabled, sensor_data_history, latest_sensor_data, reading_start_time
    if not reading_enabled:
        return jsonify({
            'spo2': 'N/A',
            'gsr': 'N/A',
            'bpm': 'N/A',
            'hrv': 'N/A',
            'error': 'Reading not enabled'
        })

    # Check if 20 seconds have passed since reading started
    if reading_start_time and (time.time() - reading_start_time < 20):
        return jsonify({
            'spo2': 'N/A',
            'gsr': 'N/A',
            'bpm': 'N/A',
            'hrv': 'N/A',
            'error': 'Waiting for initial 20-second delay'
        })

    try:
        # Read the latest sensor data from the text file (updated by sensor_reader.py)
        with open('sensor_data.txt', 'r') as file:
            lines = file.readlines()
            if len(lines) >= 4:
                spo2 = float(lines[0].strip())  # Line 0: SpO2
                gsr = float(lines[1].strip())   # Line 1: GSR
                bpm = float(lines[2].strip())   # Line 2: BPM
                hrv = float(lines[3].strip())   # Line 3: HRV
            else:
                raise ValueError("Insufficient data in sensor_data.txt")

        current_time = time.strftime('%H:%M:%S')
        sensor_data_history['bpm'].append(bpm)
        sensor_data_history['timestamps'].append(current_time)
        if len(sensor_data_history['bpm']) > 10:
            sensor_data_history['bpm'].pop(0)
            sensor_data_history['timestamps'].pop(0)

        latest_sensor_data['spo2'] = spo2
        latest_sensor_data['gsr'] = gsr
        latest_sensor_data['bpm'] = bpm
        latest_sensor_data['hrv'] = hrv

        return jsonify({
            'spo2': spo2,
            'gsr': gsr,
            'bpm': bpm,
            'hrv': hrv,
            'error': None
        })
    except Exception as e:
        return jsonify({
            'spo2': 'N/A',
            'gsr': 'N/A',
            'bpm': 'N/A',
            'hrv': 'N/A',
            'error': str(e)
        })

@app.route('/get_chart_data')
def get_chart_data():
    return jsonify(sensor_data_history)

@app.route('/psychological-test', methods=['GET', 'POST'])
def psychological_test():
    if request.method == 'POST':
        user_responses['q1'] = request.form['sleep-hours']
        return redirect(url_for('psychological_test_2'))
    return render_template('psychological-test.html')

@app.route('/psychological-test-2', methods=['GET', 'POST'])
def psychological_test_2():
    if request.method == 'POST':
        user_responses['q2'] = request.form['exercise-frequency']
        return redirect(url_for('psychological_test_3'))
    return render_template('psychological-test-2.html')

@app.route('/psychological-test-3', methods=['GET', 'POST'])
def psychological_test_3():
    if request.method == 'POST':
        user_responses['q3'] = request.form['caffeine-frequency']
        return redirect(url_for('psychological_test_4'))
    return render_template('psychological-test-3.html')

@app.route('/psychological-test-4', methods=['GET', 'POST'])
def psychological_test_4():
    if request.method == 'POST':
        user_responses['q4'] = request.form['work-life-balance']
        return redirect(url_for('psychological_test_5'))
    return render_template('psychological-test-4.html')

@app.route('/psychological-test-5', methods=['GET', 'POST'])
def psychological_test_5():
    if request.method == 'POST':
        user_responses['q5'] = request.form['social-activities']
        return redirect(url_for('psychological_test_6'))
    return render_template('psychological-test-5.html')

@app.route('/psychological-test-6', methods=['GET', 'POST'])
def psychological_test_6():
    global stress_level
    if request.method == 'POST':
        user_responses['q6'] = request.form['stress-level']
        score = 0
        response_scores = {
            'less-than-5': 1, '5-to-7': 2, 'more-than-7': 3,
            'daily': 1, 'weekly': 2, 'rarely': 3, 'never': 4,
            'never-rarely': 1, 'occasionally': 2, 'frequently': 3,
            'balanced': 1, 'slightly-unbalanced': 2, 'unbalanced': 3,
            'frequently-social': 1, 'occasionally-social': 2, 'rarely-social': 3,
            'almost-never': 1, 'occasionally': 2, 'often': 3, 'almost-always': 4
        }
        for response in user_responses.values():
            score += response_scores.get(response, 0)
        if score <= 6:
            stress_level = 1
        elif score <= 10:
            stress_level = 2
        elif score <= 14:
            stress_level = 3
        elif score <= 18:
            stress_level = 4
        else:
            stress_level = 5
        return redirect(url_for('stress_level'))
    return render_template('psychological-test-6.html')

@app.route('/stress-level')
def stress_level():
    return render_template('stress-level.html', stress_level=stress_level)

@app.route('/mental-health-report')
def mental_health_report():
    global user_name, user_age, latest_sensor_data, user_responses, stress_level

    # Set sample responses based on provided report
    user_responses = {
        'q1': 'less-than-5',        # Sleep less than 5 hours
        'q2': 'daily',              # Daily exercise
        'q3': 'never-rarely',       # Infrequent caffeine
        'q4': 'slightly-unbalanced', # Work-life imbalance
        'q5': 'rarely-social',      # Limited social engagement
        'q6': 'occasionally'        # Stress level occasionally
    }

    # Format psychological test responses
    psych_questions = {
        'q1': "How many hours do you sleep on average per night?",
        'q2': "How often do you exercise?",
        'q3': "How often do you consume caffeine?",
        'q4': "How would you describe your work-life balance?",
        'q5': "How often do you engage in social activities?",
        'q6': "How often do you feel stressed?"
    }
    psych_responses = "\n".join([f"{psych_questions[key]}: {user_responses.get(key, 'N/A')}" for key in psych_questions])

    # Create prompt for Groq
    prompt = f"""
Name: {user_name}
Age: {user_age}

Vitals:
- SpO2: {latest_sensor_data.get('spo2', 'N/A')} %
- GSR: {latest_sensor_data.get('gsr', 'N/A')} µS
- Pulse Rate: {latest_sensor_data.get('bpm', 'N/A')} bpm
- HRV: {latest_sensor_data.get('hrv', 'N/A')} ms

Psychological Test Responses:
{psych_responses}

Stress Level: {stress_level}

Generate a structured stress report in the following format in shot:
- Conclusion of Your Psychological and Sensor Data

- Recommendations & Precautions
    1. Recommendation 1 tailored to stress level and data
    2. Recommendation 2 tailored to stress level and data
    3. Recommendation 3 tailored to stress level and data
  - Precautions:
    1. Precaution 1 tailored to stress level and data
    2. Precaution 2 tailored to stress level and data
    3. Precaution 3 tailored to stress level and data

Ensure the content is short but correct, relevant to the provided data, and provided as plain text without markdown symbols (e.g., no #, *, or -). Place each point on a new line, and base the analysis and recommendations solely on the real-time vitals and psychological test responses provided above.
"""

    try:
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        report_content = completion.choices[0].message.content
        # Clean and parse report content
        conclusion_end = report_content.find("Recommendations & Precautions")
        if conclusion_end != -1:
            conclusion = report_content[:conclusion_end].strip().replace("Conclusion of Your Psychological and Sensor Data", "").strip()
            recommendations_precautions = report_content[conclusion_end:].strip().replace("Recommendations & Precautions", "").strip()
        else:
            conclusion = report_content
            recommendations_precautions = ""
        # Remove any residual markdown symbols
        conclusion = conclusion.replace("#", "").replace("*", "").replace("-", "").strip()
        recommendations_precautions = recommendations_precautions.replace("#", "").replace("*", "").replace("-", "").strip()
        session['report_conclusion'] = conclusion
        session['report_recommendations_precautions'] = recommendations_precautions
    except Exception as e:
        conclusion = f"Error generating report: {str(e)}"
        recommendations_precautions = ""
        session['report_conclusion'] = conclusion
        session['report_recommendations_precautions'] = recommendations_precautions

    return render_template('mental-health-report.html',
                           stress_level=stress_level,
                           sensor_data=latest_sensor_data,
                           user_name=user_name,
                           user_age=user_age,
                           report_conclusion=session.get('report_conclusion'),
                           report_recommendations_precautions=session.get('report_recommendations_precautions'))

@app.route('/download-report')
def download_report():
    global user_name, user_age, latest_sensor_data, user_responses, stress_level
    report_conclusion = session.get('report_conclusion', 'No report content available')
    report_recommendations_precautions = session.get('report_recommendations_precautions', 'No recommendations available')

    # Generate PDF content
    pdf_file = f"mental_health_report_{user_name}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    # Add title
    content.append(Paragraph("Mental Health Report", styles['Heading1']))
    content.append(Spacer(1, 12))

    # Add user details
    details = f"""
    <b>Name:</b> {user_name}<br/>
    <b>Age:</b> {user_age}<br/>
    <b>Stress Level:</b> {stress_level} {'(Low Stress)' if stress_level <= 2 else '(High Stress)'}<br/>
    <b>SpO2:</b> {latest_sensor_data.get('spo2', 'N/A')} %<br/>
    <b>GSR:</b> {latest_sensor_data.get('gsr', 'N/A')} µS<br/>
    <b>Pulse Rate:</b> {latest_sensor_data.get('bpm', 'N/A')} bpm<br/>
    <b>HRV:</b> {latest_sensor_data.get('hrv', 'N/A')} ms
    """
    content.append(Paragraph(details, styles['Normal']))
    content.append(Spacer(1, 12))

    # Add report sections
    content.append(Paragraph("Conclusion of Your Psychological and Sensor Data", styles['Heading2']))
    content.append(Paragraph(report_conclusion, styles['Normal']))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Recommendations & Precautions", styles['Heading2']))
    content.append(Paragraph(report_recommendations_precautions, styles['Normal']))

    # Build PDF
    doc.build(content)
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



































    # from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, session
# import time
# import pandas as pd
# from groq import Groq
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# import os
# import subprocess
# import signal

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Required for session; replace with a secure key in production

# # Read sensor data from file
# df = pd.read_csv("sensor_data.txt", header=None)  # Read as a single-column DataFrame

# # Initialize Groq client
# client = Groq(api_key="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")

# # Global variables
# reading_enabled = False
# sensor_data_history = {'pulse_rate': [], 'timestamps': []}
# latest_sensor_data = {'pulse_rate': 'N/A', 'ecg': 'N/A', 'gsr': 'N/A', 'spo2': 'N/A'}
# user_responses = {}
# stress_level = 2  # Set to 2 based on your sample (low stress)
# user_name = "Aayush"  # Set to Aayush based on your sample
# user_age = 19       # Set to 19 based on your sample
# arduino_process = None  # To store the background process

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     global user_name, user_age
#     if request.method == 'POST':
#         user_name = request.form['name']
#         user_age = int(request.form['age'])
#         return redirect(url_for('next_page'))
#     return render_template('index.html')

# @app.route('/next-page')
# def next_page():
#     return render_template('next-page.html')

# @app.route('/start_reading', methods=['POST'])
# def start_reading():
#     global reading_enabled, arduino_process
#     if not reading_enabled:
#         reading_enabled = True
#         # Run the Arduino reading script in the background
#         arduino_process = subprocess.Popen(['python', 'read_arduino.py'], 
#                                          stdout=subprocess.PIPE, 
#                                          stderr=subprocess.PIPE)
#         return jsonify({'status': 'Reading started'})
#     return jsonify({'status': 'Already reading'})

# @app.route('/stop_reading', methods=['POST'])
# def stop_reading():
#     global reading_enabled, arduino_process
#     if reading_enabled and arduino_process:
#         reading_enabled = False
#         # Terminate the background process
#         if arduino_process.poll() is None:  # Check if process is still running
#             arduino_process.terminate()
#             try:
#                 arduino_process.wait(timeout=5)  # Wait for clean termination
#             except subprocess.TimeoutExpired:
#                 arduino_process.kill()  # Force kill if it doesn't terminate
#         arduino_process = None
#         return jsonify({'status': 'Reading stopped'})
#     return jsonify({'status': 'Not reading'})

# @app.route('/get_sensor_data')
# def get_sensor_data():
#     global reading_enabled, sensor_data_history, latest_sensor_data
#     if not reading_enabled:
#         return jsonify({
#             'pulse_rate': 'N/A',
#             'ecg': 'N/A',
#             'gsr': 'N/A',
#             'spo2': 'N/A',
#             'error': 'Reading not enabled'
#         })

#     try:
#         # Read the latest sensor data from the text file (updated by read_arduino.py)
#         with open('sensor_data.txt', 'r') as file:
#             lines = file.readlines()
#             if len(lines) >= 4:
#                 pulse_rate = float(lines[0].strip())
#                 ecg = float(lines[1].strip())
#                 gsr = float(lines[2].strip())
#                 spo2 = float(lines[3].strip())
#             else:
#                 raise ValueError("Insufficient data in sensor_data.txt")

#         current_time = time.strftime('%H:%M:%S')
#         sensor_data_history['pulse_rate'].append(pulse_rate)
#         sensor_data_history['timestamps'].append(current_time)
#         if len(sensor_data_history['pulse_rate']) > 10:
#             sensor_data_history['pulse_rate'].pop(0)
#             sensor_data_history['timestamps'].pop(0)

#         latest_sensor_data['pulse_rate'] = pulse_rate
#         latest_sensor_data['ecg'] = ecg
#         latest_sensor_data['gsr'] = gsr
#         latest_sensor_data['spo2'] = spo2

#         return jsonify({
#             'pulse_rate': pulse_rate,
#             'ecg': ecg,
#             'gsr': gsr,
#             'spo2': spo2,
#             'error': None
#         })
#     except Exception as e:
#         return jsonify({
#             'pulse_rate': 'N/A',
#             'ecg': 'N/A',
#             'gsr': 'N/A',
#             'spo2': 'N/A',
#             'error': str(e)
#         })

# @app.route('/get_chart_data')
# def get_chart_data():
#     return jsonify(sensor_data_history)

# @app.route('/psychological-test', methods=['GET', 'POST'])
# def psychological_test():
#     if request.method == 'POST':
#         user_responses['q1'] = request.form['sleep-hours']
#         return redirect(url_for('psychological-test_2'))
#     return render_template('psychological-test.html')

# @app.route('/psychological-test-2', methods=['GET', 'POST'])
# def psychological_test_2():
#     if request.method == 'POST':
#         user_responses['q2'] = request.form['exercise-frequency']
#         return redirect(url_for('psychological-test_3'))
#     return render_template('psychological-test-2.html')

# @app.route('/psychological-test-3', methods=['GET', 'POST'])
# def psychological_test_3():
#     if request.method == 'POST':
#         user_responses['q3'] = request.form['caffeine-frequency']
#         return redirect(url_for('psychological-test_4'))
#     return render_template('psychological-test-3.html')

# @app.route('/psychological-test-4', methods=['GET', 'POST'])
# def psychological_test_4():
#     if request.method == 'POST':
#         user_responses['q4'] = request.form['work-life-balance']
#         return redirect(url_for('psychological-test_5'))
#     return render_template('psychological-test-4.html')

# @app.route('/psychological-test-5', methods=['GET', 'POST'])
# def psychological_test_5():
#     if request.method == 'POST':
#         user_responses['q5'] = request.form['social-activities']
#         return redirect(url_for('psychological-test_6'))
#     return render_template('psychological-test-5.html')

# @app.route('/psychological-test-6', methods=['GET', 'POST'])
# def psychological_test_6():
#     global stress_level
#     if request.method == 'POST':
#         user_responses['q6'] = request.form['stress-level']
#         score = 0
#         response_scores = {
#             'less-than-5': 1, '5-to-7': 2, 'more-than-7': 3,
#             'daily': 1, 'weekly': 2, 'rarely': 3, 'never': 4,
#             'never-rarely': 1, 'occasionally': 2, 'frequently': 3,
#             'balanced': 1, 'slightly-unbalanced': 2, 'unbalanced': 3,
#             'frequently-social': 1, 'occasionally-social': 2, 'rarely-social': 3,
#             'almost-never': 1, 'occasionally': 2, 'often': 3, 'almost-always': 4
#         }
#         for response in user_responses.values():
#             score += response_scores.get(response, 0)
#         if score <= 6:
#             stress_level = 1
#         elif score <= 10:
#             stress_level = 2
#         elif score <= 14:
#             stress_level = 3
#         elif score <= 18:
#             stress_level = 4
#         else:
#             stress_level = 5
#         return redirect(url_for('stress_level'))
#     return render_template('psychological-test-6.html')

# @app.route('/stress-level')
# def stress_level():
#     return render_template('stress-level.html', stress_level=stress_level)

# @app.route('/mental-health-report')
# def mental_health_report():
#     global user_name, user_age, latest_sensor_data, user_responses, stress_level

#     # Set sample responses based on your provided report
#     user_responses = {
#         'q1': 'less-than-5',        # Sleep less than 5 hours
#         'q2': 'daily',              # Daily exercise
#         'q3': 'never-rarely',       # Infrequent caffeine
#         'q4': 'slightly-unbalanced', # Work-life imbalance
#         'q5': 'rarely-social',      # Limited social engagement
#         'q6': 'occasionally'        # Stress level occasionally
#     }

#     # Format psychological test responses
#     psych_questions = {
#         'q1': "How many hours do you sleep on average per night?",
#         'q2': "How often do you exercise?",
#         'q3': "How often do you consume caffeine?",
#         'q4': "How would you describe your work-life balance?",
#         'q5': "How often do you engage in social activities?",
#         'q6': "How often do you feel stressed?"
#     }
#     psych_responses = "\n".join([f"{psych_questions[key]}: {user_responses.get(key, 'N/A')}" for key in psych_questions])

#     # Create prompt for Groq with new lines between points
#     prompt = f"""
# Name: {user_name}
# Age: {user_age}

# Vitals:
# - Pulse Rate: {latest_sensor_data.get('pulse_rate', 'N/A')} bpm
# - SpO2: {latest_sensor_data.get('spo2', 'N/A')} %
# - HRV: {latest_sensor_data.get('ecg', 'N/A')} ms
# - GSR: {latest_sensor_data.get('gsr', 'N/A')} µS

# Psychological Test Responses:
# {psych_responses}

# Stress Level: {stress_level}

# Generate a structured stress report in the following format in shot:
# - Conclusion of Your Psychological and Sensor Data

# - Recommendations & Precautions
#     1. Recommendation 1 tailored to stress level and data
#     2. Recommendation 2 tailored to stress level and data
#     3. Recommendation 3 tailored to stress level and data
#   - Precautions:
#     1. Precaution 1 tailored to stress level and data
#     2. Precaution 2 tailored to stress level and data
#     3. Precaution 3 tailored to stress level and data

# Ensure the content is short but correct, relevant to the provided data, and provided as plain text without markdown symbols (e.g., no #, *, or -). Place each point on a new line, and base the analysis and recommendations solely on the real-time vitals and psychological test responses provided above.
# """

#     try:
#         completion = client.chat.completions.create(
#             model="gemma2-9b-it",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1,
#             max_tokens=1024,
#             top_p=1,
#             stream=False
#         )
#         report_content = completion.choices[0].message.content
#         # Clean and parse report content
#         conclusion_end = report_content.find("Recommendations & Precautions")
#         if conclusion_end != -1:
#             conclusion = report_content[:conclusion_end].strip().replace("Conclusion of Your Psychological and Sensor Data", "").strip()
#             recommendations_precautions = report_content[conclusion_end:].strip().replace("Recommendations & Precautions", "").strip()
#         else:
#             conclusion = report_content
#             recommendations_precautions = ""
#         # Remove any residual markdown symbols
#         conclusion = conclusion.replace("#", "").replace("*", "").replace("-", "").strip()
#         recommendations_precautions = recommendations_precautions.replace("#", "").replace("*", "").replace("-", "").strip()
#         session['report_conclusion'] = conclusion
#         session['report_recommendations_precautions'] = recommendations_precautions
#     except Exception as e:
#         conclusion = f"Error generating report: {str(e)}"
#         recommendations_precautions = ""
#         session['report_conclusion'] = conclusion
#         session['report_recommendations_precautions'] = recommendations_precautions

#     return render_template('mental-health-report.html',
#                            stress_level=stress_level,
#                            sensor_data=latest_sensor_data,
#                            user_name=user_name,
#                            user_age=user_age,
#                            report_conclusion=session.get('report_conclusion'),
#                            report_recommendations_precautions=session.get('report_recommendations_precautions'))

# @app.route('/download-report')
# def download_report():
#     global user_name, user_age, latest_sensor_data, user_responses, stress_level
#     report_conclusion = session.get('report_conclusion', 'No report content available')
#     report_recommendations_precautions = session.get('report_recommendations_precautions', 'No recommendations available')

#     # Generate PDF content
#     pdf_file = f"mental_health_report_{user_name}.pdf"
#     doc = SimpleDocTemplate(pdf_file, pagesize=letter)
#     styles = getSampleStyleSheet()
#     content = []

#     # Add title
#     content.append(Paragraph("Mental Health Report", styles['Heading1']))
#     content.append(Spacer(1, 12))

#     # Add user details
#     details = f"""
#     <b>Name:</b> {user_name}<br/>
#     <b>Age:</b> {user_age}<br/>
#     <b>Stress Level:</b> {stress_level} {'(Low Stress)' if stress_level <= 2 else '(High Stress)'}<br/>
#     <b>Pulse Rate:</b> {latest_sensor_data.get('pulse_rate', 'N/A')} bpm<br/>
#     <b>SpO2:</b> {latest_sensor_data.get('spo2', 'N/A')} %<br/>
#     <b>HRV:</b> {latest_sensor_data.get('ecg', 'N/A')} ms<br/>
#     <b>GSR:</b> {latest_sensor_data.get('gsr', 'N/A')} µS
#     """
#     content.append(Paragraph(details, styles['Normal']))
#     content.append(Spacer(1, 12))

#     # Add report sections
#     content.append(Paragraph("Conclusion of Your Psychological and Sensor Data", styles['Heading2']))
#     content.append(Paragraph(report_conclusion, styles['Normal']))
#     content.append(Spacer(1, 12))
#     content.append(Paragraph("Recommendations & Precautions", styles['Heading2']))
#     content.append(Paragraph(report_recommendations_precautions, styles['Normal']))

#     # Build PDF
#     doc.build(content)
#     return send_file(pdf_file, as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)












