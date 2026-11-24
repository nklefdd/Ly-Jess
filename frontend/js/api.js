const API_URL = "http://127.0.0.1:8000/api";

const tokens = {
  get access() {
    return sessionStorage.getItem("access");
  },
  get refresh() {
    return sessionStorage.getItem("refresh");
  },
  save({ access, refresh }) {
    if (access) sessionStorage.setItem("access", access);
    if (refresh) sessionStorage.setItem("refresh", refresh);
  },
  clear() {
    sessionStorage.removeItem("access");
    sessionStorage.removeItem("refresh");
  },
};

class ApiError extends Error {
  constructor(status, message, details = {}) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

async function parseResponse(response) {
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = data.error || {};
    throw new ApiError(response.status, error.message || "Сталася помилка.", error.details);
  }
  return data;
}

async function refreshAccess() {
  if (!tokens.refresh) return false;
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!response.ok) {
    tokens.clear();
    return false;
  }
  tokens.save(await response.json());
  return true;
}

// Виконує запит до API. Якщо access-токен прострочений, оновлює його і повторює запит.
async function api(path, { method = "GET", body, auth = true } = {}) {
  const send = () => {
    const headers = { "Content-Type": "application/json" };
    if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`;
    return fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  };

  let response = await send();
  if (response.status === 401 && auth && (await refreshAccess())) {
    response = await send();
  }
  return parseResponse(response);
}

function showErrors(form, error) {
  form.querySelectorAll(".field-error").forEach((el) => (el.textContent = ""));
  const general = form.querySelector(".form-error");
  general.textContent = error.message;
  Object.entries(error.details || {}).forEach(([field, messages]) => {
    const el = form.querySelector(`[data-error-for="${field}"]`);
    if (el) el.textContent = [].concat(messages).join(" ");
  });
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}
