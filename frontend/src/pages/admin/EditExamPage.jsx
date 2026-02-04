import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import AdminLayout from '../../components/layouts/AdminLayout';
import examService from '../../services/examService';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';

const EditExamPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState({
        id: 1,
        text: '',
        type: 'multiple_choice',
        options: ['', '', '', ''],
        correct_answer: '',
        points: 10
    });

    useEffect(() => {
        loadExam();
    }, [id]);

    const loadExam = async () => {
        try {
            setLoading(true);
            const exam = await examService.getExamById(id);

            // Convert ISO dates to datetime-local format
            const startTime = exam.start_time ? exam.start_time.slice(0, 16) : '';
            const endTime = exam.end_time ? exam.end_time.slice(0, 16) : '';

            setFormData({
                title: exam.title,
                description: exam.description || '',
                start_time: startTime,
                end_time: endTime,
                duration_minutes: exam.duration_minutes,
                exam_config: exam.exam_config || { questions: [], settings: {} }
            });
        } catch (error) {
            console.error('Error loading exam:', error);
            alert('Failed to load exam');
            navigate('/admin/exams');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleQuestionChange = (e) => {
        const { name, value } = e.target;
        setCurrentQuestion(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleOptionChange = (index, value) => {
        const newOptions = [...currentQuestion.options];
        newOptions[index] = value;
        setCurrentQuestion(prev => ({
            ...prev,
            options: newOptions
        }));
    };

    const addQuestion = () => {
        if (!currentQuestion.text) {
            alert('Please enter question text');
            return;
        }

        setFormData(prev => ({
            ...prev,
            exam_config: {
                ...prev.exam_config,
                questions: [...prev.exam_config.questions, { ...currentQuestion }]
            }
        }));

        setCurrentQuestion({
            id: formData.exam_config.questions.length + 2,
            text: '',
            type: 'multiple_choice',
            options: ['', '', '', ''],
            correct_answer: '',
            points: 10
        });
    };

    const removeQuestion = (index) => {
        setFormData(prev => ({
            ...prev,
            exam_config: {
                ...prev.exam_config,
                questions: prev.exam_config.questions.filter((_, i) => i !== index)
            }
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.title || !formData.start_time || !formData.end_time) {
            alert('Please fill in all required fields');
            return;
        }

        try {
            setSaving(true);
            await examService.updateExam(id, formData);
            alert('Exam updated successfully!');
            navigate('/admin/exams');
        } catch (error) {
            console.error('Error updating exam:', error);
            alert(error.response?.data?.error || 'Failed to update exam');
        } finally {
            setSaving(false);
        }
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

    if (!formData) {
        return (
            <AdminLayout>
                <div className="text-center py-12">
                    <p className="text-gray-500">Exam not found</p>
                </div>
            </AdminLayout>
        );
    }

    return (
        <AdminLayout>
            <div className="max-w-4xl mx-auto">
                <div className="mb-6">
                    <button
                        onClick={() => navigate('/admin/exams')}
                        className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
                    >
                        <ArrowLeft className="h-5 w-5 mr-2" />
                        Back to Exams
                    </button>
                    <h1 className="text-3xl font-bold text-gray-900">Edit Exam</h1>
                    <p className="text-gray-600 mt-1">Update exam details and questions</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Basic Info - Same as CreateExamPage */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold mb-4">Basic Information</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Exam Title *
                                </label>
                                <input
                                    type="text"
                                    name="title"
                                    value={formData.title}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Description
                                </label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    rows={3}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Start Time *
                                    </label>
                                    <input
                                        type="datetime-local"
                                        name="start_time"
                                        value={formData.start_time}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        End Time *
                                    </label>
                                    <input
                                        type="datetime-local"
                                        name="end_time"
                                        value={formData.end_time}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Duration (minutes) *
                                    </label>
                                    <input
                                        type="number"
                                        name="duration_minutes"
                                        value={formData.duration_minutes}
                                        onChange={handleChange}
                                        min="1"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Questions - Same as CreateExamPage */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold mb-4">
                            Questions ({formData.exam_config.questions.length})
                        </h2>

                        {formData.exam_config.questions.map((q, index) => (
                            <div key={index} className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900">Q{index + 1}. {q.text}</p>
                                        <p className="text-sm text-gray-600 mt-1">
                                            Correct Answer: {q.correct_answer} | Points: {q.points}
                                        </p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => removeQuestion(index)}
                                        className="text-red-600 hover:text-red-700"
                                    >
                                        <Trash2 className="h-5 w-5" />
                                    </button>
                                </div>
                            </div>
                        ))}

                        {/* Add Question Form - Same as CreateExamPage */}
                        <div className="border-t border-gray-200 pt-4 mt-4">
                            <h3 className="font-medium text-gray-900 mb-3">Add New Question</h3>

                            <div className="space-y-3">
                                <input
                                    type="text"
                                    name="text"
                                    value={currentQuestion.text}
                                    onChange={handleQuestionChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    placeholder="Question text"
                                />

                                <div className="grid grid-cols-2 gap-3">
                                    {currentQuestion.options.map((option, idx) => (
                                        <input
                                            key={idx}
                                            type="text"
                                            value={option}
                                            onChange={(e) => handleOptionChange(idx, e.target.value)}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                            placeholder={`Option ${String.fromCharCode(65 + idx)}`}
                                        />
                                    ))}
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <select
                                        name="correct_answer"
                                        value={currentQuestion.correct_answer}
                                        onChange={handleQuestionChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    >
                                        <option value="">Select correct answer</option>
                                        {currentQuestion.options.map((opt, idx) => (
                                            opt && <option key={idx} value={opt}>{opt}</option>
                                        ))}
                                    </select>

                                    <input
                                        type="number"
                                        name="points"
                                        value={currentQuestion.points}
                                        onChange={handleQuestionChange}
                                        min="1"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                        placeholder="Points"
                                    />
                                </div>

                                <button
                                    type="button"
                                    onClick={addQuestion}
                                    className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                                >
                                    <Plus className="h-5 w-5 mr-2" />
                                    Add Question
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Submit */}
                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={() => navigate('/admin/exams')}
                            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </AdminLayout>
    );
};

export default EditExamPage;
