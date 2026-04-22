import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

type HistogramBar = {
  range: string;
  value: number;
  fill: string;
};

export default function EstimateRangeBarChart({ data }: { data: HistogramBar[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} barSize={54}>
        <CartesianGrid stroke="rgba(100,116,139,0.18)" vertical={false} />
        <XAxis dataKey="range" tick={{ fill: '#66748b', fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#66748b', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          formatter={(value) => [`${value}%`, 'Share of simulations']}
          contentStyle={{
            borderRadius: 18,
            border: '1px solid rgba(31,47,72,0.10)',
            background: 'rgba(255,251,245,0.96)',
            color: '#142033',
            fontSize: 12,
            boxShadow: '0 18px 48px rgba(23,34,51,0.12)',
          }}
        />
        <Bar dataKey="value" radius={[6, 6, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.range} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
