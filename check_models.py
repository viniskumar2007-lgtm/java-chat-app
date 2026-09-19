import streamlit as st
from google import genai


api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in .streamlit/secrets.toml"
    )

client = genai.Client(api_key=api_key)

print("Models available for your API key:")
print("-" * 60)

found_model = False

for model in client.models.list():
    name = getattr(model, "name", "")
    actions = getattr(model, "supported_actions", [])

    print(f"Name: {name}")
    print(f"Supported actions: {actions}")
    print("-" * 60)

    if "generateContent" in actions:
        found_model = True

if not found_model:
    print("No generateContent model is available for this API key.")