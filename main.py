import openai #imports official OpenAI API
from flask import Flask, request, jsonify
#Flask --> creates instance of Flask application
#request --> encapsulates HTTP request data and process requests
#jsonify --> returns a response object containing the JSON of given arguments

#For environment vars
import os
from dotenv import load_dotenv

#api call to nutrition database
import requests
import json
load_dotenv("C:\\Users\\mahir\\PycharmProjects\\FitnessGPT\\venv\\.env")
openai.api_key = os.getenv("OPENAI_API_KEY")
print("API KEY:")
print(openai.api_key)
app = Flask(__name__)

#make api calls to gpt
def chat_with_gpt3(prompt):
    model_engine = "text-davinci-001"
    #make a request to GPT
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100 #limit responses to 50 tokens
    )
    return response.choices[0].text.strip()

#create a Flask route to handle incoming user queries --> will recieve a POST request containing user query
@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query', '')
    follow_up_response = request.json.get('follow_up', '')

    if not user_query:
        return jsonify({'error': 'Query is empty'}), 400

    refined_query = refine_query(user_query)
    follow_up = generate_follow_up(user_query)

    #check for food item
    if follow_up and follow_up_response:
        food_item = follow_up_response
        calorie_info = nutritionix_calorie_info(food_item)
        gpt_response = f"According to the Nutritionix database,{food_item} typically contains {calorie_info} calories."
    else:
        gpt_response = chat_with_gpt3(refined_query)

    processed_response = process_response(gpt_response)

    return jsonify({
        'query': user_query,
        'refined_query': refined_query,
        'gpt_response': gpt_response,
        'processed response': processed_response,
        'follow_up': follow_up
    })

#refine user query
def refine_query(user_query):
    #basic refinement --> eventually have more sophisticated logic
    refined_query = f"Tell me about {user_query}"
    return refined_query

#generate follow up questions based on user input
def generate_follow_up(user_query):
    if "weight" in user_query.lower():
        return "Are you interested in diet, exercise, or both?"
    if "calorie" in user_query.lower():
        return "What food are you interested in?"
    return None

#process the response to gpt --> either filter or cross-reference, format, or add info
def process_response(gpt_response):
    #cross reference for accuracy
    gpt_response = cross_reference(gpt_response)

    return gpt_response

#create a dict of verified info --> better approach is an external file or db that can hold more info
verified_info = {
    "weight loss": {
        "general": "It's generally recommended to combine a balanced diet with regular exercise for effective weight loss.",
        "fasting": "Fasting can be effective for weight loss but should be done under medical supervision.",
        "carb-cycling": "Carb cycling involves alternating high-carb and low-carb days, and may aid in weight loss or body composition changes."
    },
    "protein sources": {
        "animal": "Chicken, fish, and lean meats are excellent sources of protein.",
        "plant": "Legumes, nuts, and seeds are good plant-based sources of protein."
    }
}

def cross_reference(gpt_response):
    for key, value in verified_info.items():
        if key in gpt_response.lower():
            gpt_response += f" Note: {value}"
    return gpt_response

#fetch calorie info on food
def nutritionix_calorie_info(food_item):
    #API endpoint
    api_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": os.environ.get("NUTRITIONIX_APP_ID"),
        "x-app-key": os.environ.get("NUTRITIONIX_API_KEY"),
        "Content-Type": "application/json"
    }

    #Data payload
    data = {
        "query": food_item
    }
    #API request
    response = requests.post(api_url,headers=headers, json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Raw Response: {response.text}")

    #Extract calorie info from api
    if response.status_code == 200:
        try:
            food_data = response.json()
            # Extract calorie information
            calories = food_data['foods'][0]['nf_calories']
            print(f"According to the Nutirionix database, The food item '{food_item}' contains {calories} calories.")
            return calories
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    else:
        print("Failed to get data:", response.status_code, response.text)
        return None

#Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
