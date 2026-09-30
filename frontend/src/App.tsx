import { Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { CategoriesListPage } from "./pages/CategoriesListPage";
import { CourseBuilderPage } from "./pages/CourseBuilderPage";
import { CoursePlayerPage } from "./pages/CoursePlayerPage";
import { CoursesListPage } from "./pages/CoursesListPage";
import { DashboardPage } from "./pages/DashboardPage";
import { EnrollmentsPage } from "./pages/EnrollmentsPage";
import { GroupsListPage } from "./pages/GroupsListPage";
import { LoginPage } from "./pages/LoginPage";
import { MyCoursesPage } from "./pages/MyCoursesPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ReportsPage } from "./pages/ReportsPage";
import { UsersListPage } from "./pages/UsersListPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";

const COURSE_ROLES = ["SUPERADMIN", "ADMIN", "INSTRUCTOR"];

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <DashboardPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/usuarios"
        element={
          <ProtectedRoute roles={["SUPERADMIN", "ADMIN"]}>
            <AppLayout>
              <UsersListPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/grupos"
        element={
          <ProtectedRoute roles={["SUPERADMIN", "ADMIN"]}>
            <AppLayout>
              <GroupsListPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/categorias"
        element={
          <ProtectedRoute roles={["SUPERADMIN", "ADMIN"]}>
            <AppLayout>
              <CategoriesListPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/cursos"
        element={
          <ProtectedRoute roles={COURSE_ROLES}>
            <AppLayout>
              <CoursesListPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/cursos/:id"
        element={
          <ProtectedRoute roles={COURSE_ROLES}>
            <AppLayout>
              <CourseBuilderPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/matriculas"
        element={
          <ProtectedRoute roles={["SUPERADMIN", "ADMIN"]}>
            <AppLayout>
              <EnrollmentsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mis-cursos"
        element={
          <ProtectedRoute>
            <AppLayout>
              <MyCoursesPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mis-cursos/:id"
        element={
          <ProtectedRoute>
            <AppLayout>
              <CoursePlayerPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reportes"
        element={
          <ProtectedRoute roles={["SUPERADMIN", "ADMIN"]}>
            <AppLayout>
              <ReportsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
