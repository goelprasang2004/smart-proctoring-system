import { useState, useEffect } from 'react';
import { Heart, TrendingUp, TrendingDown, Coffee, AlertCircle } from 'lucide-react';
import advancedProctoring from '../../services/advancedProctoring';

/**
 * StressMonitor Component
 * Adaptive AI that detects test anxiety and suggests breaks
 */
const StressMonitor = ({ videoRef, onBreakSuggested }) => {
    const [stressData, setStressData] = useState({
        stressLevel: 'low',
        score: 0,
        recommendation: null
    });
    const [showBreakSuggestion, setShowBreakSuggestion] = useState(false);
    const [breakTimer, setBreakTimer] = useState(30);
    const [onBreak, setOnBreak] = useState(false);

    useEffect(() => {
        // Monitor stress every 10 seconds
        const interval = setInterval(async () => {
            if (videoRef?.current && !onBreak) {
                const stress = await advancedProctoring.detectStressLevel(videoRef.current);
                setStressData(stress);

                if (stress.shouldSuggestBreak && !showBreakSuggestion) {
                    setShowBreakSuggestion(true);
                }
            }
        }, 10000);

        return () => clearInterval(interval);
    }, [videoRef, onBreak]);

    useEffect(() => {
        if (onBreak && breakTimer > 0) {
            const timer = setTimeout(() => {
                setBreakTimer(breakTimer - 1);
            }, 1000);
            return () => clearTimeout(timer);
        } else if (onBreak && breakTimer === 0) {
            handleEndBreak();
        }
    }, [onBreak, breakTimer]);

    const handleTakeBreak = () => {
        setOnBreak(true);
        setShowBreakSuggestion(false);
        setBreakTimer(30);
        if (onBreakSuggested) onBreakSuggested(true);
    };

    const handleEndBreak = () => {
        setOnBreak(false);
        setBreakTimer(30);
        if (onBreakSuggested) onBreakSuggested(false);
    };

    const getStressColor = () => {
        switch (stressData.stressLevel) {
            case 'high': return 'text-red-600 bg-red-50';
            case 'medium': return 'text-yellow-600 bg-yellow-50';
            default: return 'text-green-600 bg-green-50';
        }
    };

    const getStressIcon = () => {
        switch (stressData.stressLevel) {
            case 'high': return <TrendingUp className="h-4 w-4" />;
            case 'medium': return <AlertCircle className="h-4 w-4" />;
            default: return <TrendingDown className="h-4 w-4" />;
        }
    };

    return (
        <div className="space-y-3">
            {/* Stress Level Indicator */}
            <div className={`flex items-center justify-between p-3 rounded-lg ${getStressColor()}`}>
                <div className="flex items-center space-x-2">
                    <Heart className="h-4 w-4" />
                    <span className="text-sm font-medium">Stress Level</span>
                </div>
                <div className="flex items-center space-x-2">
                    {getStressIcon()}
                    <span className="text-xs font-semibold uppercase">
                        {stressData.stressLevel}
                    </span>
                </div>
            </div>

            {/* Break Suggestion Modal */}
            {showBreakSuggestion && !onBreak && (
                <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 animate-pulse">
                    <div className="flex items-start space-x-3">
                        <Coffee className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                            <h4 className="text-sm font-semibold text-blue-900 mb-1">
                                Take a Mindfulness Break?
                            </h4>
                            <p className="text-xs text-blue-700 mb-3">
                                We detected elevated stress levels. A 30-second breathing exercise
                                can help you refocus and reduce false anxiety flags.
                            </p>
                            <div className="flex space-x-2">
                                <button
                                    onClick={handleTakeBreak}
                                    className="px-3 py-1.5 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700"
                                >
                                    Yes, Take Break
                                </button>
                                <button
                                    onClick={() => setShowBreakSuggestion(false)}
                                    className="px-3 py-1.5 bg-white border border-blue-300 text-blue-700 rounded text-xs font-medium hover:bg-blue-50"
                                >
                                    Continue
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Break Timer */}
            {onBreak && (
                <div className="bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg p-6 text-white text-center">
                    <Coffee className="h-12 w-12 mx-auto mb-3 opacity-90" />
                    <h3 className="text-xl font-bold mb-2">Mindfulness Break</h3>
                    <p className="text-sm mb-4 opacity-90">
                        Take deep breaths. Relax your shoulders. You're doing great!
                    </p>
                    <div className="text-5xl font-bold mb-2">
                        {breakTimer}s
                    </div>
                    <p className="text-xs opacity-75">
                        This break won't affect your exam time
                    </p>
                    <button
                        onClick={handleEndBreak}
                        className="mt-4 px-4 py-2 bg-white text-indigo-600 rounded-lg text-sm font-medium hover:bg-indigo-50"
                    >
                        End Break Early
                    </button>
                </div>
            )}

            {/* Recommendation */}
            {stressData.recommendation && !onBreak && !showBreakSuggestion && (
                <div className="bg-gray-50 border border-gray-200 rounded p-2">
                    <p className="text-xs text-gray-600 italic">
                        💡 {stressData.recommendation}
                    </p>
                </div>
            )}
        </div>
    );
};

export default StressMonitor;
