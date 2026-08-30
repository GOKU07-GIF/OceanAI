import { useEffect, useState } from "react";
import {
  User,
  Bell,
  Lock,
  Mail,
  Save,
  Eye,
  EyeOff,
} from "lucide-react";
import toast from "react-hot-toast";

import {
  getCurrentUser,
  updateProfile,
  changePassword,
} from "../../services/auth";

export default function Settings(): React.JSX.Element {
  const [notifications, setNotifications] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [saving, setSaving] = useState(false);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [language, setLanguage] = useState("English");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const [loadingUser, setLoadingUser] = useState(true);

  // ===============================
  // LOAD CURRENT USER DATA
  // ===============================

  useEffect(() => {
    async function loadUser() {
      try {
        setLoadingUser(true);

        const user = await getCurrentUser();

        setFullName(user.full_name ?? "");
        setEmail(user.email ?? "");
        setPhoneNumber(user.phone_number ?? "");
        setLanguage(user.language ?? "English");
      } catch {
        toast.error("Failed to load user profile");
      } finally {
        setLoadingUser(false);
      }
    }

    loadUser();
  }, []);

  // ===============================
  // SAVE SETTINGS
  // ===============================

  const handleSave = async () => {
    try {
      setSaving(true);

      // Update profile
      await updateProfile({
        full_name: fullName,
        phone_number: phoneNumber,
        language,
      });

      // Change password only when user entered a new password
      if (newPassword.trim()) {
        if (!currentPassword.trim()) {
          toast.error("Please enter your current password");
          return;
        }

        await changePassword({
          current_password: currentPassword,
          new_password: newPassword,
        });

        // Important: never keep passwords after changing them
        setCurrentPassword("");
        setNewPassword("");

        toast.success("Password changed successfully");
      }

      toast.success("Settings saved successfully");
    } catch (error: unknown) {
      const message =
        error &&
        typeof error === "object" &&
        "response" in error
          ? (
              error as {
                response?: {
                  data?: {
                    detail?: string;
                  };
                };
              }
            ).response?.data?.detail
          : undefined;

      toast.error(message ?? "Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  if (loadingUser) {
    return (
      <div className="p-6 text-white">
        Loading settings...
      </div>
    );
  }

  return (
    <div className="min-h-full p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">
          Settings
        </h1>

        <p className="mt-2 text-slate-400">
          Manage your OceanAI account and application preferences.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Profile Settings */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-xl bg-cyan-500/10 p-3 text-cyan-400">
              <User size={24} />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-white">
                Profile Settings
              </h2>

              <p className="text-sm text-slate-400">
                Manage your personal information.
              </p>
            </div>
          </div>

          <div className="space-y-5">
            {/* Full Name */}
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Full Name
              </label>

              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                autoComplete="name"
                className="w-full rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            {/* Email */}
            <div>
              <label className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <Mail size={16} />
                Email Address
              </label>

              <input
                type="email"
                value={email}
                disabled
                className="w-full cursor-not-allowed rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-slate-400 outline-none"
              />

              <p className="mt-2 text-xs text-slate-500">
                Email address cannot be changed here.
              </p>
            </div>

            {/* Phone Number */}
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Phone Number
              </label>

              <input
                type="text"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="Enter your phone number"
                className="w-full rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            {/* Language */}
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Language
              </label>

              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi</option>
              </select>
            </div>
          </div>
        </div>

        {/* Application Preferences */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <h2 className="mb-6 text-xl font-semibold text-white">
            Application Preferences
          </h2>

          {/* Notifications */}
          <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-900 p-4">
            <div className="flex items-center gap-3">
              <Bell
                className="text-cyan-400"
                size={22}
              />

              <div>
                <h3 className="font-medium text-white">
                  Notifications
                </h3>

                <p className="text-sm text-slate-400">
                  Receive ocean monitoring alerts.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() =>
                setNotifications(!notifications)
              }
              className={`relative h-7 w-12 rounded-full transition ${
                notifications
                  ? "bg-cyan-600"
                  : "bg-slate-600"
              }`}
            >
              <span
                className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${
                  notifications
                    ? "right-1"
                    : "left-1"
                }`}
              />
            </button>
          </div>

          {/* Permanent Dark Theme Info */}
          <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900 p-4">
            <h3 className="font-medium text-white">
              OceanAI Appearance
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              OceanAI uses a permanent dark theme for a consistent ocean monitoring experience.
            </p>
          </div>
        </div>

        {/* Security */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6 lg:col-span-2">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-xl bg-red-500/10 p-3 text-red-400">
              <Lock size={24} />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-white">
                Security
              </h2>

              <p className="text-sm text-slate-400">
                Update your account security settings.
              </p>
            </div>
          </div>

          <div className="grid max-w-2xl gap-5">
            {/* Current Password */}
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Current Password
              </label>

              <input
                type="password"
                value={currentPassword}
                onChange={(e) =>
                  setCurrentPassword(e.target.value)
                }
                placeholder="Enter your current password"
                autoComplete="current-password"
                className="w-full rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />
            </div>

            {/* New Password */}
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                New Password
              </label>

              <div className="relative">
                <input
                  id="oceanai-new-password"
                  name="oceanai-new-password"
                  type={
                    showPassword ? "text" : "password"
                  }
                  value={newPassword}
                  onChange={(e) =>
                    setNewPassword(e.target.value)
                  }
                  placeholder="Enter a new password"
                  autoComplete="new-password"
                  className="w-full rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 pr-12 text-white outline-none transition focus:border-cyan-500"
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                  className="absolute right-4 top-3 text-slate-400 hover:text-white"
                >
                  {showPassword ? (
                    <EyeOff size={20} />
                  ) : (
                    <Eye size={20} />
                  )}
                </button>
              </div>

              <p className="mt-3 text-xs text-slate-500">
                Leave both password fields empty if you do not want to change your password.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="mt-8 flex justify-end">
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 rounded-xl bg-cyan-600 px-6 py-3 font-medium text-white transition hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Save size={20} />

          {saving
            ? "Saving..."
            : "Save Changes"}
        </button>
      </div>
    </div>
  );
}