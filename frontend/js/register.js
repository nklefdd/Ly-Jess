const registerForm = document.getElementById("register-form");

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const body = formData(registerForm);
  try {
    await api("/auth/register", { method: "POST", body, auth: false });
    const data = await api("/auth/login", {
      method: "POST",
      body: { username: body.username, password: body.password },
      auth: false,
    });
    tokens.save(data);
    window.location.href = "profile.html";
  } catch (error) {
    showErrors(registerForm, error);
  }
});
