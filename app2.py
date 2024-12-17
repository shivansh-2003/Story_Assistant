import openai
import streamlit as st
from fpdf import FPDF
import base64
from gtts import gTTS
import os
from PIL import Image
import io

# Function to set the OpenAI API key
def set_openai_key():
    st.sidebar.write("🔑 **Enter your OpenAI API Key**")
    api_key = st.sidebar.text_input("API Key", type="password")
    if api_key:
        openai.api_key = api_key
        st.session_state.api_key = api_key
        st.sidebar.success("API Key set successfully!")

# Function to add multiple characters
def add_multiple_characters():
    st.sidebar.header("👤 Add Characters (Max 10)")
    
    if "characters" not in st.session_state:
        st.session_state.characters = []

    # Allow user to add a new character until there are 10 characters
    if len(st.session_state.characters) < 10:
        name = st.text_input(f"Character {len(st.session_state.characters) + 1} Name", key=f"name{len(st.session_state.characters)}")
        personality = st.selectbox(f"Character {len(st.session_state.characters) + 1} Personality", 
                                   ["Brave", "Clever", "Shy", "Aggressive", "Wise"], key=f"personality{len(st.session_state.characters)}")
        appearance = st.text_input(f"Character {len(st.session_state.characters) + 1} Appearance", 
                                   value="A tall man with brown hair and green eyes.", key=f"appearance{len(st.session_state.characters)}")

        if st.button(f"Add Character {len(st.session_state.characters) + 1}"):
            if name:
                character = {"name": name, "personality": personality, "appearance": appearance}
                st.session_state.characters.append(character)
                st.success(f"Character {name} added!")
            else:
                st.warning("Please enter a character name.")

    else:
        st.info("You have reached the maximum of 10 characters.")

# Define the prompt template for story generation
prompt_template = """
You are the narrator of an interactive story. The story starts with:

{start}

The user makes a choice: {choice}

Based on this choice, continue the story in a creative way:
"""

# Function to generate the story
def generate_story_with_characters(characters, theme, prompt, choice):
    # Adding the characters to the prompt
    characters_description = ""
    for character in characters:
        characters_description += f"Your character is {character['name']}, who is {character['personality']} and has {character['appearance']}.\n"
    
    formatted_prompt = f"Theme: {theme}. {characters_description} {prompt_template.format(start=prompt, choice=choice)}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": formatted_prompt}
        ],
        max_tokens=900,
        temperature=0.7,
    )

    story = response['choices'][0]['message']['content'].strip()
    return story

# Function to summarize the prompt to reduce token count
def summarize_text(text):
    summarization_prompt = f"Please summarize the following text to stay under 800 tokens while maintaining its main idea:\n\n{text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": summarization_prompt}
        ],
        max_tokens=300,
        temperature=0.7,
    )
    
    summarized_text = response['choices'][0]['message']['content'].strip()
    return summarized_text

# Function to generate an image using OpenAI's DALL·E
def generate_image_from_story(story_text):
    # Summarize the story before passing it to DALL·E
    summarized_story = summarize_text(story_text)
    
    # Use DALL·E to generate an image based on the summarized story
    response = openai.Image.create(
        prompt=summarized_story,
        n=1,
        size="1024x1024"
    )
    
    image_url = response['data'][0]['url']
    return image_url

# Function to convert story to PDF
def convert_to_pdf(story_parts):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for part in story_parts:
        pdf.multi_cell(0, 10, part)

    return pdf

# Function to convert story to audio
def convert_to_audio(story, language='en'):
    tts = gTTS(text=story, lang=language, slow=False)
    audio_file = "story_audio.mp3"
    tts.save(audio_file)
    return audio_file

# Main function
def main():
    st.title("🌟 Interactive Storytelling App")

    # Set OpenAI API key from user input
    set_openai_key()

    if not st.session_state.get("api_key"):
        st.warning("Please enter your OpenAI API key in the sidebar to start.")
        return

    # Add multiple characters
    add_multiple_characters()

    # Theme selection
    st.sidebar.header("📝 Choose Your Story Theme")
    theme_options = ["Fantasy", "Mystery", "Adventure", "Sci-Fi", "Horror", "Romance"]
    selected_theme = st.selectbox("Select Story Theme", theme_options)

    if "story" not in st.session_state:
        st.session_state.story = []
        st.session_state.started = False
        st.session_state.stopped = False

    with st.sidebar:
        st.header("Story Settings")
        base_story = st.text_area("📝 Base Story Idea", height=150, help="Enter the idea that will kickstart your story.")
        if st.button("🎬 Start Story"):
            if base_story.strip():
                st.session_state.story = [base_story]
                st.session_state.started = True
                st.session_state.stopped = False
                st.success("Story started successfully!")
            else:
                st.error("Please enter a base story idea to start.")
    
    if st.session_state.get("started", False):
        st.subheader("📖 Your Story So Far")
        st.markdown(" ".join(st.session_state.story))
        
        if not st.session_state.stopped:
            user_choice = st.text_input("🤔 What happens next?", placeholder="Enter a decision or action...")
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if st.button("Continue Story"):
                    if user_choice:
                        new_story = generate_story_with_characters(st.session_state.characters, selected_theme, " ".join(st.session_state.story), user_choice)
                        st.session_state.story.append(new_story)
                        st.success("Story continued!")
                        
                        # Generate image based on the current story
                        # Generate image based on the current story
                        image_url = generate_image_from_story(new_story)
                        st.image(image_url, caption="Story Visual", use_container_width=True)  # Use 'use_container_width' instead of 'use_column_width'
                    else:
                        st.warning("Please enter a choice to continue the story.")
            
            with col2:
                if st.button("Continue Automatically"):
                    last_part = st.session_state.story[-1] if st.session_state.story else ""
                    new_story = generate_story_with_characters(st.session_state.characters, selected_theme, " ".join(st.session_state.story), last_part)
                    st.session_state.story.append(new_story)
                    st.success("Story continued automatically!")
                    
                    # Generate image based on the current story
                    image_url = generate_image_from_story(new_story)
                    st.image(image_url, caption="Story Visual", use_column_width=True)
            
            with col3:
                if st.button("⛔ Stop Story"):
                    st.session_state.stopped = True
                    st.info("Story stopped. You can now convert it to PDF or Audio.")

        if st.session_state.stopped:
            st.subheader("📤 Export Your Story")
            
            if st.button("🖨️ Convert to PDF"):
                pdf = convert_to_pdf(st.session_state.story)
                pdf_output = pdf.output(dest='S').encode('latin1')
                b64_pdf = base64.b64encode(pdf_output).decode('latin1')
                href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="story.pdf">Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            language_option = st.selectbox("🌍 Choose a language for the audio:", ["English", "Spanish", "French", "Chinese"])
            lang_dict = {"English": "en", "Spanish": "es", "French": "fr", "Chinese": "zh"}

            if st.button("🎧 Convert to Audio"):
                selected_lang = lang_dict[language_option]
                audio_file = convert_to_audio(" ".join(st.session_state.story), language=selected_lang)
                with open(audio_file, "rb") as audio:
                    b64_audio = base64.b64encode(audio.read()).decode('latin1')
                href = f'<a href="data:audio/mp3;base64,{b64_audio}" download="story_audio.mp3">Download Audio</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()