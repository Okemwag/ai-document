"use client";

import { useState } from "react";
import DocumentCard from "./DocumentCard";

interface Document {
  id: string;
  title: string;
  fileType: string;
  uploadedAt: string;
}

interface DocumentListProps {
  documents: Document[];
}

const DocumentList = ({ documents }: DocumentListProps) => {
  const [sortBy, setSortBy] = useState("date");
  const [filterType, setFilterType] = useState("all"); // 'all', 'docx', 'pdf', 'txt'
  const [searchQuery, setSearchQuery] = useState("");

  // Filter and sort documents
  const filteredAndSortedDocuments = documents
    .filter((doc) => {
      // Filter by type
      if (filterType !== "all" && doc.fileType !== filterType) {
        return false;
      }

      // Filter by search query
      if (
        searchQuery.trim() !== "" &&
        !doc.title.toLowerCase().includes(searchQuery.toLowerCase())
      ) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      // Sort by selected criteria
      switch (sortBy) {
        case "name":
          return a.title.localeCompare(b.title);
        case "type":
          return a.fileType.localeCompare(b.fileType);
        case "date":
        default:
          return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime();
      }
    });
  return (
    <div>
    {/* Search and Filters */}
    <div className="p-4 border-b border-gray-200 bg-gray-50">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-grow">
          <div className="relative">
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2">
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="docx">Word (.docx)</option>
            <option value="pdf">PDF (.pdf)</option>
            <option value="txt">Text (.txt)</option>
          </select>
          
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="date">Latest First</option>
            <option value="name">Name (A-Z)</option>
            <option value="type">File Type</option>
          </select>
        </div>
      </div>
    </div>
    
    {/* Document List */}
    <div className="p-4">
      {filteredAndSortedDocuments.length === 0 ? (
        <div className="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-700">No documents found</h3>
          <p className="mt-1 text-gray-500">
            {searchQuery || filterType !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Upload your first document to get started'}
          </p>
          {!searchQuery && filterType === 'all' && (
            <button 
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            >
              Upload Document
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAndSortedDocuments.map((document) => (
            <DocumentCard key={document.id} document={document} />
          ))}
        </div>
      )}
    </div>
  </div>
  );
};

export default DocumentList;