from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def classify_preferences(preference_str):
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions = """
            You are a course scheduling assistant. Parse the user's scheduling preferences into a JSON array of constraints.

            Available constraint types:
            - {"type": "start_after", "time": "H:MM a.m./p.m.", "days": ["Mon","Tue","Wed","Thu","Fri"] or null}
            - {"type": "end_before", "time": "H:MM a.m./p.m.", "days": [...] or null}
            - {"type": "free_block", "start_time": "H:MM a.m./p.m.", "end_time": "H:MM a.m./p.m.", "days": [...] or null}
            - {"type": "avoid_days", "days": ["Mon","Tue","Wed","Thu","Fri"]}
            - {"type": "prefer_days", "days": ["Mon","Tue","Wed","Thu","Fri"]}
            - {"type": "avoid_time", "period": "morning" | "afternoon" | "evening", "days": [...] or null}
            - {"type": "prefer_time", "period": "morning" | "afternoon" | "evening", "days": [...] or null}
            - {"type": "minimize_gaps"}
            - {"type": "unsupported", "preference": "<original text of unsupported preference>"}

            Rules:
            - Return ONLY a valid JSON array, no explanation, no markdown, no backticks
            - Days must be abbreviated: Mon, Tue, Wed, Thu, Fri, Sat, Sun
            - Times must be in format "H:MM a.m." or "H:MM p.m."
            - If a preference matches no constraint type, include it as unsupported
            - Split compound preferences into separate constraints

            Example input: "no classes before 11am, keep thursdays free, i want professor smith"
            Example output: [{"type": "start_after", "time": "11:00 a.m."}, {"type": "avoid_days", "days": ["Thu"]}, {"type": "unsupported", "preference": "i want professor smith"}]
        """,
        input=preference_str
    )

    return response.output_text