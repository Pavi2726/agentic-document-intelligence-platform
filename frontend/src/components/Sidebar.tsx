import { Link, useLocation } from 'react-router-dom';
import { Home, FileText, MessageSquare, Network, BarChart3, FolderOpen } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const links = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/knowledge-graph', icon: Network, label: 'Knowledge Graph' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/conversations', icon: FolderOpen, label: 'Conversations' },
  ];

  return (
    <div className="bg-gray-900 text-white w-64 flex-shrink-0">
      <div className="p-4">
        <h1 className="text-xl font-bold">Doc Intelligence</h1>
      </div>
      <nav className="mt-8">
        {links.map(({ path, icon: Icon, label }) => (
          <Link
            key={path}
            to={path}
            className={`flex items-center px-6 py-3 hover:bg-gray-800 transition ${
              location.pathname === path ? 'bg-gray-800 border-l-4 border-blue-500' : ''
            }`}
          >
            <Icon className="w-5 h-5 mr-3" />
            {label}
          </Link>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
