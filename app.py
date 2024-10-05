import requests
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_template', methods=['POST'])
def create_template():
    # Extract data from the request
    account_id = request.form['account_id']
    waba_id = request.form['waba_id']
    username = request.form['username']
    password = request.form['password']
    template_name = request.form['template_name']
    language = request.form['language']
    category = request.form['category']
    main_body_text = request.form['main_body_text']
    num_cards = int(request.form['num_cards'])

    cards = []
    for i in range(num_cards):
        card_body_text = request.form[f'card_body_text_{i}']
        image_handle = request.form[f'image_handle_{i}']
        buttons = []

        num_buttons = int(request.form[f'num_buttons_{i}'])
        for j in range(num_buttons):
            button_type = request.form[f'button_type_{i}_{j}']
            button_text = request.form[f'button_text_{i}_{j}']
            button_data = {
                "type": button_type,
                "text": button_text
            }

            if button_type == "URL":
                button_data["url"] = request.form[f'button_url_{i}_{j}']

            buttons.append(button_data)

        cards.append({
            "image_handle": image_handle,
            "body_text": card_body_text,
            "buttons": buttons
        })

    data = {
        "whatsapp": {
            "templates": [
                {
                    "template": {
                        "name": template_name,
                        "language": language,
                        "category": category,
                        "components": [
                            {
                                "type": "BODY",
                                "text": main_body_text
                            },
                            {
                                "type": "CAROUSEL",
                                "cards": []
                            }
                        ]
                    }
                }
            ]
        }
    }

    for card in cards:
        card_data = {
            "components": [
                {
                    "type": "HEADER",
                    "format": "IMAGE",
                    "example": {
                        "header_handle": [card["image_handle"]]
                    }
                },
                {
                    "type": "BODY",
                    "text": card["body_text"]
                },
                {
                    "type": "BUTTONS",
                    "buttons": card["buttons"]
                }
            ]
        }
        data["whatsapp"]["templates"][0]["template"]["components"][1]["cards"].append(card_data)

    # Determine the API URL based on account_id format using regex
    if re.search(r'\d+m$', account_id):  # Matches any digits followed by 'm' at the end
        api_url = f"https://api.in.exotel.com/v2/accounts/{account_id}/templates?waba_id={waba_id}"
    else:
        api_url = f"https://api.exotel.com/v2/accounts/{account_id}/templates?waba_id={waba_id}"

    # Print the request data for debugging
    print("Request data being sent to Exotel:")
    print("API URL:", api_url)
    print("Payload:", data)

    # Make API request to Exotel
    response = requests.post(api_url, json=data, auth=(username, password))

    # Check the response and return it to the user
    if response.ok:
        return jsonify({"status": "success", "data": response.json()})
    else:
        return jsonify({"status": "error", "message": response.text}), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=5001)