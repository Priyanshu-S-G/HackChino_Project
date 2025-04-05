document.addEventListener("DOMContentLoaded", () => {
  const newPatientBtn = document.getElementById("new-patient-btn");
  const existingPatientBtn = document.getElementById("existing-patient-btn");

  if (newPatientBtn) {
    newPatientBtn.addEventListener("click", () => {
      window.location.href = "/upload.html"; // Adjust route if using Flask routing
    });
  }

  if (existingPatientBtn) {
    existingPatientBtn.addEventListener("click", () => {
      window.location.href = "templates/history.html";
    });
  }

  // Future proofing: Add theme toggle / animations here if needed
});
