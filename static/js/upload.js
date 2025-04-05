document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("#upload-form");
  const statusMessage = document.querySelector("#status-message");
  const submitButton = form.querySelector("button");

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    statusMessage.classList.remove("hidden", "status-red", "status-green");
    statusMessage.textContent = "Uploading...";

    const formData = new FormData();
    const patientType = document.querySelector("#patient_type").value;

    if (patientType === "new") {
      formData.append("patient_type", "new");

      const name = document.querySelector("#patient_name").value.trim();
      const age = document.querySelector("#patient_age").value.trim();
      const gender = document.querySelector("#patient_gender").value;
      const mobile = document.querySelector("#mobile_number").value.trim();
      const email = document.querySelector("#email_id").value.trim();
      const doctor = document.querySelector("#doctor_name").value.trim();

      if (!name) {
        statusMessage.textContent = "Please enter the patient's name.";
        statusMessage.classList.add("status-red");
        return;
      }

      if (isNaN(age) || age <= 0) {
        statusMessage.textContent = "Please enter a valid age.";
        statusMessage.classList.add("status-red");
        return;
      }

      if (email && !/^\S+@\S+\.\S+$/.test(email)) {
        statusMessage.textContent = "Invalid email format.";
        statusMessage.classList.add("status-red");
        return;
      }

      if (mobile && !/^\d{10}$/.test(mobile)) {
        statusMessage.textContent = "Invalid mobile number (should be 10 digits).";
        statusMessage.classList.add("status-red");
        return;
      }

      formData.append("patient_name", name);
      formData.append("patient_age", age);
      formData.append("patient_gender", gender);
      formData.append("mobile_number", mobile);
      formData.append("email_id", email);
      formData.append("doctor_name", doctor);

    } else {
      const uid = document.querySelector("#patient_uid").value.trim();
      if (!uid) {
        statusMessage.textContent = "Please enter the Patient UID.";
        statusMessage.classList.add("status-red");
        return;
      }
      formData.append("patient_type", "existing");
      formData.append("patient_uid", uid);
    }

    const fileInput = document.querySelector("#mri_image");
    const file = fileInput.files[0];

    if (!file) {
      statusMessage.textContent = "Please upload an MRI image.";
      statusMessage.classList.add("status-red");
      return;
    }

    formData.append("mri_image", file);

    submitButton.disabled = true;
    submitButton.textContent = "Uploading...";
    submitButton.classList.add("opacity-50", "cursor-not-allowed");

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed. Server error.");
      }

      const result = await response.json();

      if (!result.scan_id) {
        throw new Error("Upload succeeded but no scan ID received.");
      }

      statusMessage.textContent = "Upload successful! Redirecting...";
      statusMessage.classList.add("status-green");

      setTimeout(() => {
        window.location.href = `/scan-results/${result.scan_id}`;
      }, 1500);

    } catch (error) {
      statusMessage.textContent = error.message || "An error occurred during upload.";
      statusMessage.classList.add("status-red");
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Upload";
      submitButton.classList.remove("opacity-50", "cursor-not-allowed");
    }
  });
});
