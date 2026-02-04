import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/layouts/AdminLayout';
import examService from '../../services/examService';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';

const CreateExamPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        start_time: '',
        end_time: '',
        duration_minutes: 60,
        exam_config: {
            questions: [],
            settings: {
                shuffle_questions: false,
                show_results_immediately: false,
                passing_score: 60
            }
        }
    });

    const [currentQuestion, setCurrentQuestion] = useState({
        id: 1,
        text: '',
        type: 'multiple_choice',
        options: ['', '', '', ''],
        correct_answer: '',
        points: 10
    });

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

        const newQuestion = { ...currentQuestion };

        setFormData(prev => ({
            ...prev,
            exam_config: {
                ...prev.exam_config,
                questions: [...prev.exam_config.questions, newQuestion]
            }
        }));

        // Reset current question
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

        // Validation
        if (!formData.title) {
            alert('Please enter exam title');
            return;
        }

        if (!formData.start_time || !formData.end_time) {
            alert('Please set exam start and end times');
            return;
        }

        if (formData.exam_config.questions.length === 0) {
            alert('Please add at least one question');
            return;
        }

        try {
            setLoading(true);
            await examService.createExam(formData);
            alert('Exam created successfully!');
            navigate('/admin/exams');
        } catch (error) {
            console.error('Error creating exam:', error);
            alert(error.response?.data?.error || 'Failed to create exam');
        } finally {
            setLoading(false);
        }
    };

    return (
        <AdminLayout>
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-6">
                    <button
                        onClick={() => navigate('/admin/exams')}
                        className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
                    >
                        <ArrowLeft className="h-5 w-5 mr-2" />
                        Back to Exams
                    </button>
                    <h1 className="text-3xl font-bold text-gray-900">Create New Exam</h1>
                    <p className="text-gray-600 mt-1">Fill in the exam details and questions</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Basic Info */}
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
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="e.g., Final Exam - Computer Science"
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
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="Brief description of the exam"
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
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Questions */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold mb-4">
                            Questions ({formData.exam_config.questions.length})
                        </h2>

                        {/* Added Questions */}
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

                        {/* Add New Question */}
                        <div className="border-t border-gray-200 pt-4 mt-4">
                            <h3 className="font-medium text-gray-900 mb-3">Add New Question</h3>

                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Question Text *
                                    </label>
                                    <input
                                        type="text"
                                        name="text"
                                        value={currentQuestion.text}
                                        onChange={handleQuestionChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Enter question"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    {currentQuestion.options.map((option, idx) => (
                                        <div key={idx}>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Option {String.fromCharCode(65 + idx)}
                                            </label>
                                            <input
                                                type="text"
                                                value={option}
                                                onChange={(e) => handleOptionChange(idx, e.target.value)}
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                placeholder={`Option ${String.fromCharCode(65 + idx)}`}
                                            />
                                        </div>
                                    ))}
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Correct Answer *
                                        </label>
                                        <select
                                            name="correct_answer"
                                            value={currentQuestion.correct_answer}
                                            onChange={handleQuestionChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="">Select correct answer</option>
                                            {currentQuestion.options.map((opt, idx) => (
                                                opt && <option key={idx} value={opt}>{opt}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Points
                                        </label>
                                        <input
                                            type="number"
                                            name="points"
                                            value={currentQuestion.points}
                                            onChange={handleQuestionChange}
                                            min="1"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
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
                            disabled={loading}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : 'Create Exam'}
                        </button>
                    </div>
                </form>
            </div>
        </AdminLayout>
    );
};

export default CreateExamPage;
