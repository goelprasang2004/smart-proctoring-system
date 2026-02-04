import { useState, useEffect } from 'react';
import StudentLayout from '../components/layouts/StudentLayout';
import resultsService from '../services/resultsService';
import { Award, Calendar, Clock, AlertCircle, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';

const MyResultsPage = () => {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadResults();
    }, []);

    const loadResults = async () => {
        try {
            setLoading(true);
            const data = await resultsService.getMyResults();
            setResults(data || []);
        } catch (error) {
            console.error('Error loading results:', error);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (!score) return 'text-gray-600';
        if (score >= 70) return 'text-green-600';
        if (score >= 50) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getPassStatus = (score) => {
        if (!score) return { label: 'Pending', color: 'bg-gray-100 text-gray-800' };
        if (score >= 70) return { label: 'Passed', color: 'bg-green-100 text-green-800' };
        if (score >= 50) return { label: 'Marginal', color: 'bg-yellow-100 text-yellow-800' };
        return { label: 'Failed', color: 'bg-red-100 text-red-800' };
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
                    <h1 className="text-3xl font-bold text-gray-900">My Results</h1>
                    <p className="text-gray-600 mt-1">View your exam attempts and results</p>
                </div>

                {/* Results List */}
                {results.length > 0 ? (
                    <div className="space-y-4">
                        {results.map((result) => {
                            const status = getPassStatus(result.score);
                            return (
                                <div
                                    key={result.id}
                                    className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <h3 className="text-lg font-semibold text-gray-900">
                                                {result.exam_title}
                                            </h3>
                                            <div className="flex items-center space-x-6 mt-3 text-sm text-gray-600">
                                                <div className="flex items-center space-x-2">
                                                    <Calendar className="h-4 w-4" />
                                                    <span>
                                                        {result.submitted_at
                                                            ? new Date(result.submitted_at).toLocaleDateString()
                                                            : 'N/A'}
                                                    </span>
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <Clock className="h-4 w-4" />
                                                    <span>
                                                        Started: {result.started_at
                                                            ? new Date(result.started_at).toLocaleString()
                                                            : 'N/A'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right ml-4">
                                            <div className={`text-3xl font-bold ${getScoreColor(result.score)}`}>
                                                {result.score !== null && result.score !== undefined
                                                    ? `${result.score.toFixed(1)}%`
                                                    : '--'}
                                            </div>
                                            <span className={`inline-block mt-2 px-3 py-1 text-xs font-medium rounded-full ${status.color}`}>
                                                {status.label}
                                            </span>
                                            {result.attempt_id && (
                                                <Link
                                                    to={`/results/${result.attempt_id}`}
                                                    className="mt-3 flex items-center justify-center space-x-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
                                                >
                                                    <Eye className="h-4 w-4" />
                                                    <span>View Details</span>
                                                </Link>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="bg-white p-12 rounded-lg shadow-sm border border-gray-200 text-center">
                        <Award className="h-12 w-12 text-gray-400 mx-auto" />
                        <p className="text-gray-500 mt-4">No results yet</p>
                        <p className="text-sm text-gray-400 mt-2">Complete an exam to see your results here</p>
                        <Link
                            to="/exams"
                            className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Browse Exams
                        </Link>
                    </div>
                )}

                {/* Info Note */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                        <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-blue-900">
                            <p className="font-semibold">About Results</p>
                            <p className="mt-1">
                                Results are available immediately after exam submission.
                                All exams are monitored by our AI proctoring system to ensure fairness.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </StudentLayout>
    );
};

export default MyResultsPage;

