"use client";

import React from "react";

interface Suggestion {
  type: string;
  description: string;
  originalText: string;
  suggestedText: string;
  explanation?: string;
}

interface SuggestionItemProps {
  suggestion: Suggestion;
  isSelected: boolean;
  onSelect: () => void;
  onAccept: () => void;
  onReject: () => void;
}

const SuggestionItem: React.FC<SuggestionItemProps> = ({
  suggestion,
  isSelected,
  onSelect,
  onAccept,
  onReject,
}) => {
  // Get background color based on suggestion type
  const getBgColor = (type: string) => {
    switch (type) {
      case "grammar":
        return "bg-red-50 border-red-200";
      case "style":
        return "bg-purple-50 border-purple-200";
      case "clarity":
        return "bg-yellow-50 border-yellow-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  // Get text color based on suggestion type
  const getTextColor = (type: string) => {
    switch (type) {
      case "grammar":
        return "text-red-700";
      case "style":
        return "text-purple-700";
      case "clarity":
        return "text-yellow-700";
      default:
        return "text-gray-700";
    }
  };

  // Get badge color based on suggestion type
  const getBadgeColor = (type: string) => {
    switch (type) {
      case "grammar":
        return "bg-red-100 text-red-800";
      case "style":
        return "bg-purple-100 text-purple-800";
      case "clarity":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  return (
    <li
      className={`p-4 cursor-pointer transition-colors ${
        isSelected
          ? `${getBgColor(suggestion.type)} border-l-4 border-l-blue-500`
          : "hover:bg-gray-50"
      }`}
      onClick={onSelect}
    >
      <div className="space-y-2">
        <div className="flex justify-between items-start">
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor(
              suggestion.type
            )}`}
          >
            {suggestion.type.charAt(0).toUpperCase() + suggestion.type.slice(1)}
          </span>

          {isSelected && (
            <div className="flex space-x-1">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAccept();
                }}
                className="text-xs bg-green-600 text-white px-2 py-1 rounded hover:bg-green-700"
              >
                Accept
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onReject();
                }}
                className="text-xs bg-gray-600 text-white px-2 py-1 rounded hover:bg-gray-700"
              >
                Reject
              </button>
            </div>
          )}
        </div>

        <p className="text-sm font-medium">{suggestion.description}</p>

        {isSelected && (
          <div className="mt-3 space-y-2">
            <div className="text-xs">
              <div className="text-gray-500 font-medium mb-1">Original:</div>
              <div className="p-2 bg-white border border-gray-200 rounded text-gray-700">
                {suggestion.originalText}
              </div>
            </div>

            <div className="text-xs">
              <div
                className={`${getTextColor(suggestion.type)} font-medium mb-1`}
              >
                Suggestion:
              </div>
              <div
                className={`p-2 ${getBgColor(
                  suggestion.type
                )} border rounded ${getTextColor(suggestion.type)}`}
              >
                {suggestion.suggestedText}
              </div>
            </div>

            {suggestion.explanation && (
              <div className="text-xs mt-2">
                <div className="text-gray-500 font-medium mb-1">
                  Explanation:
                </div>
                <p className="text-gray-600">{suggestion.explanation}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </li>
  );
};

export default SuggestionItem;