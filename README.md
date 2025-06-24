# 📘 VocabQuiz for PCE

A simple tool to extract and study vocabulary from PDF files.  
Originally built to prepare for my **PCE (Presenting and Communicating in English)** final exam, but easily reusable for any English learning purpose.

<br>

## ✨ What it does

- Upload a PDF file (like a textbook or class material)
- Automatically extracts English words from the text
- Shows their English definitions
- Clean and simple web interface built with Flask

<br>

## 🛠 Tech Stack

- Python 3
- Flask
- PyMuPDF (for PDF text parsing)
- HTML (Jinja2 templates)
- Local file tracking (no database)

<br>

## 🗂 Project Structure
```
.
├── app.py # Flask app entry point
├── routes.py # Routes and request handling
├── extract_vocab.py # PDF parsing + vocabulary extraction
├── tracker.py # Tracks learned words
├── templates/
│ └── index.html # Web UI template
├── contents/
│ ├── Chapter1.pdf
│ ├── Chapter2.pdf
│ └── Chapter3.pdf
├── static/ # (optional) CSS/JS assets
├── Makefile # Local setup helper
├── requirements.txt # Python dependencies
└── README.md
```

<br>

## 🚀 How to Run

```bash
# 1. Clone the repository
git clone https://github.com/your-username/vocabquiz-for-pce.git
cd vocabquiz-for-pce

# 2. Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Run the app
python app.py

# Then open your browser and go to http://localhost:3400
```

<br>

## 📂 Example Workflow

1. Place your chapter PDF (e.g., `Chapter3.pdf`) into the `contents/` folder  
2. File name should follow this format: `ChapterX.pdf` (e.g., `Chapter1.pdf`, `Chapter2.pdf`, ...)  
3. In the PDF, vocabulary entries should look like:
    ```
    VocabularyWord
    Meaning: Definition of the word
    Example: Example sentence using the word
    ```

4. Start the server with `python app.py`  
5. Open your browser at `http://localhost:3400`  
6. Select a chapter or choose "All Chapters" to begin a quiz  
7. For each word, try to recall or guess the meaning before revealing it  
8. Click the **Hint** button to see the first letter of the correct word  
9. A progress bar is shown **above the answer input box** to track your quiz progress  

💡 You can also use the **word search feature** at the bottom of the page to look up any word and see its meaning instantly.

<br>

## ℹ️ Notes

- Currently supports **Chapter 1 to Chapter 3 only**
- More chapters and features are planned for future updates
