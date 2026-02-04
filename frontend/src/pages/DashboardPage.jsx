import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StudentLayout from '../components/layouts/StudentLayout';
import examService from '../services/examService';
import { BookOpen, Clock, Calendar, PlayCircle, TrendingUp } from 'lucide-react';

const DashboardPage = () => {
    const [upcomingExams, setUpcomingExams] = useState([]);
    const [recentAttempts, setRecentAttempts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const data = await examService.getAvailableExams();
            console.log('API Response:', data); // Debug log

            // Backend returns {exams: [...], count: N}, so extract the exams array
            const exams = data?.exams || data || [];
            console.log('Extracted exams:', exams); // Debug log

            // Sort by start time
            const sorted = exams.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
            setUpcomingExams(sorted.slice(0, 3));
        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const getExamStatus = (exam) => {
        const now = new Date();
        const start = new Date(exam.start_time);
        const end = new Date(exam.end_time);

        if (now < start) {
            return { label: 'Upcoming', color: 'bg-blue-100 text-blue-800', canStart: false };
        } else if (now >= start && now <= end) {
            return { label: 'Active', color: 'bg-green-100 text-green-800', canStart: true };
        } else {
            return { label: 'Ended', color: 'bg-gray-100 text-gray-800', canStart: false };
        }
    };

    if (loading) {
        return (
            <StudentLayout>
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </StudentLayout>
        );
    }

    return (
        <StudentLayout>
            <div className="space-y-6">
                {/* Welcome Section */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Welcome to Your Dashboard</h1>
                    <p className="text-gray-600 mt-1">Track your exams and progress</p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Upcoming Exams</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">{upcomingExams.length}</p>
                            </div>
                            <div className="p-3 rounded-full bg-blue-100">
                                <BookOpen className="h-6 w-6 text-blue-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Completed</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">{recentAttempts.length}</p>
                            </div>
                            <div className="p-3 rounded-full bg-green-100">
                                <PlayCircle className="h-6 w-6 text-green-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Average Score</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">--</p>
                            </div>
                            <div className="p-3 rounded-full bg-purple-100">
                                <TrendingUp className="h-6 w-6 text-purple-600" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Upcoming Exams */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-900">Upcoming Exams</h2>
                        <Link to="/exams" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                            View all →
                        </Link>
                    </div>
                    <div className="p-6">
                        {upcomingExams.length > 0 ? (
                            <div className="space-y-4">
                                {upcomingExams.map((exam) => {
                                    const status = getExamStatus(exam);
                                    return (
                                        <div
                                            key={exam.id}
                                            className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center space-x-3">
                                                        <h3 className="font-semibold text-gray-900">{exam.title}</h3>
                                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.color}`}>
                                                            {status.label}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center space-x-6 mt-2 text-sm text-gray-600">
                                                        <div className="flex items-center space-x-1">
                                                            <Clock className="h-4 w-4" />
                                                            <span>{exam.duration_minutes} min</span>
                                                        </div>
                                                        <div className="flex items-center space-x-1">
                                                            <Calendar className="h-4 w-4" />
                                                            <span>{new Date(exam.start_time).toLocaleString()}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                {status.canStart && (
                                                    <Link
                                                        to={`/exam/${exam.id}`}
                                                        className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                                    >
                                                        Start
                                                    </Link>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-center py-8">No upcoming exams</p>
                        )}
                    </div>
                </div>
            </div>
        </StudentLayout>
    );
};

// Exam Card Component
const ExamCard = ({ exam, onStart, getStatusBadge }) => {
    const isActive = exam.status === EXAM_STATUS.ACTIVE;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            {/* Title and Status */}
            <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">{exam.title}</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(exam.status)}`}>
                    {exam.status}
                </span>
            </div>

            {/* Description */}
            {exam.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{exam.description}</p>
            )}

            {/* Meta Info */}
            <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    <span>{exam.duration_minutes} minutes</span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                    <BookOpen className="h-4 w-4 mr-2" />
                    <span>Starts: {new Date(exam.start_time).toLocaleString()}</span>
                </div>
            </div>

            {/* Action Button */}
            <button
                onClick={() => onStart(exam.id)}
                disabled={!isActive}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${isActive
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    }`}
            >
                {isActive ? 'Start Exam' : 'Not Available'}
            </button>
        </div>
    );
};

export default DashboardPage;
