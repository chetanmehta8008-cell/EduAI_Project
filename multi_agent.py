import os
import json
import re
from database import create_table, save_note, get_note
from image_gen import generate_concept_images
from groq import Groq

os.environ["GROQ_API_KEY"] = "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"

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def parse_flashcards(raw: str) -> list:
    try:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            cards = json.loads(match.group())
            if isinstance(cards, list):
                return cards
    except Exception:
        pass
    return []

def ask_groq(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content

def run_education_system(topic: str, difficulty: str = "Intermediate"):
    create_table()

    # Return from cache instantly
    existing_content, existing_flashcards, existing_images, _ = get_note(topic)
    if existing_content:
        return existing_content, existing_flashcards, existing_images

    # ── Notes ────────────────────────────────────────────────────────────
    notes_prompt = f"""
You are an expert educator. Write structured study notes on: **{topic}** at {difficulty} level.

Format:
- Use ## headers for each section
- Bold all key terms
- Include: Definition, How it works, Key concepts, Real-world examples, Common mistakes
- End with a ## Quick Summary section
- Keep it 400-500 words, clear and student-friendly
"""
    notes_content = ask_groq(notes_prompt)

    # ── Flashcards ───────────────────────────────────────────────────────
    flashcard_prompt = f"""
Based on this topic: {topic} ({difficulty} level)

Generate exactly 6 flashcards. Output ONLY a valid JSON array, no extra text, no markdown.

[
  {{
    "question": "specific question",
    "answer": "concise answer in 1-2 sentences",
    "hint": "one word hint"
  }}
]
"""
    flashcard_raw = ask_groq(flashcard_prompt)
    flashcards = parse_flashcards(flashcard_raw)

    # ── Images ───────────────────────────────────────────────────────────
    image_paths = generate_concept_images(topic, [])

    save_note(topic, notes_content, flashcards, image_paths, difficulty)

    return notes_content, flashcards, image_paths