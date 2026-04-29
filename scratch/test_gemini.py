import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment.")
        return

    print(f"Attempting to connect to Gemini with API Key: {api_key[:10]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key.strip())
        
        print("\nAvailable Models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        model = genai.GenerativeModel('gemini-3.1-pro-preview')
        
        # Simple test prompt
        response = model.generate_content("Say 'Gemini API is working fine!'")
        
        print("\n--- API Response ---")
        print(response.text)
        print("--------------------")
        print("\nSUCCESS: The Gemini API key is working correctly!")
        
    except Exception as e:
        print(f"\nFAILURE: Could not connect to Gemini API.")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    test_gemini()
