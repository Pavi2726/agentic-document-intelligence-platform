import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Activity, Clock, Database, TrendingUp } from 'lucide-react';
import { getAnalyticsMetrics } from '../services/api';
import { AnalyticsMetrics } from '../types';

const Analytics = () => {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      const data = await getAnalyticsMetrics();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl">Loading analytics...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl text-red-600">Failed to load analytics</div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Documents</p>
              <p className="text-3xl font-bold mt-2">{metrics.total_documents}</p>
            </div>
            <Database className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Chunks</p>
              <p className="text-3xl font-bold mt-2">{metrics.total_chunks}</p>
            </div>
            <Activity className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Queries</p>
              <p className="text-3xl font-bold mt-2">{metrics.total_queries}</p>
            </div>
            <TrendingUp className="w-12 h-12 text-orange-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Avg Latency</p>
              <p className="text-3xl font-bold mt-2">
                {Math.round(metrics.latency.reduce((sum, l) => sum + l.avg_ms, 0) / metrics.latency.length)}ms
              </p>
            </div>
            <Clock className="w-12 h-12 text-red-500" />
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* API Usage Over Time */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">API Usage Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics.api_usage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Latency by Endpoint */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Average Latency by Endpoint</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.latency}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="endpoint" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_ms" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Query</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {metrics.recent_activity.map((activity, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{activity.query}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {activity.agent}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* System Health */}
      <div className="mt-6 bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span>Vector Store: Online</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span>Knowledge Graph: Online</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span>Database: Online</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
