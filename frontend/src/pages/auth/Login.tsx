import LoginForm from "../../components/forms/LoginForm";

export default function Login(): React.JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-6">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-cyan-400">
            🌊 OceanAI
          </h1>

          <p className="mt-2 text-gray-400">
            AI Powered Ocean Intelligence Platform
          </p>
        </div>

        <LoginForm />
      </div>
    </div>
  );
}