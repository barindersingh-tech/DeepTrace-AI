# DeepTrace AI — AI-Generated Image Detector

A full-stack Deep Learning mini-project using Flask, a browser-based upload interface, and a pretrained Hugging Face image-classification model.

## What it does

- Upload a PNG, JPG, JPEG, WEBP, or BMP image.
- Runs a pretrained vision classifier on the Flask backend.
- Displays the top predicted class, model score, and top-five class scores.
- Includes upload validation, loading/error states, and a responsive interface.
- Runs on CPU; a dedicated GPU is not required.

## Important model and research notes

The default model ID is `umm-maybe/AI-image-detector`. The first analysis downloads the model files from Hugging Face, so the first run needs an internet connection and may take several minutes. Later runs normally use the local Hugging Face cache.

The classifier is not a forensic guarantee. It can make mistakes, especially on compressed, edited, unfamiliar, or out-of-distribution images. Report the model's dataset, limitations, and measured performance honestly in your project report. A high confidence score is not proof that a prediction is correct.

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10 or 3.11 recommended
- Internet connection for initial dependency/model download
- At least 8 GB RAM recommended; CPU inference can be slow

## Run on Windows (easy method)

1. Extract the ZIP file.
2. Open the extracted `DeepTrace_AI` folder in VS Code.
3. Double-click `run.bat`, or run it from the VS Code terminal:

   ```bat
   run.bat
   ```

4. Wait for dependency installation. The first installation may take a while because PyTorch is large.
5. When the terminal says the server is running, open:

   `http://127.0.0.1:5000`

6. Upload an image and click **Analyze image**.

Keep the terminal open while using the app. Press `Ctrl+C` in the terminal to stop it.

## Run manually in VS Code

Open a terminal in this folder.

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use `run.bat` or run `.venv\Scripts\python.exe app.py` after installing dependencies.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python app.py
```

Then open `http://127.0.0.1:5000`.

## Project structure

```text
DeepTrace_AI/
├── app.py                 # Flask routes and model inference
├── requirements.txt       # Python dependencies
├── run.bat                # Windows one-click launcher
├── run.sh                 # macOS/Linux launcher
├── README.md              # Setup and project notes
├── templates/
│   └── index.html         # Main web page
├── static/
│   ├── style.css          # Responsive dark interface
│   └── script.js          # Upload and result interactions
└── uploads/               # Temporary image uploads
```

## Troubleshooting

### `python` is not recognized
Install Python 3.10 or 3.11 and select **Add Python to PATH** during installation. Restart VS Code afterward.

### Model download or loading fails
Check your internet connection, then restart the app and retry. The model is downloaded on the first prediction. If your network blocks Hugging Face, try another network or configure an approved local model cache.

### `torch` installation fails
Use Python 3.10 or 3.11 (64-bit). Delete the `.venv` folder and run `run.bat` again. If the issue persists, install a compatible PyTorch build from the official PyTorch installation selector.

### App says port 5000 is in use
Close the other app using port 5000, or change the port in the final `app.run(...)` line of `app.py`.

### The result looks wrong
The model can misclassify images. Use several known examples, record the results, and discuss the limitations in your report. Do not present the output as definitive proof.

## Viva topics to prepare

- What is deep learning?
- What is a Vision Transformer (ViT)?
- What is transfer learning?
- What is image classification?
- What is inference?
- What is a confidence score, and why is it not a guarantee?
- Why are validation and test datasets needed?
- What are false positives and false negatives?
- What limitations can cause a detector to fail on new image generators?

## Academic integrity

This is a runnable project scaffold with a pretrained classifier. For a strong submission, verify the model card and its training/evaluation details, run your own documented test set, report metrics, and clearly distinguish work you performed from pretrained components.
