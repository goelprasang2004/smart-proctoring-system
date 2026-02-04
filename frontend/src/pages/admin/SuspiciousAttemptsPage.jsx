import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../components/layouts/AdminLayout';
import proctoringService from '../../services/proctoringService';
import { AlertTriangle, Eye, Calendar, User } from 'lucide-react';

const SuspiciousAttemptsPage = () => {
    const [attempts, setAttempts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [confidenceThreshold, setConfidenceThreshold] = useState(0.0);
    const [minEvents, setMinEvents] = useState(1);

    useEffect(() => {
        loadSuspiciousAttempts();
    }, [confidenceThreshold, minEvents]);

    const loadSuspiciousAttempts = async () => {
        try {
            setLoading(true);
            const data = await proctoringService.getSuspiciousAttempts(confidenceThreshold, minEvents);
            setAttempts(data);
        } catch (error) {
            console.error('Error loading suspicious attempts:', error);
        } finally {
            setLoading(false);
        }
    };

    const getRiskLevel = (confidence) => {
        if (confidence >= 0.8) return { label: 'High', color: 'bg-red-100 text-red-800 border-red-300' };
        if (confidence >= 0.6) return { label: 'Medium', color: 'bg-orange-100 text-orange-800 border-orange-300' };
        return { label: 'Low', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' };
    };

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
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Suspicious Attempts</h1>
                    <p className="text-gray-600 mt-1">Monitor exam attempts with potential integrity issues</p>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Confidence Threshold: {(confidenceThreshold * 100).toFixed(0)}%
                            </label>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.1"
                                value={confidenceThreshold}
                                onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                                className="w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Minimum Events: {minEvents}
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="20"
                                step="1"
                                value={minEvents}
                                onChange={(e) => setMinEvents(parseInt(e.target.value))}
                                className="w-full"
                            />
                        </div>
                    </div>
                </div>

                {/* Attempts List */}
                <div className="space-y-4">
                    {attempts.length > 0 ? (
                        attempts.map((attempt) => {
                            const risk = getRiskLevel(attempt.avg_confidence);
                            return (
                                <div
                                    key={attempt.attempt_id}
                                    className="bg-white p-6 rounded-lg shadow-sm border-2 border-gray-200 hover:shadow-md transition-shadow"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3">
                                                <AlertTriangle className="h-6 w-6 text-red-600" />
                                                <h3 className="text-lg font-semibold text-gray-900">
                                                    Exam Attempt #{attempt.attempt_id.slice(0, 8)}
                                                </h3>
                                                <span className={`px-3 py-1 text-xs font-medium rounded-full border ${risk.color}`}>
                                                    {risk.label} Risk
                                                </span>
                                                {attempt.status === 'terminated' && (
                                                    <span className="px-3 py-1 text-xs font-medium rounded-full bg-red-600 text-white">
                                                        Terminated
                                                    </span>
                                                )}
                                            </div>

                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                                                <div className="flex items-center space-x-2 text-gray-600">
                                                    <User className="h-4 w-4" />
                                                    <span className="text-sm">{attempt.student_name || 'Unknown Student'}</span>
                                                </div>
                                                <div className="flex items-center space-x-2 text-gray-600">
                                                    <Calendar className="h-4 w-4" />
                                                    <span className="text-sm">
                                                        Exam ID: {attempt.exam_id.slice(0, 8)}
                                                    </span>
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    <span className="font-medium text-red-600">{attempt.suspicious_event_count}</span> suspicious events
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    Avg confidence: <span className="font-medium">{(attempt.avg_confidence * 100).toFixed(0)}%</span>
                                                </div>
                                            </div>

                                            {/* Detailed Event Types */}
                                            <div className="mt-3 flex flex-wrap gap-2">
                                                {(attempt.event_types || []).map((type, idx) => (
                                                    <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded border border-gray-200">
                                                        {type}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>

                                        <Link
                                            to={`/admin/proctoring/${attempt.attempt_id}`}
                                            className="ml-4 flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                        >
                                            <Eye className="h-4 w-4" />
                                            <span>View Details</span>
                                        </Link>
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        <div className="bg-white p-12 rounded-lg shadow-sm border border-gray-200 text-center">
                            <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto" />
                            <p className="text-gray-500 mt-4">No suspicious attempts found</p>
                            <p className="text-sm text-gray-400 mt-2">Adjust the filters to see more results</p>
                        </div>
                    )}
                </div>
            </div>
        </AdminLayout>
    );
};

export default SuspiciousAttemptsPage;
