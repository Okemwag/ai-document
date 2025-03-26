"use client";
import React, { useState } from "react";
import axios from "axios";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";

import { signUpSchema } from "@/utils/validation";

const SignUpForm = () => {
  const navigate = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  interface SignUpFormData {
    username: string;
    email: string;
    password: string;
    confirmPassword?: string;
  }


  const onSubmit = async (data: SignUpFormData) => {
    const signUpPayload: SignUpFormData = {
      username: data.username,
      email: data.email,
      password: data.password,
    };
    const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;
    setIsLoading(true);

    try {
      console.log("Form data:", signUpPayload);
      const response = await axios.post(
        `${DEV_API_URL}/api/accounts/register/`,
        signUpPayload
      );
      if (response.status === 201 ) {
        navigate.push("/sign-in")

      }
      console.log("Registration response data:", response.data);
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
          <h1 className="text-3xl font-bold">Sign Up</h1>
          <p className="text-muted-foreground">
            Enter your details to create your account
          </p>
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

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium">
                Confirm Password
              </label>
              <input
                {...register("confirmPassword")}
                type="password"
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-all duration-200 ${
                  errors.confirmPassword
                    ? "border-red-500 focus:ring-red-200"
                    : "border-gray-300 focus:ring-blue-200 focus:border-blue-400"
                }`}
                disabled={buttonIsLoading}
              />
              {errors.confirmPassword && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.confirmPassword.message}
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
              {isLoading ? "Signing you up..." : "Sign Up"}
            </button>
          </div>
        </form>

        <div className="mt-4 text-center text-sm">
          Have an account?{" "}
          <Link href="/sign-in" className="text-secondaryColor hover:underline">
            Log In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SignUpForm;