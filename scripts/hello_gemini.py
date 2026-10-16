from dotenv import load_dotenv
from google import genai

load_dotenv()            # reads .env, so GEMINI_API_KEY becomes available
client = genai.Client()  # finds GEMINI_API_KEY automatically

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Say hello in five words.",
)
print(interaction.output_text)