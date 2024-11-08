import os
import pytesseract
import streamlit as st
from PIL import Image
from collections import Counter
from streamlit_cropper import st_cropper
import re

# Set TESSDATA_PREFIX to the local directory
os.environ['TESSDATA_PREFIX'] = './tessdata'

# Ensure tessdata directory exists (this won't download anything, just sets up the folder)
os.makedirs('./tessdata', exist_ok=True)

# Define the ordered list of Telugu characters and matras for display
ordered_telugu_chars = [
    'అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ',
    'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ',
    'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ల', 'వ', 'శ', 'ష', 'స', 'హ',
    'ళ', 'క్ష', 'ఱ'  # Additional characters
]
ordered_telugu_matras = [
    'ా', 'ి', 'ీ', 'ు', 'ూ', 'ృ', 'ె', 'ే', 'ై', 'ొ', 'ో', 'ౌ', 'ం', 'ః', '్',
    'ౠ', 'ఌ', 'ౡ'  # Additional matras
]

def extract_text_from_image(image):
    """Extract text from image using pytesseract."""
    text = pytesseract.image_to_string(image, lang='tel')
    return text

def count_telugu_characters(text):
    """Count only Telugu characters and separate matras in the text."""
    telugu_chars = [char for char in text if char in ordered_telugu_chars]
    telugu_matras = [char for char in text if char in ordered_telugu_matras]
    char_counts = Counter(telugu_chars)
    matra_counts = Counter(telugu_matras)
    return (
        {char: char_counts.get(char, 0) for char in ordered_telugu_chars},
        {matra: matra_counts.get(matra, 0) for matra in ordered_telugu_matras}
    )

def count_telugu_words(text):
    """Count occurrences of each Telugu word in the text."""
    words = re.findall(r'[\u0C00-\u0C7F]+', text)
    word_counts = Counter(words).most_common()
    return word_counts

st.title("Ordered Telugu Character Count from Image with Cropping and Editing")

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

    character_counts, matra_counts = count_telugu_characters(user_text)

    characters_str = '\n'.join([char for char in character_counts.keys()])
    char_counts_str = '\n'.join([str(count) for count in character_counts.values()])
    matras_str = '\n'.join([matra for matra in matra_counts.keys()])
    matra_counts_str = '\n'.join([str(count) for count in matra_counts.values()])

    st.write("### Telugu Character and Matra Frequency in Specified Order")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("**Characters**")
        st.text_area("Characters Column", characters_str, height=400)

    with col2:
        st.write("**Character Counts**")
        st.text_area("Character Counts Column", char_counts_str, height=400)

    with col3:
        st.write("**Matras**")
        st.text_area("Matras Column", matras_str, height=400)

    with col4:
        st.write("**Matra Counts**")
        st.text_area("Matra Counts Column", matra_counts_str, height=400)

    st.write("### Telugu Word Frequency")
    word_counts = count_telugu_words(user_text)

    word_col, freq_col = st.columns(2)
    with word_col:
        words_str = '\n'.join([word for word, _ in word_counts])
        st.text_area("Words Column", words_str, height=400)

    with freq_col:
        freq_str = '\n'.join([str(count) for _, count in word_counts])
        st.text_area("Frequency Column", freq_str, height=400)

else:
    st.info("Please upload an image to analyze.")
