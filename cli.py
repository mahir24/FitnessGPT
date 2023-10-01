import requests

#interact with api
def send_query_to_api(query, follow_up=None):
    payload = {
        'query': query
    }

    #If there is a followup response,add it to the payload
    if follow_up:
        payload['follow_up'] = follow_up

    #send POST request
    response = requests.post('http://127.0.0.1:5000/query', json=payload)

    return response.json()

def main():
    print("Welcome to FitnessGPT! Type 'quit' to exit.")

    #infinte loop until user quits
    while True:
        user_query = input("You: ")

        if user_query.lower() =='quit':
            print("FitnessGPT: Goodbye!")
            break

        #send query to api
        api_response = send_query_to_api(user_query)

        #display response
        print(f"FitnessGPT: {api_response.get('gpt_response', 'Sorry, I did not get that.')}")

        #check for follow-up questions
        follow_up = api_response.get('follow_up')
        if follow_up:
            # After the first API call
            print(f"\nDebug: First API response: {api_response}\n")

            follow_up_response = input(f"FitnessGPT: {follow_up} \n You: ")
            follow_up_api_response = send_query_to_api(user_query, follow_up_response)
            # After the second API call
            print(f"\nDebug: Follow-up API response: {follow_up_api_response}\n")
            print(f"FitnessGPT: {follow_up_api_response.get('gpt_response', 'Sorry, I did not get that.')}")

if __name__ == "__main__":
    main()


