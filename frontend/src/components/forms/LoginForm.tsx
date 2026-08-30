import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import axios from "axios";

import {
  login,
  getCurrentUser,
} from "../../services/auth";

import { useAuthStore } from "../../store/authStore";

interface LoginData {
  username: string;
  password: string;
}

export default function LoginForm(): React.JSX.Element {
  const navigate = useNavigate();

  const { setUser } = useAuthStore();

  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginData>();

  async function onSubmit(data: LoginData) {
    try {
      setLoading(true);

      // Step 1: Login
      const response = await login(data);

      // Step 2: Save tokens
      localStorage.setItem(
        "access_token",
        response.access_token
      );

      localStorage.setItem(
        "refresh_token",
        response.refresh_token
      );

      // Step 3: Get currently logged-in user
      const user = await getCurrentUser();

      // Step 4: Save user in Zustand
      setUser(user);

      toast.success("Login Successful");

      // Step 5: Go to dashboard
      navigate("/dashboard");

    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        toast.error(
          error.response?.data?.detail ??
          "Login Failed"
        );
      } else {
        toast.error("Login Failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-md rounded-2xl bg-slate-800 p-8 shadow-xl">

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-6"
      >

        {/* Email */}
        <div>
          <label className="mb-2 block text-white">
            Email
          </label>

          <input
            type="text"
            autoComplete="username"
            {...register("username", {
              required: "Email is required",
            })}
            className="w-full rounded-lg border border-gray-600 bg-slate-900 p-3 text-white outline-none focus:border-cyan-500"
          />

          {errors.username && (
            <p className="mt-1 text-sm text-red-500">
              {errors.username.message}
            </p>
          )}
        </div>

        {/* Password */}
        <div>
          <label className="mb-2 block text-white">
            Password
          </label>

          <input
            type="password"
            autoComplete="current-password"
            {...register("password", {
              required: "Password is required",
            })}
            className="w-full rounded-lg border border-gray-600 bg-slate-900 p-3 text-white outline-none focus:border-cyan-500"
          />

          {errors.password && (
            <p className="mt-1 text-sm text-red-500">
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Login Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-cyan-600 py-3 font-semibold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading
            ? "Signing In..."
            : "Login"}
        </button>

      </form>
    </div>
  );
}