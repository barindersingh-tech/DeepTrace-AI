const form = document.getElementById("analyze-form");
const input = document.getElementById("image-input");
const dropzone = document.getElementById("dropzone");
const previewWrap = document.getElementById("preview-wrap");
const previewImage = document.getElementById("preview-image");
const fileName = document.getElementById("file-name");
const analyzeButton = document.getElementById("analyze-button");
const buttonText = document.getElementById("button-text");
const emptyState = document.getElementById("empty-state");
const loadingState = document.getElementById("loading-state");
const resultContent = document.getElementById("result-state-content");
const errorState = document.getElementById("error-state");
const resultState = document.getElementById("result-state");
let selectedFile = null;
let objectUrl = null;

function setView(view) {
  emptyState.hidden = view !== "empty";
  loadingState.hidden = view !== "loading";
  resultContent.hidden = view !== "result";
  errorState.hidden = view !== "error";
  resultState.textContent = ({empty:"AWAITING INPUT", loading:"RUNNING INFERENCE", result:"ANALYSIS COMPLETE", error:"ANALYSIS FAILED"})[view];
}

function chooseFile(file) {
  if (!file) return;
  const allowed = ["image/png", "image/jpeg", "image/webp", "image/bmp"];
  if (!allowed.includes(file.type) && !/\.(png|jpe?g|webp|bmp)$/i.test(file.name)) {
    showError("Unsupported file type. Choose a PNG, JPG, JPEG, WEBP, or BMP image.");
    return;
  }
  if (file.size > 12 * 1024 * 1024) {
    showError("This image is larger than 12 MB. Choose a smaller file.");
    return;
  }
  selectedFile = file;
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = URL.createObjectURL(file);
  previewImage.src = objectUrl;
  fileName.textContent = file.name;
  dropzone.hidden = true;
  previewWrap.hidden = false;
  analyzeButton.disabled = false;
  buttonText.textContent = "Analyze image";
  setView("empty");
}

function showError(message) {
  document.getElementById("error-message").textContent = message;
  setView("error");
}

dropzone.addEventListener("click", () => input.click());
dropzone.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }});
input.addEventListener("change", () => chooseFile(input.files[0]));
document.getElementById("change-image").addEventListener("click", () => input.click());
dropzone.addEventListener("dragover", e => { e.preventDefault(); dropzone.classList.add("dragover"); });
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
dropzone.addEventListener("drop", e => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  chooseFile(e.dataTransfer.files[0]);
});

form.addEventListener("submit", async e => {
  e.preventDefault();
  if (!selectedFile) return;
  setView("loading");
  analyzeButton.disabled = true;
  buttonText.textContent = "Analyzing…";
  document.getElementById("loading-message").textContent = "Running the image classifier. First use may download model weights.";
  const data = new FormData();
  data.append("image", selectedFile);
  try {
    const response = await fetch("/api/analyze", {method:"POST", body:data});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "The server could not analyze this image.");
    showResult(payload);
  } catch (err) {
    showError(err.message || "Could not connect to the server. Make sure Flask is running.");
  } finally {
    analyzeButton.disabled = false;
    buttonText.textContent = "Analyze image";
  }
});

function showResult(data) {
  document.getElementById("result-title").textContent = data.result;
  document.getElementById("result-explanation").textContent = data.explanation;
  document.getElementById("confidence-value").textContent = `${data.confidence.toFixed(2)}%`;
  document.getElementById("confidence-bar").style.width = `${Math.min(100, Math.max(0, data.confidence))}%`;
  document.getElementById("top-label").textContent = data.top_label;
  document.getElementById("analyzed-name").textContent = data.filename;
  const badge = document.getElementById("result-badge");
  badge.className = "result-badge";
  if (/real photograph/i.test(data.result)) badge.classList.add("real");
  if (/model prediction/i.test(data.result)) badge.classList.add("unknown");
  const classList = document.getElementById("class-list");
  classList.innerHTML = "";
  (data.all_predictions || []).forEach(item => {
    const row = document.createElement("div");
    row.className = "class-row";
    const name = document.createElement("span"); name.className = "class-name"; name.textContent = item.label;
    const track = document.createElement("div"); track.className = "class-track";
    const bar = document.createElement("span"); bar.style.width = `${Math.min(100, item.confidence)}%`; track.appendChild(bar);
    const score = document.createElement("span"); score.className = "class-score"; score.textContent = `${item.confidence.toFixed(1)}%`;
    row.append(name, track, score); classList.appendChild(row);
  });
  setView("result");
}

function reset() {
  selectedFile = null;
  input.value = "";
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = null;
  previewImage.removeAttribute("src");
  previewWrap.hidden = true;
  dropzone.hidden = false;
  analyzeButton.disabled = true;
  buttonText.textContent = "Analyze image";
  setView("empty");
}
document.getElementById("reset-button").addEventListener("click", reset);
document.getElementById("retry-button").addEventListener("click", () => selectedFile ? form.requestSubmit() : setView("empty"));
