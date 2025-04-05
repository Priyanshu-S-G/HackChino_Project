from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
import os
import time
from werkzeug.utils import secure_filename
from database_handler import save_new_patient_scan, save_existing_patient_scan, check_patient_exists, patients_collection
from PIL import Image

app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure necessary folders exist inside 'static'
UPLOAD_FOLDER = os.path.join("static", "uploads")
MASK_FOLDER = os.path.join("static", "masks")
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
    files = request.files.getlist("mri_images")  # <-- fixed field name
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    saved_filepaths = []
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Normalize to relative POSIX-style path from 'static/'
            rel_path = os.path.relpath(filepath, start="static").replace(os.sep, "/")
            saved_filepaths.append(rel_path)

    # Only process the first image
    first_image_path = os.path.join("static", saved_filepaths[0])
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

    # Save segmented mask to static/masks/
    mask_filename = f"segmented_{os.path.basename(saved_filepaths[0])}"
    segmented_image_rel_path = os.path.join("masks", mask_filename).replace(os.sep, "/")
    segmented_image_abs_path = os.path.join("static", segmented_image_rel_path)
    Image.fromarray(mask[0, :, :, 0] * 255).convert("L").save(segmented_image_abs_path)

    # Determine patient type
    patient_type = request.form.get("patient_type", "new")

    if patient_type == "new":
        patient_name = request.form.get("patient_name", "Unknown")
        patient_age = request.form.get("patient_age", "")
        patient_gender = request.form.get("patient_gender", "")
        doctor_name = request.form.get("doctor_name", "")
        phone = request.form.get("mobile_number", "")
        email = request.form.get("email_id", "")

        scan_info = save_new_patient_scan(
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            phone=phone,
            email=email,
            doctor_name=doctor_name,
            original_file_path=saved_filepaths,
            segmented_image_path=segmented_image_rel_path
        )

        patient_record = {
            "patient_name": patient_name,
            "patient_age": patient_age,
            "patient_gender": patient_gender
        }

    else:
        patient_id = request.form.get("patient_uid", "").strip()  # <-- fixed: patient_uid matches JS
        if not patient_id:
            return jsonify({"error": "Patient ID required for returning patients"}), 400

        if not check_patient_exists(patient_id):
            return jsonify({"error": "Patient ID not found"}), 404

        scan_info = save_existing_patient_scan(
            patient_id=patient_id,
            original_file_path=saved_filepaths,
            segmented_image_path=segmented_image_rel_path
        )

        patient_record = patients_collection.find_one({"patient_id": patient_id})
        if not patient_record:
            return jsonify({"error": "Patient record missing"}), 500

    return jsonify({
        "scan_id": scan_info.get("scan_id", ""),
        "patient_id": scan_info["patient_id"],
        "patient_name": patient_record.get("patient_name", ""),
        "patient_age": patient_record.get("patient_age", ""),
        "patient_gender": patient_record.get("patient_gender", ""),
        "scan_date": scan_info["scan_date"].split(" ")[0],
        "segmented_image": segmented_image_rel_path
    }), 200


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

