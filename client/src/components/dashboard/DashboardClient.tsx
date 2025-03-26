"use client";

import { useState, useEffect } from "react";
import DocumentList from "@/components/dashboard/DocumentList";
import DocumentUpload from "@/components/document/DocumentUpload";
import AuthGuard from "@/components/auth/AuthGuard";

interface Activity {
  type: "upload" | "improvement" | "other";
  description: string;
  timestamp: string;
}

interface DashboardClientProps {
  authToken: string;
}

const DashboardClient = ({ authToken }: DashboardClientProps) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showUpload, setShowUpload] = useState(false);

  const [stats, setStats] = useState<{
    totalDocuments: number;
    improvementsApplied: number;
    recentActivity: Activity[];
  }>({
    totalDocuments: 0,
    improvementsApplied: 0,
    recentActivity: [],
  });

  const fetchDocuments = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/documents", {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }

      const data = await response.json();
      setDocuments(data.documents);
      setStats(data.stats);
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError("Failed to load documents. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <AuthGuard>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              Document Dashboard
            </h1>
            <p className="text-gray-600">Manage and improve your documents</p>
          </div>

          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            onClick={() => setShowUpload(!showUpload)}
          >
            {showUpload ? "Hide Upload" : "Upload New Document"}
          </button>
        </div>

        {showUpload && (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <DocumentUpload />
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              Total Documents
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {stats.totalDocuments}
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              Improvements Applied
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {stats.improvementsApplied}
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              Success Rate
            </h3>
            <p className="text-3xl font-bold text-purple-600">
              {stats.totalDocuments > 0
                ? `${Math.round(
                    (stats.improvementsApplied / stats.totalDocuments) * 100
                  )}%`
                : "0%"}
            </p>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">
              Recent Activity
            </h2>
          </div>

          <div className="p-6">
            {stats.recentActivity && stats.recentActivity.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {stats.recentActivity.map((activity, index) => (
                  <li key={index} className="py-3">
                    <div className="flex items-start">
                      <div
                        className={`mt-1 mr-3 w-2 h-2 rounded-full ${
                          activity.type === "upload"
                            ? "bg-blue-500"
                            : activity.type === "improvement"
                            ? "bg-green-500"
                            : "bg-purple-500"
                        }`}
                      ></div>
                      <div>
                        <p className="text-sm text-gray-800">
                          {activity.description}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(activity.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No recent activity
              </p>
            )}
          </div>
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">
              Your Documents
            </h2>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="p-6 text-center text-red-500">{error}</div>
          ) : (
            <DocumentList documents={documents} />
          )}
        </div>
      </div>
    </AuthGuard>
  );
};

export default DashboardClient;