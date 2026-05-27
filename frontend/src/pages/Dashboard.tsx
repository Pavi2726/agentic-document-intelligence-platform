import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getDocuments } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ documents: 0, chunks: 0, queries: 0 });
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const docs = await getDocuments();
      
      setStats({
        documents: docs.length,
        chunks: docs.reduce((sum, doc) => sum + doc.chunk_count, 0),
        queries: 0,
      });

      setChartData(
        docs.map(doc => ({
          name: doc.filename.substring(0, 15),
          chunks: doc.chunk_count,
        }))
      );
    };
    fetchData();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total Documents</h3>
          <p className="text-3xl font-bold mt-2">{stats.documents}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total Chunks</h3>
          <p className="text-3xl font-bold mt-2">{stats.chunks}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Queries Processed</h3>
          <p className="text-3xl font-bold mt-2">{stats.queries}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Document Chunks Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="chunks" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Dashboard;
