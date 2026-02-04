import { useState, useEffect } from 'react';
import AdminLayout from '../../components/layouts/AdminLayout';
import blockchainService from '../../services/blockchainService';
import { Link2, CheckCircle, XCircle, Search } from 'lucide-react';

const BlockchainAuditPage = () => {
    const [summary, setSummary] = useState(null);
    const [verification, setVerification] = useState(null);
    const [loading, setLoading] = useState(true);
    const [verifying, setVerifying] = useState(false);

    useEffect(() => {
        loadBlockchainData();
    }, []);

    const loadBlockchainData = async () => {
        try {
            setLoading(true);
            const summaryData = await blockchainService.getSummary();
            setSummary(summaryData.summary);
        } catch (error) {
            console.error('Error loading blockchain data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleVerify = async () => {
        try {
            setVerifying(true);
            const result = await blockchainService.verifyIntegrity();
            setVerification(result.verification);
        } catch (error) {
            console.error('Error verifying blockchain:', error);
        } finally {
            setVerifying(false);
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

    return (
        <AdminLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Blockchain Audit Trail</h1>
                    <p className="text-gray-600 mt-1">Immutable record of all system events</p>
                </div>

                {/* Summary Stats */}
                {summary && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Total Blocks</p>
                                    <p className="text-3xl font-bold text-gray-900 mt-2">{summary.total_blocks || 0}</p>
                                </div>
                                <div className="p-3 rounded-full bg-blue-100">
                                    <Link2 className="h-6 w-6 text-blue-600" />
                                </div>
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Event Types</p>
                                    <p className="text-3xl font-bold text-gray-900 mt-2">{summary.event_types?.length || 0}</p>
                                </div>
                                <div className="p-3 rounded-full bg-purple-100">
                                    <Search className="h-6 w-6 text-purple-600" />
                                </div>
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Latest Block</p>
                                    <p className="text-sm text-gray-900 mt-2 font-mono truncate">
                                        {summary.latest_hash?.slice(0, 16)}...
                                    </p>
                                </div>
                                <div className="p-3 rounded-full bg-green-100">
                                    <CheckCircle className="h-6 w-6 text-green-600" />
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Verify Integrity */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h2 className="text-lg font-semibold text-gray-900">Verify Blockchain Integrity</h2>
                            <p className="text-sm text-gray-600 mt-1">Check that all blocks are valid and properly linked</p>
                        </div>
                        <button
                            onClick={handleVerify}
                            disabled={verifying}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                        >
                            {verifying ? 'Verifying...' : 'Run Verification'}
                        </button>
                    </div>

                    {verification && (
                        <div className={`mt-4 p-4 rounded-lg border-2 ${verification.is_valid ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'
                            }`}>
                            <div className="flex items-start space-x-3">
                                {verification.is_valid ? (
                                    <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
                                ) : (
                                    <XCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
                                )}
                                <div>
                                    <p className={`font-semibold ${verification.is_valid ? 'text-green-900' : 'text-red-900'}`}>
                                        {verification.is_valid ? 'Blockchain Verified' : 'Integrity Issues Detected'}
                                    </p>
                                    <p className={`text-sm mt-1 ${verification.is_valid ? 'text-green-700' : 'text-red-700'}`}>
                                        Checked {verification.blocks_checked} blocks
                                    </p>
                                    {verification.errors && verification.errors.length > 0 && (
                                        <div className="mt-2 text-sm text-red-700">
                                            <p className="font-medium">Errors found:</p>
                                            <ul className="list-disc list-inside mt-1">
                                                {verification.errors.map((error, index) => (
                                                    <li key={index}>{error}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Event Types */}
                {summary?.event_types && summary.event_types.length > 0 && (
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">Event Types</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {summary.event_types.map((eventType) => (
                                <div
                                    key={eventType}
                                    className="px-3 py-2 bg-gray-100 rounded-lg text-sm font-medium text-gray-700"
                                >
                                    {eventType.replace(/_/g, ' ')}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Note */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-900">
                        <span className="font-semibold">Note:</span> The blockchain provides an immutable audit trail
                        of all critical system events. Each block is cryptographically linked to the previous block,
                        ensuring data integrity and preventing tampering.
                    </p>
                </div>
            </div>
        </AdminLayout>
    );
};

export default BlockchainAuditPage;
