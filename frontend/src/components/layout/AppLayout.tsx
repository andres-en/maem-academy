import { useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import maemLogo from "../../assets/maem-logo.png";
import { useAuth } from "../../contexts/AuthContext";

interface NavItem {
  label: string;
  to?: string;
  comingSoon?: boolean;
}

const ADMIN_NAV: NavItem[] = [
  { label: "Dashboard", to: "/" },
  { label: "Users", to: "/usuarios" },
  { label: "Groups", to: "/grupos" },
  { label: "Categories", to: "/categorias" },
  { label: "Courses", to: "/cursos" },
  { label: "Enrollments", to: "/matriculas" },
  { label: "Reports", to: "/reportes" },
];

const INSTRUCTOR_NAV: NavItem[] = [
  { label: "Dashboard", to: "/" },
  { label: "Courses", to: "/cursos" },
];

const STUDENT_NAV: NavItem[] = [
  { label: "Home", to: "/" },
  { label: "My courses", to: "/mis-cursos" },
  { label: "In progress", to: "/mis-cursos?estado=en-progreso" },
  { label: "Completed", to: "/mis-cursos?estado=completados" },
];

function navForRole(roleName: string): NavItem[] {
  if (roleName === "SUPERADMIN" || roleName === "ADMIN") return ADMIN_NAV;
  if (roleName === "INSTRUCTOR") return INSTRUCTOR_NAV;
  return STUDENT_NAV;
}

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
    </svg>
  );
}

export function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navItems = navForRole(user?.role.name ?? "USER");
  const [sidebarOpen, setSidebarOpen] = useState(
    () => typeof window === "undefined" || window.innerWidth >= 768
  );

  return (
    <div className="flex min-h-screen bg-gray-50">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 overflow-hidden border-r border-gray-200 bg-white transition-transform duration-200 md:relative md:z-auto md:transition-[width] md:duration-200 ${
          sidebarOpen ? "translate-x-0 md:w-64" : "-translate-x-full md:w-0 md:border-r-0"
        } md:translate-x-0`}
      >
        <div className="flex w-64 shrink-0 flex-col">
          <div className="flex items-center justify-between gap-2 border-b border-gray-200 px-5 py-4">
            <img src={maemLogo} alt="MAEM Academy" className="h-auto w-36" />
            <button
              onClick={() => setSidebarOpen(false)}
              className="shrink-0 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 md:hidden"
              aria-label="Close menu"
            >
              <CloseIcon />
            </button>
          </div>
          <nav className="flex-1 space-y-1 px-3 py-4">
            {navItems.map((item) =>
              item.to ? (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end={item.to === "/"}
                  onClick={() => setSidebarOpen(window.innerWidth >= 768)}
                  className={({ isActive }) =>
                    `block rounded-lg px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-brand-50 text-brand-700" : "text-gray-600 hover:bg-gray-100"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ) : (
                <div
                  key={item.label}
                  className="flex cursor-not-allowed items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-gray-400"
                  title="Coming soon"
                >
                  <span>{item.label}</span>
                  <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-gray-400">
                    Coming soon
                  </span>
                </div>
              )
            )}
          </nav>
          <div className="border-t border-gray-200 px-4 py-4">
            <p className="truncate text-sm font-medium text-gray-800">{user?.full_name}</p>
            <p className="truncate text-xs text-gray-500">{user?.role.display_name}</p>
            <button
              onClick={logout}
              className="mt-3 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
            >
              Sign out
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center gap-3 border-b border-gray-200 bg-white px-4">
          <button
            onClick={() => setSidebarOpen((open) => !open)}
            className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            aria-label="Toggle menu"
          >
            <MenuIcon />
          </button>
          {!sidebarOpen && <img src={maemLogo} alt="MAEM Academy" className="h-6 w-auto" />}
        </header>
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
