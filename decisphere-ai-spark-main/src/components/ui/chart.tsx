import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  TooltipProps,
} from "recharts";

// Define your chart data type
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

// Extend TooltipProps to include payload and label safely
interface CustomTooltipProps {
  active?: boolean;
  payload?: { payload: ChartDataPoint }[];
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-white border p-2 shadow rounded">
      <p className="font-semibold">{label}</p>
      {payload.map((entry, index) => {
        const data = entry.payload;
        return (
          <p key={index} style={{ color: data.color || "#000" }}>
            {data.name}: {data.value}
          </p>
        );
      })}
    </div>
  );
};

interface ChartProps {
  data: ChartDataPoint[];
  dataKey?: keyof ChartDataPoint;
  lineColor?: string;
}

const Chart: React.FC<ChartProps> = ({ data, dataKey = "value", lineColor = "#8884d8" }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey={dataKey as string}
          stroke={lineColor}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default Chart;