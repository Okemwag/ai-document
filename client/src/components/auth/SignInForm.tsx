"use client";
import React, { useState } from "react";
import axios from "axios";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";


import { signInSchema } from "@/utils/validation";
const SignInForm = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(signInSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
    },
  });

  interface SignInFormData {
    username: string;
    email: string;
    password: string;
  }

  const onSubmit = async (data: SignInFormData) => {
    const signInPayload: SignInFormData = {
      username: data.username,
      email: data.email,
      password: data.password,
    };
    const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;
    setIsLoading(true);

    try {
      console.log("Form data:", signInPayload);
      const response = await axios.post(
        `${DEV_API_URL}/api/accounts/login/`,
        signInPayload
      );
      if (response.status === 200) {
        // access token
        const accessToken = response.data.token.access;
        console.log(accessToken);
        localStorage.setItem("accessToken", accessToken);
        navigate.push("/dashboard");
      }
    } catch (error) {
      console.error("Sign up failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const buttonIsLoading = isSubmitting || isLoading;

  return (
    <div className="flex items-center justify-center py-12">
      <div className="mx-auto w-[350px] space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Sign In</h1>
          <p className="text-muted-foreground">Welcome back</p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium">
                Username
              </label>
              <input
                {...register("username")}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-all duration-200 ${
                  errors.username
                    ? "border-red-500 focus:ring-red-200"
                    : "border-gray-300 focus:ring-blue-200 focus:border-blue-400"
                }`}
                placeholder="John_Doe"
                disabled={buttonIsLoading}
              />
              {errors.username && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.username.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <input
                {...register("email")}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-all duration-200 ${
                  errors.email
                    ? "border-red-500 focus:ring-red-200"
                    : "border-gray-300 focus:ring-blue-200 focus:border-blue-400"
                }`}
                placeholder="name@example.com"
                disabled={buttonIsLoading}
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <input
                {...register("password")}
                type="password"
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-all duration-200 ${
                  errors.password
                    ? "border-red-500 focus:ring-red-200"
                    : "border-gray-300 focus:ring-blue-200 focus:border-blue-400"
                }`}
                disabled={buttonIsLoading}
              />
              {errors.password && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.password.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-md font-medium hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              ) : null}
              {isLoading ? "Signing you in..." : "Sign In"}
            </button>
          </div>
        </form>

        <div className="mt-4 text-center text-sm">
          Don&apos;t have an account?{" "}
          <Link href="/sign-up" className="text-secondaryColor hover:underline">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SignInForm;