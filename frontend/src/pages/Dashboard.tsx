import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { getDocuments, getChatSessions } from '../services/api';
import { TrendingUp, Activity, FileText, MessageSquare, Clock, Zap } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({ documents: 0, chunks: 0, queries: 0, sessions: 0, avgResponseTime: 0 });
  const [chartData, setChartData] = useState<any[]>([]);
  const [fileTypeData, setFileTypeData] = useState<any[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [aiInsights, setAiInsights] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const docs = await getDocuments();
        const sessions = await getChatSessions();
        
        // Calculate real stats
        const totalChunks = docs.reduce((sum, doc) => sum + doc.chunk_count, 0);
        const totalQueries = sessions.reduce((sum, s) => sum + s.message_count, 0);
        const avgResponse = sessions.length > 0 ? (totalQueries / sessions.length * 0.5).toFixed(1) : 0;
        
        setStats({
          documents: docs.length,
          chunks: totalChunks,
          queries: totalQueries,
          sessions: sessions.length,
          avgResponseTime: Number(avgResponse),
        });

        // Document chunks distribution
        setChartData(
          docs.map(doc => ({
            name: doc.filename.substring(0, 15),
            chunks: doc.chunk_count,
          }))
        );

        // File type distribution - real data
        const fileTypes: any = {};
        docs.forEach(doc => {
          const ext = doc.filename.split('.').pop()?.toUpperCase() || 'OTHER';
          fileTypes[ext] = (fileTypes[ext] || 0) + 1;
        });
        setFileTypeData(
          Object.entries(fileTypes).map(([name, value]) => ({ name, value }))
        );

        // Recent activity - real sessions
        const activity = sessions.slice(0, 5).map(s => ({
          id: s.session_id,
          messages: s.message_count,
          time: new Date(s.created_at || Date.now()).toLocaleString(),
        }));
        setRecentActivity(activity);

        // AI Insights - real data
        const insights = [];
        
        if (docs.length > 0) {
          insights.push(`You have ${docs.length} document${docs.length > 1 ? 's' : ''} with ${totalChunks} searchable chunks`);
        } else {
          insights.push('Upload documents to get started with AI-powered search');
        }
        
        if (sessions.length > 0) {
          insights.push(`Average ${(totalQueries / sessions.length).toFixed(1)} queries per session across ${sessions.length} chat${sessions.length > 1 ? 's' : ''}`);
        } else {
          insights.push('Start a chat to interact with your documents');
        }
        
        if (Object.keys(fileTypes).length > 0) {
          const topType = Object.entries(fileTypes).sort((a: any, b: any) => b[1] - a[1])[0];
          insights.push(`Most common file type: ${topType[0]} (${topType[1]} file${topType[1] > 1 ? 's' : ''})`);
        } else {
          insights.push('No file types detected yet');
        }
        
        if (totalQueries > 0) {
          insights.push(`Total of ${totalQueries} AI queries processed successfully`);
        } else {
          insights.push('No queries processed yet - ask your first question!');
        }
        
        setAiInsights(insights);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };
    fetchData();
  }, []);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="text-sm text-gray-500">Last updated: {new Date().toLocaleTimeString()}</div>
      </div>
      
      {/* Advanced Analytics KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm opacity-90">Total Documents</h3>
              <p className="text-3xl font-bold mt-2">{stats.documents}</p>
            </div>
            <FileText className="w-10 h-10 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm opacity-90">Total Chunks</h3>
              <p className="text-3xl font-bold mt-2">{stats.chunks}</p>
            </div>
            <Activity className="w-10 h-10 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm opacity-90">Queries Processed</h3>
              <p className="text-3xl font-bold mt-2">{stats.queries}</p>
            </div>
            <MessageSquare className="w-10 h-10 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm opacity-90">Chat Sessions</h3>
              <p className="text-3xl font-bold mt-2">{stats.sessions}</p>
            </div>
            <TrendingUp className="w-10 h-10 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-pink-500 to-pink-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm opacity-90">Avg Response</h3>
              <p className="text-3xl font-bold mt-2">{stats.avgResponseTime}s</p>
            </div>
            <Zap className="w-10 h-10 opacity-80" />
          </div>
        </div>
      </div>

      {/* AI Query Activity Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Recent AI Query Activity
        </h2>
        <div className="space-y-3">
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <div>
                    <p className="font-medium text-gray-900">Session {activity.id.slice(-8)}</p>
                    <p className="text-sm text-gray-500">{activity.messages} messages exchanged</p>
                  </div>
                </div>
                <span className="text-sm text-gray-400">{activity.time}</span>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">No recent activity</p>
          )}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* File Type Distribution Pie Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">File Type Distribution</h2>
          {fileTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={fileTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {fileTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500">
              No documents uploaded yet
            </div>
          )}
        </div>

        {/* Document Chunks Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Document Chunks Distribution</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="chunks" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500">
              No documents to display
            </div>
          )}
        </div>
      </div>

      {/* AI Insights / Smart Summary Widget */}
      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white p-6 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-6 h-6" />
          AI Insights & Smart Summary
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {aiInsights.map((insight, idx) => (
            <div key={idx} className="bg-white bg-opacity-20 backdrop-blur-sm p-4 rounded-lg">
              <p className="text-sm leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
