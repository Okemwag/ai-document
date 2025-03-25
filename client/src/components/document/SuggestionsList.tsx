"use client";
import React, { useState } from "react";
import SuggestionItem from "./SuggestionItem";

interface Suggestion {
  id: string;
  content: string;
  type: string;
  description: string;
  originalText: string;
  suggestedText: string;
}

interface SuggestionsListProps {
  suggestions: Suggestion[];
  onSelectSuggestion: (suggestion: Suggestion) => void;
  onAcceptSuggestion: (id: string) => void;
  onRejectSuggestion: (id: string) => void;
  selectedSuggestion?: Suggestion | null;
}

const SuggestionsList = ({
  suggestions,
  onSelectSuggestion,
  onAcceptSuggestion,
  onRejectSuggestion,
  selectedSuggestion,
}: SuggestionsListProps) => {
  const [filter, setFilter] = useState("all");

  // Filter suggestions based on the selected filter
  const filteredSuggestions = suggestions.filter((suggestion) => {
    if (filter === "all") return true;
    return suggestion.type === filter;
  });

  // Group suggestions by type for displaying counts
  const suggestionCounts = suggestions.reduce(
    (counts: { [key: string]: number }, suggestion) => {
      counts[suggestion.type] = (counts[suggestion.type] || 0) + 1;
      return counts;
    },
    {}
  );
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden h-full flex flex-col">
      <div className="px-4 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Suggestions</h2>
      </div>

      {/* Filters */}
      <div className="px-4 py-2 border-b border-gray-200 flex space-x-2 overflow-x-auto">
        <button
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            filter === "all"
              ? "bg-blue-100 text-blue-800"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
          onClick={() => setFilter("all")}
        >
          All ({suggestions.length})
        </button>
        <button
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            filter === "grammar"
              ? "bg-blue-100 text-blue-800"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
          onClick={() => setFilter("grammar")}
        >
          Grammar ({suggestionCounts.grammar || 0})
        </button>
        <button
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            filter === "style"
              ? "bg-blue-100 text-blue-800"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
          onClick={() => setFilter("style")}
        >
          Style ({suggestionCounts.style || 0})
        </button>
        <button
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            filter === "clarity"
              ? "bg-blue-100 text-blue-800"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
          onClick={() => setFilter("clarity")}
        >
          Clarity ({suggestionCounts.clarity || 0})
        </button>
      </div>

      {/* Suggestions List */}
      <div className="flex-grow overflow-y-auto">
        {filteredSuggestions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No suggestions available.
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {filteredSuggestions.map((suggestion) => (
              <SuggestionItem
                key={suggestion.id}
                suggestion={suggestion}
                isSelected={selectedSuggestion?.id === suggestion.id}
                onSelect={() => onSelectSuggestion(suggestion)}
                onAccept={() => onAcceptSuggestion(suggestion.id)}
                onReject={() => onRejectSuggestion(suggestion.id)}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SuggestionsList;