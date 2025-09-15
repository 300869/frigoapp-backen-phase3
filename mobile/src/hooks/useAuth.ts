import { useAuthStore } from '../store/auth.store';

export function useAuth() {
  const token = useAuthStore((s) => s.token);
  const login = useAuthStore((s) => s.login);
  const logout = useAuthStore((s) => s.logout);
  return { token, login, logout };
}
