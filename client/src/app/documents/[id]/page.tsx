"use client";

import { useState, useEffect } from "react";


interface ComparisonViewProps {
  documentId: string;
}

interface DocumentVersion {
  id: string;
  version_type: string;
  content: string;
  file: string;
  suggestions?: Record<string, any>;
  created_at: string;
}

interface Document {
  id: string;
  user: number;
  title: string;
  status: string;
  uploaded_at: string;
  versions: DocumentVersion[];
}

export default function ComparisonView({ documentId }: ComparisonViewProps) {
  const [doc, setDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDocument = async () => {
    const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;
    console.log(DEV_API_URL);
    try {
      const response = await fetch(`${DEV_API_URL}/api/documents/${documentId}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        console.log(response);
        throw new Error("Failed to fetch document");
      }

      const data: Document = await response.json();
      setDoc(data);
    } catch (err) {
      console.error("Error fetching document:", err);
      setError("Failed to load document. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (documentId) {
      fetchDocument();
    }
  }, [documentId]);

  const getVersionContent = (type: string) => {
    if (!doc) return "";  // Handle case if `doc` is null
    const version = doc.versions.find(v => v.version_type === type);
    if (version) {
      return version.content;
    }
    return "No content available";  // Fallback message
  };

  const handleExport = async () => {
    try {
      const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;
      const response = await fetch(`${DEV_API_URL}/api/documents/${documentId}/export`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error("Failed to export document");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = doc?.title ? `${doc.title}_improved.docx` : "improved_document.docx";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error exporting document:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
        Document not found.
      </div>
    );
  }

  const originalContent = getVersionContent("original");
  const improvedContent = getVersionContent("improved");

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Document view section */}
      <div className="w-full lg:w-3/4 bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <div className="px-6 py-4">
            <h1 className="text-xl font-bold text-gray-800">{doc.title}</h1>
            <p className="text-sm text-gray-500">
              Uploaded on {new Date(doc.uploaded_at).toLocaleDateString()}
            </p>
          </div>

          <div className="flex border-b border-gray-200">
            <button
              className="px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600"
              onClick={() => {}}
            >
              Side by Side
            </button>
            <button
              className="px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600"
              onClick={() => {}}
            >
              Original
            </button>
            <button
              className="px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600"
              onClick={() => {}}
            >
              Improved
            </button>
          </div>
        </div>

        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">
            Original Document
          </h2>
          <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
            {originalContent}
          </div>

          <h2 className="text-lg font-semibold text-gray-700 mt-6 mb-3">
            Improved Document
          </h2>
          <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
            {improvedContent || "No improved content available."}
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600">No suggestions available</p>
          </div>

          <div className="flex space-x-2">
            <button
              className="px-4 py-2 bg-white border border-gray-300 rounded-md text-gray-700 text-sm font-medium hover:bg-gray-50"
              onClick={() => window.history.back()}
            >
              Back
            </button>
            <button
              className="px-4 py-2 bg-green-600 rounded-md text-white text-sm font-medium hover:bg-green-700"
              onClick={handleExport}
              disabled={!improvedContent}
            >
              Export Document
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
