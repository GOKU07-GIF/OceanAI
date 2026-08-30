import { create } from "zustand";

export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  phone_number: string;
  role: string;
  language: string;
  profile_image: string | null;
  is_email_verified: boolean;
  is_phone_verified: boolean;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;

  setUser: (user: User) => void;

  updateUser: (user: User) => void;

  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,

  isAuthenticated: false,

  setUser: (user: User) =>
    set({
      user,
      isAuthenticated: true,
    }),

  updateUser: (user: User) =>
    set({
      user,
      isAuthenticated: true,
    }),

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    set({
      user: null,
      isAuthenticated: false,
    });
  },
}));