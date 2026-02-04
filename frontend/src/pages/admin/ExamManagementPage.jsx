import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../components/layouts/AdminLayout';
import examService from '../../services/examService';
import examAssignmentService from '../../services/examAssignmentService';
import adminService from '../../services/adminService';
import { Plus, Search, Filter, Edit, Trash2, PlayCircle, UserPlus, X } from 'lucide-react';

const ExamManagementPage = () => {
    const [exams, setExams] = useState([]);
    const [filteredExams, setFilteredExams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');

    // Assignment modal state
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [selectedExam, setSelectedExam] = useState(null);
    const [students, setStudents] = useState([]);
    const [selectedStudents, setSelectedStudents] = useState([]);
    const [assignmentLoading, setAssignmentLoading] = useState(false);

    useEffect(() => {
        loadExams();
    }, []);

    useEffect(() => {
        filterExams();
    }, [exams, searchTerm, statusFilter]);

    const loadExams = async () => {
        try {
            setLoading(true);
            const data = await examService.getAllExams();
            setExams(data || []); // Service already extracts .exams array
        } catch (error) {
            console.error('Error loading exams:', error);
        } finally {
            setLoading(false);
        }
    };

    const filterExams = () => {
        let filtered = exams;

        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(exam =>
                exam.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                exam.description?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Status filter
        if (statusFilter !== 'all') {
            filtered = filtered.filter(exam => exam.status === statusFilter);
        }

        setFilteredExams(filtered);
    };

    const handleDeleteExam = async (examId) => {
        if (!window.confirm('Are you sure you want to delete this exam? This action cannot be undone.')) {
            return;
        }

        try {
            await examService.deleteExam(examId);
            setExams(exams.filter(e => e.id !== examId));
        } catch (error) {
            console.error('Error deleting exam:', error);
            alert('Failed to delete exam');
        }
    };

    const handleStatusChange = async (examId, newStatus) => {
        try {
            await examService.changeExamStatus(examId, newStatus);
            setExams(exams.map(e => e.id === examId ? { ...e, status: newStatus } : e));
        } catch (error) {
            console.error('Error changing status:', error);
            alert('Failed to change exam status');
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            draft: 'bg-gray-100 text-gray-800',
            scheduled: 'bg-blue-100 text-blue-800',
            active: 'bg-green-100 text-green-800',
            completed: 'bg-purple-100 text-purple-800',
            cancelled: 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    const handleOpenAssignModal = async (exam) => {
        setSelectedExam(exam);
        setShowAssignModal(true);
        setSelectedStudents([]);

        // Load students
        try {
            const data = await adminService.getAllStudents();
            setStudents(data.students || []);
        } catch (error) {
            console.error('Error loading students:', error);
            alert('Failed to load students');
        }
    };

    const handleAssignExam = async () => {
        if (selectedStudents.length === 0) {
            alert('Please select at least one student');
            return;
        }

        try {
            setAssignmentLoading(true);
            const result = await examAssignmentService.assignExamToStudents(
                selectedExam.id,
                selectedStudents
            );

            const successCount = result.success?.length || 0;
            const failedCount = result.failed?.length || 0;

            // Build detailed message
            let message = `Assignment complete!\n${successCount} student(s) assigned successfully`;

            if (failedCount > 0 && result.failed) {
                message += `\n\n${failedCount} failed:`;
                result.failed.forEach((failure, idx) => {
                    message += `\n${idx + 1}. ${failure.student_id || 'Unknown'}: ${failure.reason || 'Unknown error'}`;
                });
            }

            alert(message);

            setShowAssignModal(false);
            setSelectedExam(null);
            setSelectedStudents([]);
        } catch (error) {
            console.error('Error assigning exam:', error);
            const errorMsg = error.response?.data?.error || error.message || error.toString();
            alert('Failed to assign exam:\n' + errorMsg);
        } finally {
            setAssignmentLoading(false);
        }
    };

    const toggleStudentSelection = (studentId) => {
        setSelectedStudents(prev =>
            prev.includes(studentId)
                ? prev.filter(id => id !== studentId)
                : [...prev, studentId]
        );
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
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Exam Management</h1>
                        <p className="text-gray-600 mt-1">Create, edit, and manage exams</p>
                    </div>
                    <Link
                        to="/admin/exams/new"
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Plus className="h-5 w-5" />
                        <span>Create Exam</span>
                    </Link>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Search */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search exams..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>

                        {/* Status Filter */}
                        <div className="relative">
                            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
                            >
                                <option value="all">All Status</option>
                                <option value="draft">Draft</option>
                                <option value="scheduled">Scheduled</option>
                                <option value="active">Active</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Exams List */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    {filteredExams.length > 0 ? (
                        <div className="divide-y divide-gray-200">
                            {filteredExams.map((exam) => (
                                <div key={exam.id} className="p-6 hover:bg-gray-50 transition-colors">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3">
                                                <h3 className="text-lg font-semibold text-gray-900">
                                                    {exam.title}
                                                </h3>
                                                <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(exam.status)}`}>
                                                    {exam.status}
                                                </span>
                                            </div>
                                            {exam.description && (
                                                <p className="text-gray-600 mt-2">{exam.description}</p>
                                            )}
                                            <div className="flex items-center space-x-6 mt-3 text-sm text-gray-600">
                                                <span>Duration: {exam.duration_minutes} min</span>
                                                <span>Start: {new Date(exam.start_time).toLocaleString()}</span>
                                                <span>End: {new Date(exam.end_time).toLocaleString()}</span>
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex items-center space-x-2 ml-4">
                                            {exam.status !== 'cancelled' && (
                                                <button
                                                    onClick={() => handleOpenAssignModal(exam)}
                                                    className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                                                    title={exam.status === 'draft' ? 'Assign to Students (Exam will remain in draft until published)' : 'Assign to Students'}
                                                >
                                                    <UserPlus className="h-5 w-5" />
                                                </button>
                                            )}
                                            {exam.status === 'draft' && (
                                                <button
                                                    onClick={() => handleStatusChange(exam.id, 'scheduled')}
                                                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                                    title="Publish"
                                                >
                                                    <PlayCircle className="h-5 w-5" />
                                                </button>
                                            )}
                                            <Link
                                                to={`/admin/exams/${exam.id}/edit`}
                                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                title="Edit"
                                            >
                                                <Edit className="h-5 w-5" />
                                            </Link>
                                            <button
                                                onClick={() => handleDeleteExam(exam.id)}
                                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                title="Delete"
                                            >
                                                <Trash2 className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-12 text-center">
                            <p className="text-gray-500">No exams found</p>
                            {searchTerm || statusFilter !== 'all' ? (
                                <button
                                    onClick={() => {
                                        setSearchTerm('');
                                        setStatusFilter('all');
                                    }}
                                    className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
                                >
                                    Clear filters
                                </button>
                            ) : (
                                <Link
                                    to="/admin/exams/new"
                                    className="inline-block mt-4 text-blue-600 hover:text-blue-700 font-medium"
                                >
                                    Create your first exam
                                </Link>
                            )}
                        </div>
                    )}
                </div>

                {/* Assignment Modal */}
                {showAssignModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
                            {/* Modal Header */}
                            <div className="flex items-center justify-between p-6 border-b border-gray-200">
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-900">Assign Exam to Students</h2>
                                    <p className="text-gray-600 mt-1">{selectedExam?.title}</p>
                                </div>
                                <button
                                    onClick={() => setShowAssignModal(false)}
                                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    <X className="h-6 w-6 text-gray-500" />
                                </button>
                            </div>

                            {/* Modal Body */}
                            <div className="flex-1 overflow-y-auto p-6">
                                {students.length > 0 ? (
                                    <div className="space-y-2">
                                        {students.map((student) => (
                                            <label
                                                key={student.id}
                                                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={selectedStudents.includes(student.id)}
                                                    onChange={() => toggleStudentSelection(student.id)}
                                                    className="h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                                />
                                                <div className="ml-3">
                                                    <p className="font-medium text-gray-900">{student.full_name}</p>
                                                    <p className="text-sm text-gray-600">{student.email}</p>
                                                </div>
                                            </label>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8">
                                        <p className="text-gray-500">No students found. Create students first.</p>
                                    </div>
                                )}
                            </div>

                            {/* Modal Footer */}
                            <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
                                <p className="text-sm text-gray-600">
                                    {selectedStudents.length} student(s) selected
                                </p>
                                <div className="flex space-x-3">
                                    <button
                                        onClick={() => setShowAssignModal(false)}
                                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleAssignExam}
                                        disabled={assignmentLoading || selectedStudents.length === 0}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                                    >
                                        {assignmentLoading ? 'Assigning...' : 'Assign Exam'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </AdminLayout>
    );
};

export default ExamManagementPage;
