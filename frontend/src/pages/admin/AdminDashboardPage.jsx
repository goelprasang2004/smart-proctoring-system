import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../components/layouts/AdminLayout';
import examService from '../../services/examService';
import proctoringService from '../../services/proctoringService';
import { ClipboardList, Users, AlertTriangle, TrendingUp, Plus } from 'lucide-react';

const AdminDashboardPage = () => {
    const [stats, setStats] = useState({
        totalExams: 0,
        activeExams: 0,
        suspiciousAttempts: 0,
        totalAttempts: 0
    });
    const [recentExams, setRecentExams] = useState([]);
    const [suspiciousAttempts, setSuspiciousAttempts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            // Load exams
            const examsData = await examService.getAllExams();
            const exams = examsData.exams || [];

            // Load suspicious attempts
            const suspicious = await proctoringService.getSuspiciousAttempts(0.1, 1);

            setStats({
                totalExams: exams.length,
                activeExams: exams.filter(e => e.status === 'active').length,
                suspiciousAttempts: suspicious.length,
                totalAttempts: 0 // Would need a separate endpoint
            });

            setRecentExams(exams.slice(0, 5));
            setSuspiciousAttempts(suspicious.slice(0, 5));
        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ icon: Icon, label, value, color, link }) => (
        <Link to={link} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-600">{label}</p>
                    <p className="text-3xl font-bold mt-2 text-gray-900">{value}</p>
                </div>
                <div className={`p-3 rounded-full ${color}`}>
                    <Icon className="h-6 w-6 text-white" />
                </div>
            </div>
        </Link>
    );

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        );
    }

    return (
        <AdminLayout>
            <div className="space-y-6">
                {/* Page Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                        <p className="text-gray-600 mt-1">Overview of system activity and statistics</p>
                    </div>
                    <Link
                        to="/admin/exams/new"
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Plus className="h-5 w-5" />
                        <span>Create Exam</span>
                    </Link>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <StatCard
                        icon={ClipboardList}
                        label="Total Exams"
                        value={stats.totalExams}
                        color="bg-blue-600"
                        link="/admin/exams"
                    />
                    <StatCard
                        icon={TrendingUp}
                        label="Active Exams"
                        value={stats.activeExams}
                        color="bg-green-600"
                        link="/admin/exams?status=active"
                    />
                    <StatCard
                        icon={AlertTriangle}
                        label="Suspicious"
                        value={stats.suspiciousAttempts}
                        color="bg-red-600"
                        link="/admin/suspicious"
                    />
                    <StatCard
                        icon={Users}
                        label="Total Attempts"
                        value={stats.totalAttempts}
                        color="bg-purple-600"
                        link="/admin/exams"
                    />
                </div>

                {/* Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Recent Exams */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900">Recent Exams</h2>
                        </div>
                        <div className="p-6">
                            {recentExams.length > 0 ? (
                                <div className="space-y-4">
                                    {recentExams.map((exam) => (
                                        <Link
                                            key={exam.id}
                                            to={`/admin/exams/${exam.id}/edit`}
                                            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                                        >
                                            <p className="font-medium text-gray-900">{exam.title}</p>
                                            <div className="flex items-center justify-between mt-2">
                                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${exam.status === 'active' ? 'bg-green-100 text-green-800' :
                                                    exam.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                                                        'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {exam.status}
                                                </span>
                                                <span className="text-sm text-gray-600">
                                                    {exam.duration_minutes} min
                                                </span>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500 text-center py-8">No exams yet</p>
                            )}
                        </div>
                    </div>

                    {/* Suspicious Attempts */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900">Recent Suspicious Activity</h2>
                        </div>
                        <div className="p-6">
                            {suspiciousAttempts.length > 0 ? (
                                <div className="space-y-4">
                                    {suspiciousAttempts.map((attempt) => (
                                        <Link
                                            key={attempt.attempt_id}
                                            to={`/admin/proctoring/${attempt.attempt_id}`}
                                            className="block p-4 border border-red-200 bg-red-50 rounded-lg hover:border-red-300 transition-colors"
                                        >
                                            <p className="font-medium text-gray-900">
                                                Student: {attempt.student_name || 'Unknown'}
                                            </p>
                                            <div className="flex items-center justify-between mt-2">
                                                <span className="text-sm text-gray-600">
                                                    {attempt.suspicious_event_count} events
                                                </span>
                                                <span className="text-sm font-medium text-red-600">
                                                    Risk: {(attempt.avg_confidence * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500 text-center py-8">No suspicious activity</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
};

export default AdminDashboardPage;
