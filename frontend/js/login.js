const loginForm = document.getElementById("login-form");

if (tokens.access) window.location.href = "profile.html";

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await api("/auth/login", { method: "POST", body: formData(loginForm), auth: false });
    tokens.save(data);
    window.location.href = "profile.html";
  } catch (error) {
    if (error.status === 401) error.message = "Неправильний логін або пароль.";
    showErrors(loginForm, error);
  }
});
