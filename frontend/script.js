const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://127.0.0.1:8000" : "https://your-backend.onrender.com";

// Toggle visibility of Login and Sign Up forms
function showSignup() {
  document.getElementById("loginForm").style.display = "none";
  document.getElementById("signupForm").style.display = "block";
}

function showLogin() {
  document.getElementById("signupForm").style.display = "none";
  document.getElementById("loginForm").style.display = "block";
}

// Toggle password visibility
function togglePassword(id) {
  const input = document.getElementById(id);
  if (input.type === "password") {
    input.type = "text";
  } else {
    input.type = "password";
  }
}

// Signup functionality
async function signup() {
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!name || !email || !password) {
    alert("Please fill in all fields.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      // Backend expects 'fullname' not 'name', map it
      body: JSON.stringify({ fullname: name, email, password })
    });

    const data = await response.json();

    if (response.ok) {
      alert("Registration successful! Please login.");
      showLogin(); // Automatically switch to login screen
    } else {
      alert("Error: " + data.detail);
    }
  } catch (error) {
    console.error("Error connecting to server:", error);
    alert("Cannot connect to backend server.");
  }
}

// Login functionality
async function login() {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  if (!email || !password) {
    alert("Please fill in all fields.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
      alert("Login successful! Welcome " + data.user.fullname);
      // Save user to local storage for the dashboard
      localStorage.setItem("user", JSON.stringify(data.user));
      // Redirect to dashboard (index.html)
      window.location.href = "index.html"; 
    } else {
      alert("Error: " + data.detail);
    }
  } catch (error) {
    console.error("Error connecting to server:", error);
    alert("Cannot connect to backend server.");
  }
}
