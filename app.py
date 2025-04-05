from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
import os
import time
from werkzeug.utils import secure_filename
from database_handler import save_new_patient_scan, save_existing_patient_scan
from PIL import Image

app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure necessary folders exist
UPLOAD_FOLDER = "uploads"
MASK_FOLDER = "masks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MASK_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@tf.keras.utils.register_keras_serializable()
def dice_metric(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    intersection = tf.reduce_sum(y_true * y_pred)
    return (2. * intersection + 1) / (tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + 1)

@tf.keras.utils.register_keras_serializable()
def iou_metric(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    intersection = tf.reduce_sum(y_true * y_pred)
    union = tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) - intersection
    return (intersection + 1) / (union + 1)

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

MODEL_PATHS = {
    "unet": "models/unet_model.keras",
    "segnet": "models/segnet_model.keras",
    "minisegnet": "models/minisegnet_model.keras"
}

models = {
    name: tf.keras.models.load_model(path, custom_objects={"dice_metric": dice_metric, "iou_metric": iou_metric})
    for name, path in MODEL_PATHS.items()
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload.html')
def upload_page():
    return render_template('upload.html')

@app.route('/result.html')
def result_page():
    return render_template('result.html')

@app.route('/history.html')
def history_page():
    return render_template('history.html')

@app.route('/history_results.html')
def history_results_page():
    return render_template('history_results.html')

@app.route('/api/upload', methods=['POST'])
def upload_mri():
    files = request.files.getlist("mri_images")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    saved_filepaths = []
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_filepaths.append(filepath)

    # Only process the first image for now
    first_image_path = saved_filepaths[0]
    try:
        image = preprocess_image(first_image_path)
    except Exception as e:
        return jsonify({"error": f"Image preprocessing failed: {str(e)}"}), 500

    if image.shape != (1, 128, 128, 4):
        return jsonify({"error": f"Unexpected image shape: {image.shape}"}), 500

    try:
        predictions = {name: model.predict(image) for name, model in models.items()}
    except Exception as e:
        return jsonify({"error": f"Model prediction failed: {str(e)}"}), 500

    avg_prediction = np.mean(list(predictions.values()), axis=0)
    mask = postprocess_prediction(avg_prediction)

    segmented_image_path = os.path.join(MASK_FOLDER, f"segmented_{os.path.basename(first_image_path)}")
    Image.fromarray(mask[0, :, :, 0] * 255).convert("L").save(segmented_image_path)

    # Determine patient type
    patient_type = request.form.get("patient_type", "new")
    patient_info = None

    if patient_type == "new":
        # Handle new patient
        patient_name = request.form.get("patient_name", "Unknown")
        patient_age = request.form.get("patient_age", "")
        patient_gender = request.form.get("patient_gender", "")
        doctor_name = request.form.get("doctor_name", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")

        patient_info = save_new_patient_scan(
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            phone=phone,
            email=email,
            doctor_name=doctor_name,
            original_file_path=saved_filepaths,
            segmented_image_path=segmented_image_path
        )

    else:
        # Handle returning patient
        patient_id = request.form.get("patient_id", "").strip()
        if not patient_id:
            return jsonify({"error": "Patient ID required for returning patients"}), 400

        # You can add an optional check here:
        # if not check_patient_exists(patient_id):
        #     return jsonify({"error": "Patient ID not found"}), 404

        patient_info = save_existing_patient_scan(
            patient_id=patient_id,
            original_file_path=saved_filepaths,
            segmented_image_path=segmented_image_path
        )

    return render_template("result.html",
                           patient_id=patient_info["patient_id"],
                           patient_name=request.form.get("patient_name", ""),
                           patient_age=request.form.get("patient_age", ""),
                           patient_gender=request.form.get("patient_gender", ""),
                           scan_date=patient_info["scan_date"].split(" ")[0],
                           segmented_image=segmented_image_path.replace("static/", ""))


def preprocess_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    image = tf.keras.preprocessing.image.load_img(image_path, color_mode="grayscale", target_size=(128, 128))
    image = tf.keras.preprocessing.image.img_to_array(image)

    # Corrected: Convert grayscale to 4-channel format
    image = np.concatenate([image] * 4, axis=-1)

    image = np.expand_dims(image, axis=0)
    image = image / 255.0

    if image.shape != (1, 128, 128, 4):
        raise ValueError(f"Preprocessed image has unexpected shape: {image.shape}")

    return image

def postprocess_prediction(prediction):
    return (prediction > 0.5).astype(np.uint8)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("DEBUG", "False").lower() == "true")

