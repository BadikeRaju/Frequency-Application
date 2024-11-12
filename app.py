import os
import pytesseract
import streamlit as st
from PIL import Image
from collections import Counter, defaultdict
from streamlit_cropper import st_cropper
import re

# Set TESSDATA_PREFIX to the local directory
os.environ['TESSDATA_PREFIX'] = './tessdata'

# Ensure tessdata directory exists
os.makedirs('./tessdata', exist_ok=True)

# Define Telugu characters and matras in the required display order
ordered_telugu_chars = [
    'అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ౠ', 'ఌ', 'ౡ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ', 'అం', 'అః'
]
ordered_telugu_consonants = [
    'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ',
    'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ల', 'వ', 'శ', 'ష', 'స', 'హ',
    'ళ', 'క్ష', 'ఱ'
]
ordered_telugu_matras = [
    '✓(అ)', 'ా', 'ి', 'ీ', 'ు', 'ూ', 'ృ', 'ె', 'ే', 'ై', 'ొ', 'ో', 'ౌ', 'ం', 'ః'
]  # Note: '్' is intentionally excluded

# Define matras and consonants eligible for implicit "అ"
matras = ['\u0C3E', '\u0C3F', '\u0C40', '\u0C41', '\u0C42', '\u0C43', '\u0C44', 
          '\u0C46', '\u0C47', '\u0C48', '\u0C4A', '\u0C4B', '\u0C4C', '\u0C02', '\u0C03']  # Include 'ం' and 'ః' but exclude '్'
eligible_consonants_for_implicit_a = set(ordered_telugu_consonants)

def analyze_text(text):
    """Breaks down text into letters, matras, and counts `✓(అ)` for consonants without matras."""
    results = []
    word_counts = Counter(text.split())  # Count occurrences of each word

    for word, frequency in word_counts.items():
        letter_count = defaultdict(int)
        matra_count = defaultdict(int)
        letters_without_matras = []

        for i, char in enumerate(word):
            if re.match(r'[\u0C05-\u0C39\u0C58-\u0C5F]', char):  # Telugu letters range
                letter_count[char] += 1
                letters_without_matras.append(char)  # Assume no matra at first
            elif char in matras:
                matra_count[char] += 1
                if letters_without_matras:
                    letters_without_matras.pop()  # Remove if matra follows

        # Add `✓(అ)` count if there are letters without matras
        if letters_without_matras:
            matra_count["✓(అ)"] = len(letters_without_matras)

        # Multiply counts by word frequency
        for char in letter_count:
            letter_count[char] *= frequency
        for char in matra_count:
            matra_count[char] *= frequency

        results.append({
            "word": word,
            "frequency": frequency,
            "letter_counts": letter_count,
            "matra_counts": matra_count
        })

    # Sort results by word frequency in descending order
    results = sorted(results, key=lambda x: x["frequency"], reverse=True)
    return results

def get_total_character_frequency(word_breakdown):
    """Calculate total frequency of each character and matra based on the word breakdown."""
    total_letter_counts = Counter()
    total_matra_counts = Counter()

    for entry in word_breakdown:
        total_letter_counts.update(entry['letter_counts'])
        total_matra_counts.update(entry['matra_counts'])

    # Format the frequency for display in the specified order
    formatted_frequency = "Character\tCount\n"
    
    # Add ordered Telugu characters
    for char in ordered_telugu_chars:
        count = total_letter_counts.get(char, 0)
        formatted_frequency += f"{char}\t{count}\n"
    
    # Add ordered consonants and implicit `✓(అ)` if applicable
    formatted_frequency += "\n"
    for char in ordered_telugu_consonants:
        count = total_letter_counts.get(char, 0)
        formatted_frequency += f"{char}\t{count}\n"
    
    # Add matras in the requested order
    formatted_frequency += "\n"
    for matra in ordered_telugu_matras:
        count = total_matra_counts.get(matra, 0)
        formatted_frequency += f"{matra}\t{count}\n"
    
    return formatted_frequency

def extract_text_from_image(image):
    """Extract text from image using pytesseract."""
    text = pytesseract.image_to_string(image, lang='tel')
    return text

st.title("Telugu Character and Matra Frequency with Copy Option")

uploaded_image = st.file_uploader("Upload an image with Telugu text", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.write("### Original Image")
    st.image(image, caption='Uploaded Image', use_column_width=True)

    st.write("### Crop the Image")
    cropped_image = st_cropper(image, realtime_update=True, box_color='blue', aspect_ratio=None)

    st.write("### Cropped Image")
    st.image(cropped_image, caption='Cropped Image', use_column_width=True)

    with st.spinner("Extracting text from cropped image..."):
        extracted_text = extract_text_from_image(cropped_image)

    st.write("### Edit Extracted Text")
    user_text = st.text_area("You can edit the extracted text here to remove any unwanted content:", extracted_text)

    # Get breakdown of words with letters and matras using the `analyze_text` function
    word_breakdown = analyze_text(user_text)
    character_frequency = get_total_character_frequency(word_breakdown)

    # Combine all word breakdowns into a single text block, sorted by word frequency
    combined_output = "Word\tFrequency\tLetters\tMatras\n"
    for entry in word_breakdown:
        formatted_letters = ', '.join([f"{key}-{val}" for key, val in entry["letter_counts"].items()])
        formatted_matras = ', '.join([f"{key}-{val}" for key, val in entry["matra_counts"].items() if key != "✓(అ)" or val > 0])
        combined_output += f"{entry['word']}\t{entry['frequency']}\t{formatted_letters}\t{formatted_matras}\n"

    # Display the combined output with a copy option
    st.write("### Telugu Words with Character and Matra Breakdown (Copy All)")
    st.text_area("Copy the entire breakdown to paste into Google Sheets", combined_output, height=300)

    # Display character and matra frequency in the specified order
    st.write("### Telugu Character and Matra Frequency (Copy All)")
    st.text_area("Copy the character and matra frequency", character_frequency, height=300)

else:
    st.info("Please upload an image to analyze.")
