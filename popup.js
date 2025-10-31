alert("Popup loaded!");
console.log("TEST: Popup script is working");

const API_ENDPOINT = "https://phishing-detector-api-1.onrender.com/predict";
const statusEl = document.getElementById("status");
const btn = document.getElementById("analyze");

btn.addEventListener("click", () => {
  alert("Button clicked!");
  console.log("Button was clicked");
});
