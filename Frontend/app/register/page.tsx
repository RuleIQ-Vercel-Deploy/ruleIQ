"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/auth-layout";

export default function RegisterPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("register");

  const handleModeChange = (newMode: "login" | "register") => {
    setMode(newMode);
    if (newMode === "login") {
      router.push("/login");
    }
  };

  return <AuthLayout mode={mode} onModeChange={handleModeChange} />;
}
