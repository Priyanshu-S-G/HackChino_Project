from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
import os
import time
from werkzeug.utils import secure_filename
from database_handler import save_scan_record
from PIL import Image

app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure necessary folders exist
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
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

    segmented_image_path = os.path.join(STATIC_FOLDER, f"segmented_{os.path.basename(first_image_path)}")
    Image.fromarray(mask[0, :, :, 0] * 255).convert("L").save(segmented_image_path)

    scan_info = {
        "patient_name": request.form.get("patient_name", "Unknown"),
        "patient_age": request.form.get("patient_age", ""),
        "patient_gender": request.form.get("patient_gender", ""),
        "doctor_name": request.form.get("doctor_name", ""),
        "phone": request.form.get("phone", ""),
        "email": request.form.get("email", ""),
        "file_path": saved_filepaths,
        "segmented_image_path": segmented_image_path
    }

    patient_info = save_scan_record(
        scan_info["patient_name"],
        scan_info["patient_age"],
        scan_info["patient_gender"],
        scan_info["phone"],
        scan_info["email"],
        scan_info["doctor_name"],
        scan_info["file_path"],
        scan_info["segmented_image_path"]
    )

    return render_template("result.html",
                           patient_id=patient_info["patient_id"],
                           patient_name=scan_info["patient_name"],
                           patient_age=scan_info["patient_age"],
                           patient_gender=scan_info["patient_gender"],
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

