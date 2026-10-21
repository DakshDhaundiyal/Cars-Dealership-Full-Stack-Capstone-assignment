import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const EMPTY_FORM = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
};

export default function Register() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [status, setStatus] = useState({ kind: "", message: "" });

  function update(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setStatus({ kind: "pending", message: "Creating your account…" });

    try {
      const response = await fetch(`${API_BASE}/djangoapp/api/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Unable to register.");
      }

      setStatus({
        kind: "success",
        message: `Account created for ${result.username}. You can now log in.`,
      });
      setForm(EMPTY_FORM);
    } catch (error) {
      setStatus({
        kind: "error",
        message: error.message || "Could not connect to the server.",
      });
    }
  }

  return (
    <section className="register-card" aria-labelledby="register-heading">
      <p className="eyebrow">GET STARTED</p>
      <h1 id="register-heading">Sign-up</h1>
      <h2>Create your account</h2>
      <p className="subtext">Enter all five details to register.</p>

      <form onSubmit={submit} className="register-form">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          value={form.username}
          onChange={update}
          autoComplete="username"
          minLength={3}
          required
        />

        <div className="two-col">
          <div>
            <label htmlFor="first_name">First Name</label>
            <input
              id="first_name"
              name="first_name"
              value={form.first_name}
              onChange={update}
              autoComplete="given-name"
              required
            />
          </div>
          <div>
            <label htmlFor="last_name">Last Name</label>
            <input
              id="last_name"
              name="last_name"
              value={form.last_name}
              onChange={update}
              autoComplete="family-name"
              required
            />
          </div>
        </div>

        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          value={form.email}
          onChange={update}
          autoComplete="email"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          value={form.password}
          onChange={update}
          autoComplete="new-password"
          minLength={8}
          required
        />

        <button type="submit" disabled={status.kind === "pending"}>
          {status.kind === "pending" ? "Creating account…" : "Register"}
        </button>
        <p role="status" aria-live="polite" className={`status ${status.kind}`}>
          {status.message}
        </p>
      </form>

      <p className="signin-note">
        Already registered? <a href={`${API_BASE}/login/`}>Log in</a>
      </p>
    </section>
  );
}
