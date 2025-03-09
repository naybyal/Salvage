import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { X } from "lucide-react";

interface AnalyticsProps {
  cCode: string;
  rustCode: string;
}

const Analytics: React.FC<AnalyticsProps> = ({ cCode, rustCode }) => {
  const [isOpen, setIsOpen] = React.useState(true);

  const getAnalytics = () => {
    const cLines = cCode.split("\n").length;
    const rustLines = rustCode.split("\n").length;
    const cChars = cCode.length;
    const rustChars = rustCode.length;

    return [
      `C code: ${cLines} lines, ${cChars} characters`,
      `Rust code: ${rustLines} lines, ${rustChars} characters`,
      `Line difference: ${rustLines - cLines} lines`,
      `Character difference: ${rustChars - cChars} characters`,
      `Expansion ratio: ${(rustChars / cChars).toFixed(2)}x`,
    ];
  };

  const getTranspilationExplanation = () => {
    const changes = [];
    if (rustCode.includes("Result<")) {
      changes.push("Added Result type for error handling");
    }
    if (rustCode.includes("match")) {
      changes.push("Replaced if-else statements with match expressions for pattern matching");
    }
    if (rustCode.includes("Vec<")) {
      changes.push("Replaced C arrays with Rust's Vec for dynamic arrays");
    }
    if (rustCode.includes("String")) {
      changes.push("Replaced C-style strings with Rust's String type");
    }
    if (rustCode.includes("println!")) {
      changes.push("Replaced printf with println! macro");
    }
    if (rustCode.includes("struct")) {
      changes.push("Converted C structs to Rust structs");
    }
    if (rustCode.includes("impl")) {
      changes.push("Added impl blocks for struct methods");
    }
    if (rustCode.includes("Option<")) {
      changes.push("Used Option type for nullable values");
    }

    return changes.length > 0
      ? changes
      : ["No significant changes detected. The transpilation might be basic or incomplete."];
  };

  return (
    <>
      {isOpen && (
        <Card className="fixed bottom-0 left-0 right-0 max-h-[50vh] overflow-auto bg-neutral-800 text-white">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Code Analytics</CardTitle>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-red-300"
            >
              <X className="h-4 w-4" />
            </button>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <h4 className="text-lg font-semibold mb-2">Transpilation Statistics</h4>
              <ul className="list-disc pl-5 space-y-1">
                {getAnalytics().map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-2">Transpilation Explanation</h4>
              <ul className="list-disc pl-5 space-y-1">
                {getTranspilationExplanation().map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
};

export default Analytics;