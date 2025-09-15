// src/api/auth.ts
import api from "./client";

export type LoginResp = { access_token: string; token_type: string };
export async function login(email: string, password: string) {
  // adapte si ton backend attend username/password ou email/password
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  const { data } = await api.post<LoginResp>("/auth/token", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}
