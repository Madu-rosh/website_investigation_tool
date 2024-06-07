import openai
import json

def analyze_site(report, api_key):
    """Analyze the site using OpenAI and return a description."""
    openai.api_key = api_key
    prompt = f"Analyze the following website report and provide a detailed description about the site's nature, infrastructure, and tech stack. Highlight any important details:\n\n{json.dumps(report, indent=4)}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a well-experienced cloud and web developer with expertise in software architectures and cloud computing."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )

    description = response.choices[0].message['content'].strip()
    return description

if __name__ == "__main__":
    # Example usage
    with open("report.json", "r") as file:
        report = json.load(file)
        api_key = "your_openai_api_key"
        description = analyze_site(report, api_key)
        print(description)