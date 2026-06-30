import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def get_llm_response(user_input: str, correction_instruction: str = None) -> str:
    system_message = "You are a helpful, safe, and professional AI assistant."

    if correction_instruction:
        system_message += f" IMPORTANT CORRECTION: {correction_instruction}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"ERROR: Could not get response from LLM. Details: {str(e)}"
    

def classify_output_against_policy(llm_response: str, blocked_topics: list) -> dict:
    topics_str = ", ".join(blocked_topics)

    classifier_prompt = f"""You are a strict content policy classifier. Your job is to flag ONLY clear, direct violations — not general or tangentially related content.

Blocked topics: {topics_str}

Rules:
- Flag "medical advice" ONLY if the response recommends specific medications, dosages, or treatments for an illness/symptom.
- Flag "legal advice" ONLY if the response gives specific legal recommendations for a real legal situation.
- General wellness, fitness, nutrition, or lifestyle tips are NOT medical advice.
- General information or factual answers are NOT violations.
- When in doubt, say no violation.

AI Response to analyze:
\"\"\"{llm_response}\"\"\"

Reply ONLY in this exact format, nothing else:
VIOLATION: yes or no
TOPIC: the specific blocked topic if violation is yes, otherwise none"""

    try:
        result = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a strict content policy classifier. Follow the output format exactly."},
                {"role": "user", "content": classifier_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=50
        )

        output_text = result.choices[0].message.content.strip()

        violation = "yes" in output_text.lower().split("violation:")[1].split("\n")[0].lower()
        topic_line = output_text.lower().split("topic:")[1].strip() if "topic:" in output_text.lower() else "none"

        return {"violation": violation, "topic": topic_line}

    except Exception:
        return {"violation": False, "topic": "none"}
    

