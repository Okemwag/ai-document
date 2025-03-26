"use client";

import { useState, useRef, SetStateAction } from "react";
import { useRouter } from "next/navigation";

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleDrag = (e: {
    preventDefault: () => void;
    stopPropagation: () => void;
    type: string;
  }) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (selectedFile: SetStateAction<null> | File) => {
    // Check file type
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain",
    ];

    if (
      selectedFile instanceof File &&
      validTypes.includes(selectedFile.type)
    ) {
      setFile(selectedFile);
      setError("");
    } else {
      setFile(null);
      setError("Please upload a valid file (PDF, DOCX, or TXT)");
    }
  };

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;

    if (!file) {
      setError("Please select a file to upload");
      return;
    }

    setLoading(true);

    // Create form data
    const formData = new FormData();
    formData.append("original_file", file);

    // Get auth token from local storage
    const resourceAuthToken = localStorage.getItem("authToken");
    console.log(formData);
    try {
      const response = await fetch(`${DEV_API_URL}/api/upload/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${resourceAuthToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload document");
      }

      const data = await response.json();

      // Redirect to the document view page
      router.push(`/documents/${data.documentId}`);
    } catch (err) {
      console.error("Error uploading document:", err);
      setError("Failed to upload document. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Upload Document
          </h2>

          <form onSubmit={handleSubmit}>
            <div
              className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors
                ${
                  dragActive
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-300 hover:border-blue-400"
                }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileInput}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".pdf,.docx,.txt"
                onChange={(e) => {
                  if (e.target.files) {
                    handleFileChange(e.target.files[0]);
                  }
                }}
              />

              <div className="flex flex-col items-center justify-center space-y-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>

                <div className="text-gray-700">
                  <p className="font-medium">
                    Drag and drop your file here or click to browse
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Supports PDF, DOCX, and TXT (Max 10MB)
                  </p>
                </div>

                {file && (
                  <div className="mt-2 text-sm text-gray-800 bg-gray-100 rounded px-3 py-1">
                    {file.name}
                  </div>
                )}
              </div>
            </div>

            {error && <div className="mt-4 text-red-500 text-sm">{error}</div>}

            <div className="mt-6">
              <button
                type="submit"
                className={`w-full py-3 px-4 rounded-md text-white font-medium transition-colors
                  ${
                    loading
                      ? "bg-blue-400 cursor-not-allowed"
                      : "bg-blue-600 hover:bg-blue-700"
                  }`}
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Processing...
                  </span>
                ) : (
                  "Upload & Analyze Document"
                )}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <h3 className="font-medium text-gray-700 mb-2">
              Accepted File Types:
            </h3>
            <div className="flex flex-wrap gap-2">
              <div className="bg-gray-100 rounded px-3 py-1 text-sm">
                <span className="font-medium">.pdf</span> - PDF Documents
              </div>
              <div className="bg-gray-100 rounded px-3 py-1 text-sm">
                <span className="font-medium">.docx</span> - Word Documents
              </div>
              <div className="bg-gray-100 rounded px-3 py-1 text-sm">
                <span className="font-medium">.txt</span> - Text Files
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}