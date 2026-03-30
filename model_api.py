from huggingface_hub import InferenceClient
import os

def query_model(prompt):
    try:
        HF_TOKEN = os.getenv("HF_TOKEN")
        # You can also set provider at the client level
        client = InferenceClient(api_key=HF_TOKEN, provider="auto")
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": "You are a professional fitness trainer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
