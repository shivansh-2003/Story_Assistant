# 🌟 Interactive Storytelling App
This is an interactive storytelling app built with Streamlit that allows users to create dynamic stories based on their input. The app uses OpenAI Api key to generate the story, and users can export their final story to PDF or audio formats.

## 🎬 Features
1. Interactive Story Creation: Start with a base story idea, and continue the story based on your choices.
2. OpenAI Integration: Generate creative and dynamic story continuations using GPT-3.5.
3. Export Options:
PDF Export: Convert your entire story into a PDF document.
Audio Export: Convert your story into an audio file (MP3) in multiple languages.
User-Friendly Interface: A clean and intuitive interface designed with Streamlit.

## 🚀 Getting Started
Prerequisites
Python 3.7+
Streamlit
OpenAI Python Client
FPDF
gTTS
PIP

## Installation
1. Clone the repository:
```
git clone https://github.com/yourusername/interactive-storytelling-app.git
cd interactive-storytelling-app
```
2. Install the required packages:
```
pip install -r requirements.txt
```

3. Set up your OpenAI API key:

Obtain an API key from OpenAI.
You can securely input your API key in the app's sidebar

## Running app
Start the Streamlit app:
```
streamlit run app.py
```

🎨 Usage
1. Enter OpenAI API Key: Enter your OpenAI API key in the sidebar. This key is required to generate story content.
2. Start Story: Provide an initial story idea and click "Start Story."
3. Continue the Story:
Type in a decision or action to guide the story.
Alternatively, let the app continue the story automatically based on previous events.
4. Stop the Story: When you're satisfied with the story, click "Stop Story."
5. Export Options:
Convert the story into a PDF file by clicking "Convert to PDF."
Convert the story into an audio file by selecting a language and clicking "Convert to Audio."


🌍 Supported Languages for Audio
1. English
2. Spanish
3. French
4. Chinese