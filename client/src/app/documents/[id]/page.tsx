"use client";

import { useState, useEffect } from "react";
import SuggestionsList from "@/components/document/SuggestionsList";

interface ComparisonViewProps {
  documentId: string;
}

interface Document {
  title: string;
  uploadedAt: string;
  originalContent: string;
  improvedContent: string;
  suggestions?: Suggestion[];
}

interface Suggestion {
  id: string;
  content: string;
  type: string;
  description: string;
  originalText: string;
  suggestedText: string;
}


export default function ComparisonView({ documentId }: ComparisonViewProps) {
  const [doc, setDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedSuggestion, setSelectedSuggestion] =
    useState<Suggestion | null>(null);
  const [viewMode, setViewMode] = useState("side-by-side"); // or 'original' or 'improved'
  
  const fetchDocument = async () => {
    const DEV_API_URL = process.env.NEXT_PUBLIC_DEV_BASE_API_URL;   
    try {
      const response = await fetch(`${DEV_API_URL}/api/documents/${documentId}`);

      if (!response.ok) {
        throw new Error("Failed to fetch document");
      }

      const data = await response.json();
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

  const handleSuggestionSelect = (suggestion: Suggestion) => {
    setSelectedSuggestion(suggestion);
  };

  const handleSuggestionAccept = async (suggestionId: any) => {
    try {
      // Replace with your actual API endpoint
      const response = await fetch(
        `/api/documents/${documentId}/suggestions/${suggestionId}/accept`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to accept suggestion");
      }

      // Refresh document data
      const updatedDoc = await response.json();
      setDoc(updatedDoc);

      // Clear selected suggestion
      setSelectedSuggestion(null);
    } catch (err) {
      console.error("Error accepting suggestion:", err);
      // Show error message
    }
  };

  const handleSuggestionReject = async (suggestionId: any) => {
    try {
      const response = await fetch(
        `/api/documents/${documentId}/suggestions/${suggestionId}/reject`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to reject suggestion");
      }

      // Refresh document data
      const updatedDoc = await response.json();
      setDoc(updatedDoc);

      // Clear selected suggestion
      setSelectedSuggestion(null);
    } catch (err) {
      console.error("Error rejecting suggestion:", err);
      // Show error message
    }
  };

  const handleExport = async () => {
    try {
    
      const response = await fetch(`/api/documents/${documentId}/export`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to export document");
      }

      // Get the exported document as a blob
      const blob = await response.blob();

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      if (!doc) {
        throw new Error("Document is null");
      }
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = doc.title
        ? `${doc.title}_improved.docx`
        : "improved_document.docx";

      // Append to the body and trigger download
      document.body.appendChild(a);
      a.click();

      // Clean up
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error exporting document:", err);
      // Show error message
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

  if (!document) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
        Document not found.
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Document view section */}
      <div className="w-full lg:w-3/4 bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <div className="px-6 py-4">
            <h1 className="text-xl font-bold text-gray-800">{doc?.title}</h1>
            <p className="text-sm text-gray-500">
              Uploaded on {new Date(doc?.uploadedAt ?? "").toLocaleDateString()}
            </p>
          </div>

          <div className="flex border-b border-gray-200">
            <button
              className={`px-4 py-2 text-sm font-medium ${
                viewMode === "side-by-side"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-600 hover:text-gray-800"
              }`}
              onClick={() => setViewMode("side-by-side")}
            >
              Side by Side
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium ${
                viewMode === "original"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-600 hover:text-gray-800"
              }`}
              onClick={() => setViewMode("original")}
            >
              Original
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium ${
                viewMode === "improved"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-600 hover:text-gray-800"
              }`}
              onClick={() => setViewMode("improved")}
            >
              Improved
            </button>
          </div>
        </div>

        <div className="p-6">
          {viewMode === "side-by-side" ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-3">
                  Original Document
                </h2>
                <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
                  {doc?.originalContent}
                </div>
              </div>

              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-3">
                  Improved Document
                </h2>
                <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
                  {doc?.improvedContent}
                </div>
              </div>
            </div>
          ) : viewMode === "original" ? (
            <div>
              <h2 className="text-lg font-semibold text-gray-700 mb-3">
                Original Document
              </h2>
              <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
                {doc?.originalContent}
              </div>
            </div>
          ) : (
            <div>
              <h2 className="text-lg font-semibold text-gray-700 mb-3">
                Improved Document
              </h2>
              <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
                {doc?.improvedContent}
              </div>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600">
              {doc?.suggestions?.length || 0} suggestions available
            </p>
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
            >
              Export Document
            </button>
          </div>
        </div>
      </div>

      {/* Suggestions sidebar */}
      <div className="w-full lg:w-1/4">
        {doc && (
          <SuggestionsList
            suggestions={doc.suggestions || []}
            onSelectSuggestion={handleSuggestionSelect}
            onAcceptSuggestion={handleSuggestionAccept}
            onRejectSuggestion={handleSuggestionReject}
            selectedSuggestion={selectedSuggestion}
          />
        )}
      </div>
    </div>
  );
}