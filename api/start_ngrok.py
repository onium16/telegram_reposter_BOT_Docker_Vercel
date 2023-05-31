import requests
import time


def get_public_url(token):
    try:
        time.sleep(10)
        ngrok_response = requests.get('http://localhost:4040/api/tunnels')
        if ngrok_response.status_code == 200:
            ngrok_data = ngrok_response.json()
            if 'tunnels' in ngrok_data and ngrok_data['tunnels']:
                NGROK_PUBLIC_URL = ngrok_data['tunnels'][0]['public_url']
                bot_token = token
                response = requests.get(f"https://api.telegram.org/bot{token}/setWebhook?url={NGROK_PUBLIC_URL}/webhook")
                if response.status_code == 200:
                    json_response = response.json()
                    print(token)
                    print(NGROK_PUBLIC_URL)
                    print(response.status_code)
                    print(json_response)
                else:
                    print(f"Webhook registration failed. Status code: {response.status_code}")
            else:
                print("No ngrok tunnels found.")
        else:
            print(f"Failed to get ngrok tunnels. Status code: {ngrok_response.status_code}")
    except (requests.RequestException, ValueError) as e:
        print(f"An error occurred: {e}")
