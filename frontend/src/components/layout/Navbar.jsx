import { LogOut, User, Shield } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const { user, logout, isAdmin } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Shield className="h-8 w-8 text-blue-600" />
                        <span className="ml-2 text-xl font-semibold text-gray-900">Smart Proctoring</span>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="flex items-center text-sm text-gray-700">
                            <User className="h-5 w-5 mr-2" />
                            <span>{user?.full_name}</span>
                            {isAdmin && (
                                <span className="ml-2 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                    Admin
                                </span>
                            )}
                        </div>

                        <button
                            onClick={handleLogout}
                            className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                        >
                            <LogOut className="h-4 w-4 mr-2" />
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
