import os
import pytesseract
import streamlit as st
from PIL import Image
from collections import defaultdict
from streamlit_cropper import st_cropper
import re
import pandas as pd

# Set TESSDATA_PREFIX to the local directory
os.environ['TESSDATA_PREFIX'] = './tessdata'

# Ensure tessdata directory exists
os.makedirs('./tessdata', exist_ok=True)

# Telugu characters and special markers
telugu_vowels = 'అఆఇఈఉఊఋఎఏఐఒఓఔ'
telugu_matras = 'ాిీుూృెేైొోౌంః'
telugu_conjunct_marker = '్'  # This indicates a conjunct consonant (ఒత్తులు)

# Predefined ordered categories
category_order = [
    "2 అక్షరాలు, 0 మాత్ర", "2 అక్షరాలు, 1 మాత్ర", "2 అక్షరాలు, 2 మాత్ర",
    "3 అక్షరాలు, 0 మాత్ర", "3 అక్షరాలు, 1 మాత్ర", "3 అక్షరాలు, 2 మాత్ర", "3 అక్షరాలు, 3 మాత్ర",
    "4 అక్షరాలు, 0 మాత్ర", "4 అక్షరాలు, 1 మాత్ర", "4 అక్షరాలు, 2 మాత్ర", "4 అక్షరాలు, 3 మాత్ర", "4 అక్షరాలు, 4 మాత్ర",
    "5 అక్షరాలు, 0 మాత్ర", "5 అక్షరాలు, 1 మాత్ర", "5 అక్షరాలు, 2 మాత్ర", "5 అక్షరాలు, 3 మాత్ర", "5 అక్షరాలు, 4 మాత్ర", "5 అక్షరాలు, 5 మాత్ర",
    "6 అక్షరాలు, 1 మాత్ర", "6 అక్షరాలు, 2 మాత్ర", "6 అక్షరాలు, 3 మాత్ర", "6 అక్షరాలు, 4 మాత్ర", "6 అక్షరాలు, 5 మాత్ర", "6 అక్షరాలు, 6 మాత్ర",
    "1/2/3/4/5/6 అక్షరాలు, ం, ః మాత్ర"
]

# Categorization function
def categorize_words_by_features(text):
    """
    Categorizes Telugu words based on the specified feature matrix,
    properly handling vowels, conjunct consonants, and matras.
    """
    categories = defaultdict(list)

    def count_aksharas_and_matras(word):
        """
        Counts aksharas and matras in a word, treating vowels as standalone aksharas,
        conjuncts as one akshara, and counting matras separately.
        """
        aksharas = []
        matra_count = 0
        temp_akshara = ""
        skip_next = False

        for i, char in enumerate(word):
            if skip_next:
                skip_next = False
                continue

            if char in telugu_vowels:  # Standalone vowels are aksharas
                if temp_akshara:
                    aksharas.append(temp_akshara)
                aksharas.append(char)
                temp_akshara = ""
            elif char == telugu_conjunct_marker and i + 1 < len(word) and re.match(r'[\u0C15-\u0C39]', word[i + 1]):
                # Handle conjunct consonants
                temp_akshara += char + word[i + 1]
                skip_next = True
            elif re.match(r'[\u0C15-\u0C39]', char):  # Telugu consonants
                if temp_akshara:
                    aksharas.append(temp_akshara)
                temp_akshara = char
            elif char in telugu_matras:  # Telugu matras
                temp_akshara += char
                matra_count += 1
            else:
                if temp_akshara:
                    aksharas.append(temp_akshara)
                    temp_akshara = ""
        if temp_akshara:
            aksharas.append(temp_akshara)

        return len(aksharas), matra_count

    words = text.split()

    for word in words:
        unique_count, matra_count = count_aksharas_and_matras(word)

        # Categorize based on predefined order
        category_key = f"{unique_count} అక్షరాలు, {matra_count} మాత్ర"
        categories[category_key].append(word)

        # Special category for certain characters
        if re.search(r'[ంః]', word):
            categories["1/2/3/4/5/6 అక్షరాలు, ం, ః మాత్ర"].append(word)

    # Create the ordered table
    categories_row = category_order
    words_row = [', '.join(set(categories[category])) if category in categories else "" for category in category_order]

    return pd.DataFrame([categories_row, words_row])

# Extract text from image
def extract_text_from_image(image):
    """Extract text from an image using pytesseract."""
    text = pytesseract.image_to_string(image, lang='tel')
    return text

# Streamlit app
st.title("Telugu Word Categorization with Matra and Akshara Features")

uploaded_image = st.file_uploader("Upload an image with Telugu text", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    cropped_image = st_cropper(image, realtime_update=True, box_color='blue', aspect_ratio=None)

    st.image(cropped_image, caption='Cropped Image', use_column_width=True)

    with st.spinner("Extracting text from cropped image..."):
        extracted_text = extract_text_from_image(cropped_image)

    user_text = st.text_area("Edit Extracted Text:", extracted_text)

    categorized_table = categorize_words_by_features(user_text)

    st.write("### Categorized Words Table")
    st.dataframe(categorized_table, use_container_width=True)

else:
    st.info("Please upload an image to analyze.")
