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
        <CartesianGrid stroke="rgba(107,99,87,0.18)" vertical={false} />
        <XAxis dataKey="range" tick={{ fill: '#8a8170', fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#8a8170', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          cursor={{ fill: 'rgba(201,100,66,0.06)' }}
          formatter={(value) => [`${value}%`, 'Share of simulations']}
          contentStyle={{
            borderRadius: 14,
            border: '1px solid rgba(28,22,14,0.10)',
            background: 'rgba(252,248,240,0.97)',
            color: '#1a1612',
            fontSize: 12,
            boxShadow: '0 18px 42px rgba(34,24,12,0.10)',
            padding: '8px 12px',
          }}
          labelStyle={{ color: '#5e564a', fontSize: 11, marginBottom: 4 }}
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
