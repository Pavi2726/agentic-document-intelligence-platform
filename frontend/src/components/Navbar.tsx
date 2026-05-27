import { LogOut, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../services/api';

const Navbar = () => {
  const navigate = useNavigate();
  const username = localStorage.getItem('username') || 'User';

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      navigate('/login');
    }
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        <h2 className="text-2xl font-semibold text-gray-800">Agentic Document Intelligence</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
            <User className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">{username}</span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
