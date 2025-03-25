from flask import Flask, request, jsonify



# Download necessary NLTK resources
nltk.download('punkt')

app = Flask(__name__)

# Load the paraphrasing model (T5)



@app.route('/process', methods=['POST'])
def process_text():
    """
    API endpoint to process text.
    Expects a JSON payload with 'text' and 'function' (either 'paraphrase' or 'spell_check').
    """
    data = request.json
    text = data.get("text", "")
    function = data.get("function", "")

    if not text or not function:
        return jsonify({"error": "Missing text or function"}), 400

    if function == "spell_check":
        processed_text = correct_spelling(text)
    elif function == "paraphrase":
        processed_text = paraphrase_text(text)
    else:
        return jsonify({"error": "Invalid function"}), 400

    return jsonify({"original_text": text, "processed_text": processed_text})

if __name__ == "__main__":
    app.run(debug=True)