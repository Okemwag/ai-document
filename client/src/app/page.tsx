"use client";
import Link from "next/link";
import DocumentUpload from "@/components/document/DocumentUpload";

export default function Home() {
  return (
    <div className="space-y-6 pb-10">
      {/* Short Intro */}
      <section className="text-center py-6 px-4">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Improve Your Documents with AI
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
          Our AI-powered assistant analyzes your documents and provides
          intelligent suggestions to enhance grammar, style, and clarity.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/sign-up"
            className="bg-blue-600 text-white font-medium py-3 px-6 rounded-md hover:bg-blue-700 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Smart Document Enhancement
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Grammar Correction
              </h3>
              <p className="text-gray-600">
                Automatically detect and fix grammatical errors, spelling
                mistakes, and punctuation issues.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-purple-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Style Enhancement
              </h3>
              <p className="text-gray-600">
                Improve your writing style with suggestions for better word
                choice, sentence structure, and tone.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-yellow-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Clarity Improvement
              </h3>
              <p className="text-gray-600">
                Identify and simplify complex sentences, remove ambiguity, and
                enhance overall readability.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Upload Section */}
      {/* <section className="py-4">
        <div className="max-w-4xl mx-auto">
          <DocumentUpload onSuccess={() => console.log("Upload successful")} />
        </div>
      </section> */}
    </div>
  );
}