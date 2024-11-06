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

# Define the ordered list of Telugu characters for display
ordered_telugu_chars = [
    'అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ',
    'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ',
    'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ల', 'వ', 'శ', 'ష', 'స', 'హ',
    'ా', 'ి', 'ీ', 'ు', 'ూ', 'ృ', 'ె', 'ే', 'ై', 'ొ', 'ో', 'ౌ', 'ం', 'ః', '్'
]

# Function to extract text from image using pytesseract
def extract_text_from_image(image):
    """Extract text from image using pytesseract."""
    text = pytesseract.image_to_string(image, lang='tel')
    return text

# Function to count only Telugu characters and matras in the text
def count_telugu_characters(text):
    """Count only Telugu characters and matras in the text."""
    telugu_text = [char for char in text if '\u0C00' <= char <= '\u0C7F']
    counts = Counter(telugu_text)
    return {char: counts.get(char, 0) for char in ordered_telugu_chars}

# Function to count occurrences of each Telugu word
def count_telugu_words(text):
    """Count occurrences of each Telugu word in the text."""
    # Split text using spaces and Telugu-specific punctuation to get words
    words = re.findall(r'[\u0C00-\u0C7F]+', text)
    word_counts = Counter(words)
    return word_counts

# Streamlit application
st.title("Ordered Telugu Character Count from Image with Cropping and Editing")

# File uploader for image
uploaded_image = st.file_uploader("Upload an image with Telugu text", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Load and display the image
    image = Image.open(uploaded_image)
    st.write("### Original Image")
    st.image(image, caption='Uploaded Image', use_column_width=True)

    # Cropping section
    st.write("### Crop the Image")
    cropped_image = st_cropper(image, realtime_update=True, box_color='blue', aspect_ratio=None)

    # Display cropped image
    st.write("### Cropped Image")
    st.image(cropped_image, caption='Cropped Image', use_column_width=True)

    # Extract text from cropped image
    with st.spinner("Extracting text from cropped image..."):
        extracted_text = extract_text_from_image(cropped_image)
    
    # Editable text area for user to modify extracted text
    st.write("### Edit Extracted Text")
    user_text = st.text_area("You can edit the extracted text here to remove any unwanted content:", extracted_text)
    
    # Count only Telugu characters in specified order
    character_counts = count_telugu_characters(user_text)

    # Convert character and count data to strings for copying
    characters_str = '\n'.join([char for char in character_counts.keys()])
    counts_str = '\n'.join([str(count) for count in character_counts.values()])

    # Display ordered character counts with single copy buttons for each column
    st.write("### Telugu Character Frequency in Specified Order")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Characters**")
        st.text_area("Characters Column", characters_str, height=400)
        st.button("Copy All Characters", on_click=lambda: st.session_state.update({"copy_characters": characters_str}))

    with col2:
        st.write("**Counts**")
        st.text_area("Counts Column", counts_str, height=400)
        st.button("Copy All Counts", on_click=lambda: st.session_state.update({"copy_counts": counts_str}))

    # Count Telugu word occurrences and display word counts in two columns
    st.write("### Telugu Word Frequency")
    word_counts = count_telugu_words(user_text)
    
    # Split into two columns for word frequency
    word_col, freq_col = st.columns(2)
    with word_col:
        st.write("**Words**")
        words_str = '\n'.join(word_counts.keys())
        st.text_area("Words Column", words_str, height=400)
    
    with freq_col:
        st.write("**Frequency**")
        freq_str = '\n'.join([str(count) for count in word_counts.values()])
        st.text_area("Frequency Column", freq_str, height=400)

else:
    st.info("Please upload an image to analyze.")
