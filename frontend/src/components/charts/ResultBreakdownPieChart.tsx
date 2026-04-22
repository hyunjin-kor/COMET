import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

type PieSlice = {
  name: string;
  value: number;
};

export default function ResultBreakdownPieChart({
  data,
  colors,
}: {
  data: PieSlice[];
  colors: string[];
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie data={data} innerRadius={64} outerRadius={96} dataKey="value" paddingAngle={3} stroke="transparent">
          {data.map((entry, index) => (
            <Cell key={entry.name} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Share']}
          contentStyle={{
            borderRadius: 18,
            border: '1px solid rgba(31,47,72,0.10)',
            background: 'rgba(255,251,245,0.96)',
            color: '#142033',
            fontSize: 12,
            boxShadow: '0 18px 48px rgba(23,34,51,0.12)',
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
