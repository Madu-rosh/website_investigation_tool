from openai import OpenAI, RateLimitError
import json

def analyze_site(report, user_api_key):
    """Analyze the site using OpenAI and return a description."""
    
    client = OpenAI(api_key=user_api_key)

    prompt = f"Analyze the following website report and provide a detailed description about the site's nature, infrastructure, and tech stack. Highlight any important details:\n\n{json.dumps(report, indent=4)}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a well-experienced cloud and web developer with expertise in software architectures and cloud computing."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        description = response.choices[0].message.content.strip()
        return description
    except RateLimitError as e:
        return f"Error: Rate limit exceeded. Please try again later.\nDetails: {e}"
    except Exception as e:  # Catch any other unexpected errors
        return f"Error: An unexpected error occurred.\nDetails: {e}"

if __name__ == "__main__":
    # Example usage
    with open("report.json", "r") as file:
        report = json.load(file)
        api_key = "your_openai_api_key"
        description = analyze_site(report, api_key)
        print(description)