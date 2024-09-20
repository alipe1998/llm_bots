import tkinter as tk
from tkinter import scrolledtext

def chunk_text(text, chunk_size=2000):
    # Split the text into chunks of a specific size
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def display_chunks():
    # Clear any previous chunks displayed
    for widget in output_frame.winfo_children():
        widget.destroy()

    # Get input text from the user
    input_text = input_box.get("1.0", tk.END).strip()
    
    # Chunk the text
    chunks = chunk_text(input_text)

    # Display each chunk in its own text box
    for i, chunk in enumerate(chunks):
        chunk_label = tk.Label(output_frame, text=f"Chunk {i + 1}:")
        chunk_label.pack(anchor="w", pady=5)
        
        chunk_box = scrolledtext.ScrolledText(output_frame, width=100, height=10)
        chunk_box.pack(pady=5)
        chunk_box.insert(tk.END, chunk)
        chunk_box.config(state=tk.DISABLED)  # Make the box read-only

    # Update the scroll region of the canvas after adding widgets
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Create the main window
root = tk.Tk()
root.title("Text Chunker")

# Create a frame for the scrollbar
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

# Create a canvas to contain the content
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Add a scrollbar to the canvas
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.config(yscrollcommand=scrollbar.set)

# Create another frame to hold the actual content (inside the canvas)
content_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Create the input and output widgets inside the content frame
input_label = tk.Label(content_frame, text="Enter your text:")
input_label.pack()

input_box = scrolledtext.ScrolledText(content_frame, width=100, height=10)
input_box.pack()

chunk_button = tk.Button(content_frame, text="Chunk Text", command=display_chunks)
chunk_button.pack()

# Create a frame inside content_frame to hold the output chunks
output_frame = tk.Frame(content_frame)
output_frame.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
