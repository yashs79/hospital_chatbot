import os
import re
import google.generativeai as genai
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Load the CSV file containing doctor details
doctors_df = pd.read_csv('data/doctors_sample_data.csv')

# Configure the API key
genai.configure(api_key="Your_key")

def get_specialties_from_csv(file_path='data/doctors_sample_data.csv'):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        # Extract unique specialties
        specialties = df['specialty'].unique().tolist()
        return specialties
    except Exception as e:
        print(f"Error reading specialties from CSV: {e}")
        return []

def suggest_specialist(symptoms, specialties):
    # Create the prompt with symptoms and specialties
    prompt = f"I'm in a hospital and the available specialists are: {specialties}. My symptoms are: {', '.join(symptoms)}. Suggest the most suitable specialist to visit for a checkup. Note the answer should be a single word i.e. the name of the healthcare professional, for example physiotherapist."
    
    # Use Google GenAI model to generate a response
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    # Extract the suggested specialist from the response
    return response.text

# Function to get doctor details based on specialization
def get_doctors_by_specialization(specialization):
    # Escape any special regex characters in the specialization string
    escaped_specialization = re.escape(specialization)
    # Filter doctors based on the escaped specialization
    filtered_doctors = doctors_df[doctors_df['specialty'].str.contains(escaped_specialization, case=False, na=False)]
    return filtered_doctors[['name', 'specialty', 'building_number', 'floor_number', 'room_number']].to_dict(orient='records')

@app.route('/get_specialist', methods=['POST'])
def get_specialist():
    data = request.get_json()
    symptoms = data.get('symptoms', [])
    
    # Fetch available specialties
    specialties = get_specialties_from_csv()

    # Suggest the best specialist based on the symptoms and available specialties
    suggested_specialist = suggest_specialist(symptoms, specialties)
    
    # Log the suggested specialist
    print(f"Suggested Specialist: {suggested_specialist}")  # Debug log

    if suggested_specialist:
        # Get the doctors matching the suggested specialist
        doctors = get_doctors_by_specialization(suggested_specialist.strip())  # Strip any whitespace

        # Log the filtered doctors
        print(f"Filtered Doctors: {doctors}")  # Debug log

        return jsonify({"specialist": suggested_specialist.strip(), "doctors": doctors}), 200
    else:
        return jsonify({"error": "Unable to suggest a specialist."}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
