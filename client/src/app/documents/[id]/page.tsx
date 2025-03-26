"use client";
import { useParams } from "next/navigation";
import { useState, useEffect } from "react";

interface DocumentVersion {
  id: string;
  version_type: string;
  content: string | Record<string, any>; // Allow both string and object content
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

export default function ComparisonView() {
  const { id } = useParams();
  const [doc, setDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeView, setActiveView] = useState<'side-by-side' | 'original' | 'improved'>('side-by-side');

  const fetchDocument = async () => {
    try {
      const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;
      const response = await fetch(`${DEV_API_URL}/api/documents/${id}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) {
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
    if (id) {
      fetchDocument();
    }
  }, [id]);

  const formatContent = (content: string | Record<string, any>): string => {
    if (typeof content === 'string') {
      return content;
    }
    
    // Format MongoDB documents/objects for better readability
    try {
      return JSON.stringify(content, null, 2);
    } catch {
      return "Unable to format content";
    }
  };

  const getVersionContent = (type: string) => {
    if (!doc) return "";
    const version = doc.versions.find(v => v.version_type === type);
    return version ? formatContent(version.content) : "No content available";
  };

  const handleExport = async () => {
    try {
      const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;
      const response = await fetch(`${DEV_API_URL}/api/documents/${id}/export/`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('authToken')}`
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
      a.download = doc?.title ? `${doc.title}_improved.json` : "improved_document.json";
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
    <div className="flex flex-col lg:flex-row gap-6 p-4">
      <div className="w-full bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <div className="px-6 py-4">
            <h1 className="text-xl font-bold text-gray-800">{doc.title}</h1>
            <p className="text-sm text-gray-500">
              Uploaded on {new Date(doc.uploaded_at).toLocaleDateString()}
              {doc.status && (
                <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                  doc.status === 'processed' ? 'bg-green-100 text-green-800' : 
                  doc.status === 'processing' ? 'bg-yellow-100 text-yellow-800' : 
                  'bg-gray-100 text-gray-800'
                }`}>
                  {doc.status}
                </span>
              )}
            </p>
          </div>

          <div className="flex border-b border-gray-200">
            <button
              className={`px-4 py-2 text-sm font-medium ${
                activeView === 'side-by-side' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'
              }`}
              onClick={() => setActiveView('side-by-side')}
            >
              Side by Side
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium ${
                activeView === 'original' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'
              }`}
              onClick={() => setActiveView('original')}
            >
              Original
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium ${
                activeView === 'improved' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'
              }`}
              onClick={() => setActiveView('improved')}
            >
              Improved
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeView === 'side-by-side' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-3">
                  Original Document
                </h2>
                <pre className="bg-gray-50 p-4 rounded border border-gray-200 overflow-y-auto text-sm">
                  {originalContent}
                </pre>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-3">
                  Improved Document
                </h2>
                <pre className="bg-gray-50 p-4 rounded border border-gray-200 overflow-y-auto text-sm">
                  {improvedContent}
                </pre>
              </div>
            </div>
          )}

          {activeView === 'original' && (
            <div>
              <h2 className="text-lg font-semibold text-gray-700 mb-3">
                Original Document
              </h2>
              <pre className="bg-gray-50 p-4 rounded border border-gray-200 overflow-y-auto text-sm max-h-[70vh]">
                {originalContent}
              </pre>
            </div>
          )}

          {activeView === 'improved' && (
            <div>
              <h2 className="text-lg font-semibold text-gray-700 mb-3">
                Improved Document
              </h2>
              <pre className="bg-gray-50 p-4 rounded border border-gray-200 overflow-y-auto text-sm max-h-[70vh]">
                {improvedContent}
              </pre>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div>
            {doc.versions[0]?.suggestions && (
              <div className="text-sm text-gray-600">
                Suggestions: {Object.keys(doc.versions[0].suggestions).length}
              </div>
            )}
          </div>

          <div className="flex space-x-2">
            <button
              className="px-4 py-2 bg-white border border-gray-300 rounded-md text-gray-700 text-sm font-medium hover:bg-gray-50"
              onClick={() => window.history.back()}
            >
              Back
            </button>
            <button
              className="px-4 py-2 bg-green-600 rounded-md text-white text-sm font-medium hover:bg-green-700 disabled:opacity-50"
              onClick={handleExport}
              disabled={!improvedContent || improvedContent === "No content available"}
            >
              Export Document
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}