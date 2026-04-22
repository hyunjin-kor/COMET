import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

type HistoryPoint = {
  date: string;
  price: number;
  open: number;
  high: number;
  low: number;
};

type Period = '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y';

export default function MetalTrendChart({
  data,
  period,
  selectedDisplayUnit,
  selectedColor,
}: {
  data: HistoryPoint[];
  period: Period;
  selectedDisplayUnit: string;
  selectedColor: string;
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={selectedColor} stopOpacity={0.3} />
            <stop offset="95%" stopColor={selectedColor} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(value) =>
            new Date(value).toLocaleDateString(
              'en-US',
              period === '1mo' ? { month: 'short', day: 'numeric' } : { year: '2-digit', month: 'short' },
            )
          }
        />
        <YAxis
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(value) => `$${Number(value).toLocaleString('en-US')}`}
          width={72}
        />
        <Tooltip
          formatter={(value) => [`$${Number(value).toLocaleString('en-US')}`, selectedDisplayUnit]}
          labelFormatter={(value) =>
            new Date(value).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })
          }
          contentStyle={{
            borderRadius: 18,
            border: '1px solid rgba(255,255,255,0.10)',
            background: '#0b1522',
            color: '#e2e8f0',
            fontSize: 12,
          }}
        />
        {data.length > 0 ? <ReferenceLine y={data[0].price} stroke="rgba(255,255,255,0.12)" strokeDasharray="4 4" /> : null}
        <Area
          type="monotone"
          dataKey="price"
          stroke={selectedColor}
          strokeWidth={2.2}
          fill="url(#priceFill)"
          dot={false}
          activeDot={{ r: 4 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
