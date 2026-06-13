import requests

def main():
    base_url = "https://bsgmarian-devsuite-apis.hf.space"
    
    # 1. Test home page
    print("Testing home page...")
    res = requests.get(base_url)
    print("Home page status:", res.status_code)
    
    # 2. Test credit card validator
    print("\nTesting credit card validator...")
    res = requests.post(f"{base_url}/creditcardvalidator/validate", json={"card_number": "4111111111111111"})
    print("Status:", res.status_code)
    print("Response:", res.json())

    # 3. Test markdown to html
    print("\nTesting markdown converter...")
    res = requests.post(f"{base_url}/markdowntohtml/convert", json={"markdown_text": "# Title\nHello *world*"})
    print("Status:", res.status_code)
    print("Response:", res.json())

    # 4. Test phone number validator
    print("\nTesting phone number validator...")
    res = requests.post(f"{base_url}/phonenumbervalidator/validate/", json={"phone_number": "+14155552671", "country_code": "US"})
    print("Status:", res.status_code)
    print("Response:", res.json())

if __name__ == "__main__":
    main()
