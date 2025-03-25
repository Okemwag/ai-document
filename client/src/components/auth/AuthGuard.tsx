"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const AuthGuard = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();

  useEffect(() => {
    // Check for token in localStorage
    const authToken =
      typeof window !== "undefined" ? localStorage.getItem("authToken") : null;

    if (!authToken) {
      router.push("/sign-in");
    }
  }, [router]);
  return <div>{children}</div>;
};

export default AuthGuard;