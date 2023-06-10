import requests

def is_valid_pair(pair):
    """
    Check if a pair is valid by making a request to Oanda's API.
    """
    url = f"https://api-fxtrade.oanda.com/v3/instruments/{pair}/candles"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-access-token',  # Replace with your Oanda access token
    }
    params = {'count': 1}  # We only need one data point to check validity

    response = requests.get(url, headers=headers, params=params)

    return response.status_code == 200  # If the response code is 200, the pair is valid

# Common currency codes in Forex
currency_codes = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "NZD"]

# Write valid pairs to file
with open("Pairs.txt", "w") as file:
    for i in range(len(currency_codes)):
        for j in range(i + 1, len(currency_codes)):
            pair1 = f"{currency_codes[i]}_{currency_codes[j]}"
            pair2 = f"{currency_codes[j]}_{currency_codes[i]}"
            
            if is_valid_pair(pair1):
                file.write(f"{pair1}\n")
            
            if is_valid_pair(pair2):
                file.write(f"{pair2}\n")
