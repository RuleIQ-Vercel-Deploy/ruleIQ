"use client";

import { useState } from "react";
import LoginFormDemo from "@/components/login-form-demo";
import SignupFormDemo from "@/components/signup-form-demo";
import { Button } from "@/components/ui/button";

export default function DemoPage() {
  const [activeForm, setActiveForm] = useState<"login" | "signup">("login");

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-neutral-800 dark:text-neutral-200 mb-4">
            NexCompli Auth Forms
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 mb-6">
            Modern authentication forms with motion effects
          </p>
          
          {/* Toggle Buttons */}
          <div className="flex justify-center space-x-4 mb-8">
            <Button
              variant={activeForm === "login" ? "default" : "outline"}
              onClick={() => setActiveForm("login")}
              className="px-6 py-2"
            >
              Login Form
            </Button>
            <Button
              variant={activeForm === "signup" ? "default" : "outline"}
              onClick={() => setActiveForm("signup")}
              className="px-6 py-2"
            >
              Signup Form
            </Button>
          </div>
        </div>

        {/* Form Display */}
        <div className="flex justify-center">
          {activeForm === "login" ? (
            <LoginFormDemo />
          ) : (
            <SignupFormDemo />
          )}
        </div>

        {/* Features */}
        <div className="mt-12 text-center">
          <h3 className="text-xl font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
            Features
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="p-4 bg-white dark:bg-neutral-800 rounded-lg shadow-sm">
              <h4 className="font-medium text-neutral-800 dark:text-neutral-200 mb-2">
                Motion Effects
              </h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Interactive hover effects with radial gradients on input fields
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-neutral-800 rounded-lg shadow-sm">
              <h4 className="font-medium text-neutral-800 dark:text-neutral-200 mb-2">
                Dark Mode
              </h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Seamless dark/light theme support with proper contrast
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-neutral-800 rounded-lg shadow-sm">
              <h4 className="font-medium text-neutral-800 dark:text-neutral-200 mb-2">
                OAuth Ready
              </h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                GitHub and Google OAuth integration buttons included
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
