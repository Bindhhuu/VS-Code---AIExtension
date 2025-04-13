import os
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def generate_code(task):
    payload = {
        "inputs": (
            "Write only code.\n\n"
            f"Task: {task}\n"
            "Code:\n"
        ),
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.2
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        generated_text = response.json()[0]['generated_text']
        # Extract only the code part
        if "Code:" in generated_text:
            code = generated_text.split("Code:")[-1].strip()
        else:
            code = generated_text.split("Task:")[-1].strip()
        
        # Clean up any remaining task text
        if task in code:
            code = code.replace(task, '').strip()
        
        # Remove empty lines and clean up
        cleaned_code = '"""'+ '\n'.join(line for line in code.split('\n') if line.strip())
        return cleaned_code
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

def main():
    task = input("📝 Enter your task: ")

    while True:
        code = generate_code(task)
        if not code:
            print("⚠️ Failed to generate code.")
            break

        print("\n📋 Generated Code:\n---------------------")
        print(code)

        proceed = input("\n✅ Proceed with this code? (yes/no): ").strip().lower()
        if proceed != "yes":
            print("❌ Task cancelled.")
            break

        with open("generated_script.py", "w") as f:
            f.write(code)

        print("\n💾 Code saved to 'generated_script.py'")
        print("⚙️ Executing the script...\n")
        subprocess.run(["python", "generated_script.py"], shell=True)

        success = input("\n❓ Was the task successful? (yes/no): ").strip().lower()
        if success == "yes":
            print("🎉 Task completed successfully!")
            break
        else:
            feedback = input("🛠️ What went wrong? Describe the issue: ")
            task += f"\nNote: The previous version failed because: {feedback}"
            print("\n🔁 Retrying with refined instructions...")

if __name__ == "__main__":
    main()
