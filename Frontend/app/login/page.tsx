"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/auth-layout";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");

  const handleModeChange = (newMode: "login" | "register") => {
    setMode(newMode);
    if (newMode === "register") {
      router.push("/register");
    }
  };

  return <AuthLayout mode={mode} onModeChange={handleModeChange} />;
}