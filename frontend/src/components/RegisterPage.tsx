import {
  AlertCircle,
  ArrowRight,
  GraduationCap,
  KeyRound,
  Loader2,
  Lock,
  Mail,
  ShieldAlert,
  User as UserIcon,
} from "lucide-react";
import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import type { UserRole } from "../types/auth";

interface RegisterPageProps {
  onSuccess: () => void;
  onNavigateToLogin: () => void;
}

export function RegisterPage({ onSuccess, onNavigateToLogin }: RegisterPageProps) {
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        name: name.trim(),
        email: email.trim(),
        password,
        role,
      });
      onSuccess();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to create account. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon-badge">
            <Lock size={24} />
          </div>
          <h2>Create Account</h2>
          <p>Join the JCET CampusIQ intelligent campus platform</p>
        </div>

        {error && (
          <div className="auth-error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="reg-name">Full Name</label>
            <div className="input-wrapper">
              <UserIcon className="input-icon" size={18} />
              <input
                id="reg-name"
                type="text"
                required
                placeholder="e.g. John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isSubmitting}
                autoComplete="name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="reg-email">Institutional Email</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input
                id="reg-email"
                type="email"
                required
                placeholder="name@jcet.ac.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
                autoComplete="email"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="reg-password">Password (min 8 characters)</label>
            <div className="input-wrapper">
              <KeyRound className="input-icon" size={18} />
              <input
                id="reg-password"
                type="password"
                required
                minLength={8}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isSubmitting}
                autoComplete="new-password"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Select Role</label>
            <div className="role-selector">
              <button
                type="button"
                className={`role-option-btn ${role === "student" ? "selected" : ""}`}
                onClick={() => setRole("student")}
                disabled={isSubmitting}
              >
                <GraduationCap size={18} />
                <div className="role-option-text">
                  <strong>Student</strong>
                  <span>Ask queries & explore knowledge</span>
                </div>
              </button>

              <button
                type="button"
                className={`role-option-btn ${role === "admin" ? "selected" : ""}`}
                onClick={() => setRole("admin")}
                disabled={isSubmitting}
              >
                <ShieldAlert size={18} />
                <div className="role-option-text">
                  <strong>Administrator</strong>
                  <span>Manage documents & analytics</span>
                </div>
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn-primary-auth"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                <span>Creating account...</span>
              </>
            ) : (
              <>
                <span>Create Account</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account?{" "}
            <button
              type="button"
              onClick={onNavigateToLogin}
              className="btn-link"
            >
              Sign in instead
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
