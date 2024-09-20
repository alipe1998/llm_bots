from flask import Flask, request, render_template

app = Flask(__name__)

def chunk_text(text, chunk_size=2000):
    # Split the text into chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Add position indicators
    if len(chunks) == 1:
        chunks[0] = f"$$START$$ {chunks[0]} $$END$$"
    else:
        chunks[0] = f"$$START$$ {chunks[0]}"
        for i in range(1, len(chunks) - 1):
            chunks[i] = f"$$CONTINUE$$ {chunks[i]}"
        chunks[-1] = f"$$END$$ {chunks[-1]}"
    
    return chunks

@app.route("/", methods=["GET", "POST"])
def home():
    chunks = []
    if request.method == "POST":
        input_text = request.form.get("input_text")
        if input_text:
            chunks = chunk_text(input_text)
    return render_template("index.html", chunks=chunks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
