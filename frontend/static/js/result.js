document.addEventListener("DOMContentLoaded", function () { 
  const statusMsg = document.querySelector("#status-message");

  function showMessage(text, color = "green") {
    statusMsg.textContent = text;
    statusMsg.classList.remove("hidden", "status-red", "status-green");
    statusMsg.classList.add(color === "red" ? "status-red" : "status-green");
  }

  document.querySelector("#send-sms").addEventListener("click", function () {
    showMessage("📱 SMS feature will be available soon.");
  });

  document.querySelector("#send-email").addEventListener("click", function () {
    showMessage("📧 Email feature will be available soon.");
  });
});
