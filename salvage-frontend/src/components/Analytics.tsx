import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { X, BarChart, Info, AlertCircle, Code, LineChart, Hash, AlertTriangle } from "lucide-react";

interface AnalyticsProps {
  cCode: string;
  rustCode: string;
  onClose: () => void;
}

const Analytics: React.FC<AnalyticsProps> = ({ cCode, rustCode, onClose }) => {
  const getStats = () => {
    const cLines = cCode.split("\n").length;
    const rustLines = rustCode.split("\n").length;
    const cChars = cCode.length;
    const rustChars = rustCode.length;

    return {
      lines: { c: cLines, rust: rustLines, difference: rustLines - cLines },
      chars: { c: cChars, rust: rustChars, difference: rustChars - cChars, ratio: (rustChars / cChars).toFixed(2) }
    };
  };

  const getInsights = () => {
    const insights = [];
    const rustCodeLower = rustCode.toLowerCase();

    if (rustCodeLower.includes("result<")) insights.push("Error handling with Result type");
    if (rustCodeLower.includes("unwrap()")) insights.push("Potential panic points using unwrap()");
    if (rustCodeLower.includes("match ")) insights.push("Pattern matching with match expressions");
    if (rustCodeLower.includes("vec<")) insights.push("Vector collection usage");
    if (rustCodeLower.includes("mut ")) insights.push("Mutable variables declared");
    if (rustCodeLower.includes("loop ")) insights.push("Loop constructs used");
    if (rustCodeLower.includes("fn ")) insights.push(`${(rustCodeLower.match(/fn /g) || []).length} functions defined`);
    if (rustCodeLower.includes("struct ")) insights.push("Custom structs defined");
    if (rustCodeLower.includes("impl ")) insights.push("Implementation blocks for struct methods");

    return insights.length > 0 ? insights : ["No significant patterns detected"];
  };

  const stats = getStats();
  const insights = getInsights();

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="bg-gray-800 text-white w-full max-w-2xl border border-gray-700">
        <CardHeader className="flex flex-row items-center justify-between border-b border-gray-700 p-4">
          <div className="flex items-center gap-2">
            <BarChart className="h-6 w-6 text-red-400" />
            <CardTitle className="text-xl">Code Analysis</CardTitle>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-red-400 transition-colors">
            <X className="h-6 w-6" />
          </button>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <LineChart className="h-5 w-5 text-red-400" />
              Basic Statistics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-700/20 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="h-4 w-4 text-red-400" />
                  <span className="font-medium">Lines of Code</span>
                </div>
                <div className="space-y-1 text-sm">
                  <p>C: {stats.lines.c}</p>
                  <p>Rust: {stats.lines.rust}</p>
                  <p className={stats.lines.difference > 0 ? 'text-red-300' : 'text-green-300'}>
                    Δ {stats.lines.difference} lines
                  </p>
                </div>
              </div>

              <div className="bg-gray-700/20 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Code className="h-4 w-4 text-red-400" />
                  <span className="font-medium">Characters</span>
                </div>
                <div className="space-y-1 text-sm">
                  <p>C: {stats.chars.c}</p>
                  <p>Rust: {stats.chars.rust}</p>
                  <p className={stats.chars.difference > 0 ? 'text-red-300' : 'text-green-300'}>
                    Δ {stats.chars.difference} ({stats.chars.ratio}x)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-400" />
              Code Patterns & Insights
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {insights.map((insight, index) => (
                <div key={index} className="bg-gray-700/20 p-3 rounded-lg flex items-start gap-2 text-sm">
                  <AlertTriangle className="h-4 w-4 text-yellow-400" />
                  {insight}
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;
