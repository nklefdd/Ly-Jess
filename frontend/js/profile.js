const profileForm = document.getElementById("profile-form");
const greeting = document.getElementById("greeting");
const roleBadge = document.getElementById("role");
const savedMessage = document.getElementById("saved");

function fillProfile(user) {
  greeting.textContent = `Вітаємо, ${user.first_name || user.username}!`;
  roleBadge.textContent = user.role === "admin" ? "Адміністратор" : "Покупець";
  ["first_name", "last_name", "email", "phone"].forEach((field) => {
    profileForm.elements[field].value = user[field] || "";
  });
}

async function loadProfile() {
  try {
    fillProfile(await api("/auth/me"));
  } catch (error) {
    tokens.clear();
    window.location.href = "index.html";
  }
}

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  savedMessage.textContent = "";
  try {
    fillProfile(await api("/auth/me", { method: "PATCH", body: formData(profileForm) }));
    showErrors(profileForm, { message: "", details: {} });
    savedMessage.textContent = "Зміни збережено.";
  } catch (error) {
    showErrors(profileForm, error);
  }
});

document.getElementById("logout").addEventListener("click", async () => {
  try {
    await api("/auth/logout", { method: "POST", body: { refresh: tokens.refresh } });
  } finally {
    tokens.clear();
    window.location.href = "index.html";
  }
});

loadProfile();
