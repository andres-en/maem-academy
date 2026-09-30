import { GoogleLogin } from "@react-oauth/google";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import maemLogo from "../assets/maem-logo.png";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/apiClient";

export function LoginPage() {
  const { user, systemInfo, loginGoogle } = useAuth();
  const [error, setError] = useState<string | null>(null);

  if (user) {
    return <Navigate to="/" replace />;
  }

  async function handleGoogleSuccess(credentialResponse: { credential?: string }) {
    setError(null);
    if (!credentialResponse.credential) return;
    try {
      await loginGoogle(credentialResponse.credential);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not sign in with Google.");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0a1330] p-6">
      <div className="flex w-full max-w-5xl overflow-hidden rounded-3xl bg-white shadow-2xl md:min-h-[600px]">
        <div className="flex w-full flex-col px-10 py-12 sm:px-16 sm:py-16 md:w-1/2">
          <img src={maemLogo} alt="MAEM Academy" className="h-14 w-auto self-start" />

          <div className="flex flex-1 flex-col justify-center py-10">
            <h1 className="text-2xl font-semibold text-gray-900">Welcome back</h1>
            <p className="mt-2 text-sm text-gray-500">Sign in with your Google account to continue</p>

            {error && (
              <div className="mt-6 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
            )}

            <div className="mt-8">
              {systemInfo?.google_oauth_enabled ? (
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => setError("Google sign-in failed.")}
                />
              ) : (
                <p className="text-sm text-gray-400">
                  Google OAuth is not configured in the backend yet (GOOGLE_CLIENT_ID).
                </p>
              )}
            </div>
          </div>

          <p className="text-xs text-gray-400">© {new Date().getFullYear()} MAEM Academy</p>
        </div>

        <div className="relative hidden w-1/2 overflow-hidden md:block">
          <div className="absolute inset-0 bg-gradient-to-br from-[#0b1e4d] via-[#0e5b8f] to-[#12a37f]" />
          <div className="absolute -left-16 -top-24 h-72 w-72 rounded-full bg-sky-400/40 blur-3xl" />
          <div className="absolute right-0 top-1/3 h-80 w-80 rounded-full bg-emerald-400/30 blur-3xl" />
          <div className="absolute -bottom-16 left-10 h-64 w-64 rounded-full bg-blue-600/40 blur-3xl" />

          <div className="relative flex h-full flex-col justify-end p-14 text-white">
            <h2 className="text-4xl font-bold">Welcome.</h2>
            <p className="mt-3 max-w-xs text-sm text-white/80">
              Train, assess and track your team's growth, all in one place.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
