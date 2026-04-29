import os
import re
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont
import textwrap

IMAGE_DIR = "generated_images"
HF_API_KEY = "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"

def sanitize_filename(text: str) -> str:
    safe = re.sub(r'[^\w\s-]', '', text).strip()
    safe = re.sub(r'\s+', '_', safe)
    return safe[:60]

def generate_concept_images(topic: str, flashcards: list) -> list:
    os.makedirs(IMAGE_DIR, exist_ok=True)
    saved_paths = []
    path = _generate_single_image(topic)
    if path:
        saved_paths.append(path)
    return saved_paths

def _generate_single_image(topic: str):
    try:
        prompt = (
            f"A clear, highly detailed educational diagram of {topic} for college students."
            f"White or light background, neat and structured layout."
            f"Include accurate English labels for all important parts and processes."
            f"Use arrows to clearly show direction and flow."
            f"All labels must be correctly spelled and scientifically accurate."
            f"Use simple textbook-style vocabulary."
            f"No gibberish text, no distorted or unreadable words."
            f"Diagram should look like a clean NCERT-style or school textbook illustration."
            f"Balanced composition with readable font size."
            f"Add short labels only (not long paragraphs)."
            f"No people, focus only on the concept visualization."
        )

        client = InferenceClient(
            provider="auto",
            api_key=HF_API_KEY,
        )

        print(f"[ImageGen] Generating image for: {topic}")

        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )

        # Add clean labels on top using Pillow
        image = add_labels(image, topic)

        filename = f"hero_{sanitize_filename(topic)}.png"
        filepath = os.path.join(IMAGE_DIR, filename)
        image.save(filepath)

        print(f"[ImageGen] Saved: {filepath}")
        return filepath

    except Exception as e:
        print(f"[ImageGen] Error: {e}")
        return None


def add_labels(image: Image.Image, topic: str) -> Image.Image:
    """
    Adds a clean title bar at the top and a label bar at the bottom
    with key terms related to the topic.
    """
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # ── Try to load a font, fallback to default ──────────────────────────
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        label_font = ImageFont.truetype("arial.ttf", 22)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # ── TOP TITLE BAR ────────────────────────────────────────────────────
    bar_height = 60
    # Draw dark blue top bar
    draw.rectangle([(0, 0), (width, bar_height)], fill=(13, 27, 62))

    # Draw title text
    title_text = f"📘 {topic.upper()}"
    draw.text((20, 15), title_text, font=title_font, fill=(255, 255, 255))

    # Draw "EduAI" badge on right
    badge_text = "EduAI · AI Generated"
    draw.text((width - 200, 20), badge_text, font=small_font, fill=(56, 182, 255))

    # ── BOTTOM LABEL BAR ────────────────────────────────────────────────
    bottom_bar_height = 55
    bottom_y = height - bottom_bar_height

    # Draw dark bottom bar
    draw.rectangle([(0, bottom_y), (width, height)], fill=(13, 27, 62))

    # Get key terms for the topic
    key_terms = get_key_terms(topic)

    # Draw key terms as pills
    x_offset = 20
    pill_padding = 12
    pill_height = 30
    pill_y = bottom_y + (bottom_bar_height - pill_height) // 2

    for term in key_terms:
        # Measure text width
        bbox = draw.textbbox((0, 0), term, font=label_font)
        text_width = bbox[2] - bbox[0]
        pill_width = text_width + pill_padding * 2

        # Stop if we run out of space
        if x_offset + pill_width > width - 20:
            break

        # Draw pill background
        draw.rounded_rectangle(
            [(x_offset, pill_y), (x_offset + pill_width, pill_y + pill_height)],
            radius=8,
            fill=(30, 60, 100)
        )

        # Draw pill border
        draw.rounded_rectangle(
            [(x_offset, pill_y), (x_offset + pill_width, pill_y + pill_height)],
            radius=8,
            outline=(56, 182, 255),
            width=1
        )

        # Draw term text
        draw.text(
            (x_offset + pill_padding, pill_y + 5),
            term,
            font=label_font,
            fill=(200, 230, 255)
        )

        x_offset += pill_width + 10

    # ── SIDE LABEL (left vertical bar) ──────────────────────────────────
    draw.rectangle([(0, bar_height), (5, bottom_y)], fill=(56, 182, 255))

    return image


def get_key_terms(topic: str) -> list:
    """
    Returns key terms to display as labels based on the topic.
    These are generic educational terms — works for any topic.
    """
    topic_lower = topic.lower()

    # Topic-specific terms
    topic_terms = {
        "photosynthesis": ["Light Reaction", "Calvin Cycle", "Chlorophyll", "ATP", "Glucose", "CO2"],
        "machine learning": ["Training", "Model", "Dataset", "Prediction", "Algorithm", "Accuracy"],
        "neural network": ["Input Layer", "Hidden Layer", "Output Layer", "Weights", "Activation", "Backprop"],
        "gradient descent": ["Learning Rate", "Loss Function", "Optimization", "Gradient", "Epoch", "Convergence"],
        "tcp/ip": ["IP Address", "Packet", "Protocol", "Router", "Port", "Handshake"],
        "dna replication": ["Helicase", "Polymerase", "Base Pair", "Nucleotide", "Template", "Strand"],
        "sorting algorithm": ["Bubble Sort", "Merge Sort", "Quick Sort", "Time Complexity", "Array", "Swap"],
        "recursion": ["Base Case", "Call Stack", "Function", "Return", "Depth", "Tree"],
        "ohm's law": ["Voltage", "Current", "Resistance", "Circuit", "Watts", "Ampere"],
        "newton's laws": ["Force", "Mass", "Acceleration", "Inertia", "Momentum", "Gravity"],
    }

    # Check if topic matches any known topic
    for key, terms in topic_terms.items():
        if key in topic_lower:
            return terms

    # Generic fallback terms for any topic
    words = topic.split()
    generic = ["Definition", "Key Concept", "Application", "Example", "Process", "Overview"]
    # Add topic words as labels too
    topic_labels = [w.capitalize() for w in words if len(w) > 3]
    return (topic_labels + generic)[:6]