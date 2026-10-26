import os
import uuid
from pathlib import Path
from threading import Lock

from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MODEL_ID = os.environ.get("DEEPTRACE_MODEL", "umm-maybe/AI-image-detector")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_BYTES
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

_classifier = None
_model_error = None
_model_lock = Lock()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_classifier():
    """Load the Hugging Face image-classification model on first prediction."""
    global _classifier, _model_error
    with _model_lock:
        if _classifier is not None:
            return _classifier
        if _model_error is not None:
            raise RuntimeError(_model_error)
        try:
            from transformers import pipeline
            # Model weights are downloaded from Hugging Face the first time this runs.
            _classifier = pipeline(
                "image-classification",
                model=MODEL_ID,
                device=-1,  # CPU: works without a dedicated GPU
            )
            return _classifier
        except Exception as exc:
            _model_error = (
                f"Could not load model '{MODEL_ID}'. Check your internet connection "
                f"on the first run and try again. Technical detail: {exc}"
            )
            raise RuntimeError(_model_error)


def interpret_predictions(predictions):
    """Map the model's output labels to a readable, cautious result."""
    cleaned = []
    for item in predictions:
        label = str(item.get("label", "unknown"))
        score = float(item.get("score", 0.0))
        cleaned.append({"label": label, "score": score})

    if not cleaned:
        raise ValueError("The model returned no predictions.")

    top = cleaned[0]
    label_lower = top["label"].lower().replace("_", " ").replace("-", " ")
    # The chosen model commonly uses labels containing 'artificial'/'real' or 'fake'/'real'.
    if any(word in label_lower for word in ("artificial", "ai generated", "ai-generated", "fake", "synthetic")):
        result = "Likely AI-generated"
        explanation = "The model's highest-scoring class indicates AI-generated or synthetic imagery."
    elif any(word in label_lower for word in ("real", "human", "authentic", "natural")):
        result = "Likely real photograph"
        explanation = "The model's highest-scoring class indicates a real or natural image."
    else:
        result = "Model prediction"
        explanation = f"The model's highest-scoring label is '{top['label']}'. Check the label details below."

    return {
        "result": result,
        "explanation": explanation,
        "confidence": round(top["score"] * 100, 2),
        "top_label": top["label"],
        "all_predictions": [
            {"label": p["label"], "confidence": round(p["score"] * 100, 2)}
            for p in cleaned[:5]
        ],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "model": MODEL_ID,
        "model_loaded": _classifier is not None,
        "model_error": _model_error,
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "Choose an image before analyzing it."}), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify({"error": "Choose an image before analyzing it."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PNG, JPG, JPEG, WEBP, or BMP."}), 400

    safe_name = secure_filename(file.filename)
    suffix = Path(safe_name).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / stored_name

    try:
        file.save(destination)
        with Image.open(destination) as image:
            image.verify()
        with Image.open(destination) as image:
            image = image.convert("RGB")
            classifier = get_classifier()
            predictions = classifier(image, top_k=5)
            result = interpret_predictions(predictions)
        result["filename"] = safe_name
        result["image_url"] = f"/uploads/{stored_name}"
        return jsonify(result)
    except UnidentifiedImageError:
        destination.unlink(missing_ok=True)
        return jsonify({"error": "This file does not appear to be a valid image."}), 400
    except RuntimeError as exc:
        destination.unlink(missing_ok=True)
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        destination.unlink(missing_ok=True)
        app.logger.exception("Image analysis failed")
        return jsonify({"error": f"Analysis failed: {exc}"}), 500


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "Image is too large. Maximum upload size is 12 MB."}), 413


if __name__ == "__main__":
    print("=" * 58)
    print("DeepTrace AI — AI-generated image detector")
    print(f"Model: {MODEL_ID}")
    print("Open http://127.0.0.1:5000 in your browser.")
    print("The model downloads on the first analysis; internet is required then.")
    print("=" * 58)
    app.run(host="127.0.0.1", port=5000, debug=True)
