import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 text-gray-600">
      <p className="text-4xl font-semibold">404</p>
      <p>Page not found.</p>
      <Link to="/" className="text-brand-600 hover:underline">
        Back to home
      </Link>
    </div>
  );
}
