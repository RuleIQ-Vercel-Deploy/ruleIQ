"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Label } from "@/components/ui/label";
import { InputSimple as Input } from "@/components/ui/input-simple";
import { Button } from "@/components/ui/button";
import { IconBrandGoogle } from "@tabler/icons-react";
import { RuleIQLogo } from "@/components/ruleiq-logo";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/auth-store";
import { loginSchema, registerSchema } from "@/lib/validators";
import { toast } from "sonner";

const MicrosoftIcon = () => (
  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
    <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z"/>
  </svg>
);

const SlackIcon = () => (
  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
    <path d="M5.042 15.165a2.528 2.528 0 0 0 2.5 2.5c1.61 0 2.906-1.66 2.906-3.257 0-1.597-1.296-3.257-2.906-3.257a2.528 2.528 0 0 0-2.5 2.5v1.514zm.906-2.014c.72 0 1.395.99 1.395 1.757 0 .767-.675 1.757-1.395 1.757-.72 0-1.395-.99-1.395-1.757 0-.767.675-1.757 1.395-1.757z"/>
  </svg>
);

interface AuthLayoutProps {
  mode: "login" | "register";
  onModeChange: (mode: "login" | "register") => void;
}

export default function AuthLayout({ mode, onModeChange }: AuthLayoutProps) {
  const router = useRouter();
  const { login } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      if (mode === "login") {
        // Basic validation first
        if (!formData.email || !formData.password) {
          setErrors({ general: "Please fill in all fields" });
          return;
        }

        // Validate login data with try-catch
        let validatedData;
        try {
          validatedData = loginSchema.parse({
            email: formData.email,
            password: formData.password,
          });
        } catch (validationError: any) {
          if (validationError.errors) {
            const fieldErrors: Record<string, string> = {};
            validationError.errors.forEach((err: any) => {
              if (err.path.length > 0) {
                fieldErrors[err.path[0]] = err.message;
              }
            });
            setErrors(fieldErrors);
          }
          return;
        }

        // Call login API (this will fail gracefully for now)
        try {
          const { tokens, user } = await authApi.login(validatedData);
          login(tokens, user);
          toast.success("Welcome back! Redirecting to dashboard...");
          router.push("/dashboard");
        } catch (apiError: any) {
          toast.error("Login feature coming soon! API not connected yet.");
          console.log("API not connected - this is expected for demo");
        }
      } else {
        // Basic validation first
        if (!formData.email || !formData.password || !formData.confirmPassword) {
          setErrors({ general: "Please fill in all fields" });
          return;
        }

        if (formData.password !== formData.confirmPassword) {
          setErrors({ confirmPassword: "Passwords don't match" });
          return;
        }

        // Validate registration data with try-catch
        let validatedData;
        try {
          validatedData = registerSchema.parse({
            email: formData.email,
            password: formData.password,
            confirmPassword: formData.confirmPassword,
          });
        } catch (validationError: any) {
          if (validationError.errors) {
            const fieldErrors: Record<string, string> = {};
            validationError.errors.forEach((err: any) => {
              if (err.path.length > 0) {
                fieldErrors[err.path[0]] = err.message;
              }
            });
            setErrors(fieldErrors);
          }
          return;
        }

        // Call register API (this will fail gracefully for now)
        try {
          const { tokens, user } = await authApi.register(validatedData);
          login(tokens, user);
          toast.success("Account created successfully! Redirecting to dashboard...");
          router.push("/dashboard");
        } catch (apiError: any) {
          toast.error("Registration feature coming soon! API not connected yet.");
          console.log("API not connected - this is expected for demo");
        }
      }
    } catch (error: any) {
      console.error("Authentication error:", error);

      if (error.name === "ZodError") {
        // Handle validation errors
        const fieldErrors: Record<string, string> = {};
        error.errors.forEach((err: any) => {
          if (err.path.length > 0) {
            fieldErrors[err.path[0]] = err.message;
          }
        });
        setErrors(fieldErrors);
        toast.error("Please check your input and try again.");
      } else if (error.response?.status === 401) {
        // Handle authentication errors
        toast.error("Invalid email or password. Please try again.");
        setErrors({ general: "Invalid email or password" });
      } else if (error.response?.status === 409) {
        // Handle registration conflicts (user already exists)
        toast.error("An account with this email already exists.");
        setErrors({ email: "An account with this email already exists" });
      } else {
        // Handle other errors
        toast.error("Something went wrong. Please try again.");
        setErrors({ general: "An unexpected error occurred" });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 dark:from-blue-500/5 dark:to-purple-500/5" />
        <div className="flex items-center justify-center w-full z-10">
          <RuleIQLogo variant="cyan" size="lg" />
        </div>
      </div>

      <div className="w-full lg:w-1/2 flex items-center justify-center bg-white dark:bg-gray-900 relative">
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-blue-50/20 to-transparent dark:from-gray-800/20" />
        
        <div className="w-full max-w-md p-8 relative z-10">
          <div className="bg-white dark:bg-gray-900 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {mode === "login" ? "Welcome back" : "Create your account"}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                {mode === "login"
                  ? "Sign in to your compliance dashboard"
                  : "Join ruleIQ to get started"
                }
              </p>
              {errors.general && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">{errors.general}</p>
                </div>
              )}
            </div>

            <div className="space-y-3 mb-6">
              <Button
                variant="outline"
                className="w-full h-11 flex items-center justify-center space-x-3"
                type="button"
              >
                <IconBrandGoogle className="h-5 w-5" />
                <span>Continue with Google</span>
              </Button>
              
              <Button
                variant="outline"
                className="w-full h-11 flex items-center justify-center space-x-3"
                type="button"
              >
                <MicrosoftIcon />
                <span>Continue with Microsoft</span>
              </Button>

              <Button
                variant="outline"
                className="w-full h-11 flex items-center justify-center space-x-3"
                type="button"
              >
                <SlackIcon />
                <span>Continue with Slack</span>
              </Button>
            </div>

            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300 dark:border-gray-600" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-gray-900 text-gray-500">
                  Or continue with email
                </span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "register" && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName">First name</Label>
                    <Input
                      id="firstName"
                      name="firstName"
                      type="text"
                      placeholder="John"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="lastName">Last name</Label>
                    <Input
                      id="lastName"
                      name="lastName"
                      type="text"
                      placeholder="Doe"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      className="mt-1"
                    />
                  </div>
                </div>
              )}

              <div>
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="john@company.com"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`mt-1 ${errors.email ? 'border-red-500' : ''}`}
                  disabled={isLoading}
                />
                {errors.email && (
                  <p className="text-sm text-red-600 mt-1">{errors.email}</p>
                )}
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`mt-1 ${errors.password ? 'border-red-500' : ''}`}
                  disabled={isLoading}
                />
                {errors.password && (
                  <p className="text-sm text-red-600 mt-1">{errors.password}</p>
                )}
              </div>

              {mode === "register" && (
                <div>
                  <Label htmlFor="confirmPassword">Confirm password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className={`mt-1 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                    disabled={isLoading}
                  />
                  {errors.confirmPassword && (
                    <p className="text-sm text-red-600 mt-1">{errors.confirmPassword}</p>
                  )}
                </div>
              )}

              <Button type="submit" className="w-full h-11 mt-6" disabled={isLoading}>
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>{mode === "login" ? "Signing in..." : "Creating account..."}</span>
                  </div>
                ) : (
                  mode === "login" ? "Sign in" : "Create account"
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
                <button
                  type="button"
                  onClick={() => onModeChange(mode === "login" ? "register" : "login")}
                  className="text-blue-600 hover:text-blue-500 dark:text-blue-400 font-medium"
                >
                  {mode === "login" ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
