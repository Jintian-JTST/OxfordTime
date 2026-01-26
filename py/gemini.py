from google import genai

with open("D:/Users/JTST/Desktop/Desktop/JTST/.Oxford/gemini api key.txt", "r") as file:
    api_key = file.read().strip()

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="hello!",
)

print(response.text)