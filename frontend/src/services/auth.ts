import api from "./api";

// ===============================
// TYPES
// ===============================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

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

export interface UpdateProfileData {
  full_name: string;
  phone_number: string;
  language: string;
  profile_image?: string | null;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

// ===============================
// LOGIN
// POST /auth/login
// ===============================

export async function login(
  data: LoginRequest
): Promise<LoginResponse> {
  const form = new URLSearchParams();

  form.append("username", data.username);
  form.append("password", data.password);

  const response = await api.post<LoginResponse>(
    "/auth/login",
    form,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
}

// ===============================
// GET CURRENT USER
// GET /auth/me
// ===============================

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>("/auth/me");

  return response.data;
}

// ===============================
// UPDATE PROFILE
// PUT /auth/profile
// ===============================

export async function updateProfile(
  data: UpdateProfileData
): Promise<User> {
  const response = await api.put<User>(
    "/auth/profile",
    data
  );

  return response.data;
}

// ===============================
// CHANGE PASSWORD
// PUT /auth/password
// ===============================

export async function changePassword(
  data: ChangePasswordData
): Promise<string> {
  const response = await api.put<string>(
    "/auth/password",
    data
  );

  return response.data;
}