import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StudentLayout from '../components/layouts/StudentLayout';
import examService from '../services/examService';
import { BookOpen, Clock, Calendar, PlayCircle } from 'lucide-react';

const ExamsListPage = () => {
    const [exams, setExams] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadExams();
    }, []);

    const loadExams = async () => {
        try {
            setLoading(true);
            const data = await examService.getAvailableExams();
            setExams(data || []);
        } catch (error) {
            console.error('Error loading exams:', error);
        } finally {
            setLoading(false);
        }
    };

    const getExamStatus = (exam) => {
        // First check attempt status from backend
        if (exam.attempt_status === 'completed' || exam.attempt_status === 'cancelled') {
            return { label: 'Completed', color: 'bg-green-100 text-green-800', canStart: false, isCompleted: true };
        }
        if (exam.attempt_status === 'terminated') {
            return { label: 'Terminated', color: 'bg-red-100 text-red-800', canStart: false, isCompleted: true };
        }
        if (exam.attempt_status === 'in_progress') {
            return { label: 'In Progress', color: 'bg-yellow-100 text-yellow-800', canStart: false, isInProgress: true, attemptId: exam.attempt_id };
        }

        // Then check time-based status
        const now = new Date();
        const start = new Date(exam.start_time);
        const end = new Date(exam.end_time);

        if (now < start) {
            return { label: 'Upcoming', color: 'bg-blue-100 text-blue-800', canStart: false };
        } else if (now >= start && now <= end) {
            return { label: 'Active', color: 'bg-green-100 text-green-800', canStart: exam.can_start !== false };
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
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Available Exams</h1>
                    <p className="text-gray-600 mt-1">View and start scheduled exams</p>
                </div>

                {/* Exams Grid */}
                {exams.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {exams.map((exam) => {
                            const status = getExamStatus(exam);
                            return (
                                <div
                                    key={exam.id}
                                    className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
                                >
                                    <div className="p-6">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div className="p-2 bg-blue-100 rounded-lg">
                                                    <BookOpen className="h-6 w-6 text-blue-600" />
                                                </div>
                                                <span className={`px-3 py-1 text-xs font-medium rounded-full ${status.color}`}>
                                                    {status.label}
                                                </span>
                                            </div>
                                        </div>

                                        <h3 className="text-lg font-semibold text-gray-900 mt-4">
                                            {exam.title}
                                        </h3>

                                        {exam.description && (
                                            <p className="text-gray-600 text-sm mt-2 line-clamp-2">
                                                {exam.description}
                                            </p>
                                        )}

                                        <div className="space-y-2 mt-4">
                                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                                                <Clock className="h-4 w-4" />
                                                <span>Duration: {exam.duration_minutes} minutes</span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                                                <Calendar className="h-4 w-4" />
                                                <span>Start: {new Date(exam.start_time).toLocaleString()}</span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                                                <Calendar className="h-4 w-4" />
                                                <span>End: {new Date(exam.end_time).toLocaleString()}</span>
                                            </div>
                                        </div>

                                        <div className="mt-6">
                                            {status.isCompleted ? (
                                                <button
                                                    disabled
                                                    className="w-full px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed"
                                                >
                                                    {status.label === 'Completed' ? '✓ Exam Completed' : 'Exam Terminated'}
                                                </button>
                                            ) : status.isInProgress ? (
                                                <Link
                                                    to={`/exam/${exam.id}?attemptId=${status.attemptId}`}
                                                    className="flex items-center justify-center space-x-2 w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                                                >
                                                    <PlayCircle className="h-5 w-5" />
                                                    <span>Resume Exam</span>
                                                </Link>
                                            ) : status.canStart ? (
                                                <Link
                                                    to={`/exam/${exam.id}`}
                                                    className="flex items-center justify-center space-x-2 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                                >
                                                    <PlayCircle className="h-5 w-5" />
                                                    <span>Start Exam</span>
                                                </Link>
                                            ) : (
                                                <button
                                                    disabled
                                                    className="w-full px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed"
                                                >
                                                    {status.label === 'Upcoming' ? 'Not Started Yet' : 'Exam Ended'}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="bg-white p-12 rounded-lg shadow-sm border border-gray-200 text-center">
                        <BookOpen className="h-12 w-12 text-gray-400 mx-auto" />
                        <p className="text-gray-500 mt-4">No exams available</p>
                        <p className="text-sm text-gray-400 mt-2">Check back later for scheduled exams</p>
                    </div>
                )}
            </div>
        </StudentLayout>
    );
};

export default ExamsListPage;
