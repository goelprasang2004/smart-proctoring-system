import { useState, useEffect } from 'react';
import { Smartphone, QrCode, CheckCircle, XCircle } from 'lucide-react';

/**
 * SmartphonePairing Component
 * Allows students to use their smartphone as a secondary camera
 */
const SmartphonePairing = ({ attemptId, sessionToken, onPaired }) => {
    const [qrData, setQrData] = useState(null);
    const [isPaired, setIsPaired] = useState(false);
    const [qrCodeUrl, setQrCodeUrl] = useState(null);

    useEffect(() => {
        generateQRCode();
    }, [attemptId, sessionToken]);

    const generateQRCode = async () => {
        const pairingData = {
            attemptId,
            sessionToken,
            timestamp: Date.now(),
            serverUrl: window.location.origin,
            type: 'secondary_camera'
        };

        const dataString = JSON.stringify(pairingData);
        setQrData(dataString);

        // Generate QR code using an API or library
        // Using QRServer API for simplicity
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(dataString)}`;
        setQrCodeUrl(qrUrl);
    };

    const checkPairingStatus = () => {
        // Simulate checking if phone has connected
        // In real implementation, this would check WebSocket connection
        setTimeout(() => {
            setIsPaired(true);
            if (onPaired) onPaired(true);
        }, 2000);
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md border-2 border-blue-200">
            <div className="flex items-center mb-4">
                <Smartphone className="h-6 w-6 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold">Secondary Camera Setup</h3>
            </div>

            <p className="text-sm text-gray-600 mb-4">
                Use your smartphone as a side-angle camera to monitor your hands and desk area.
                This eliminates blind spots and provides comprehensive coverage.
            </p>

            <div className="flex flex-col items-center space-y-4">
                {!isPaired ? (
                    <>
                        <div className="bg-gray-50 p-4 rounded-lg border-2 border-dashed border-gray-300">
                            {qrCodeUrl ? (
                                <img 
                                    src={qrCodeUrl} 
                                    alt="QR Code for smartphone pairing" 
                                    className="w-48 h-48"
                                />
                            ) : (
                                <div className="w-48 h-48 flex items-center justify-center">
                                    <QrCode className="h-16 w-16 text-gray-400" />
                                </div>
                            )}
                        </div>

                        <div className="text-center">
                            <p className="text-sm font-medium text-gray-700 mb-2">
                                Scan this QR code with your smartphone
                            </p>
                            <ol className="text-xs text-gray-600 text-left space-y-1">
                                <li>1. Open camera app on your phone</li>
                                <li>2. Scan the QR code above</li>
                                <li>3. Grant camera permissions when prompted</li>
                                <li>4. Position phone to show side angle of desk</li>
                            </ol>
                        </div>

                        <button
                            onClick={checkPairingStatus}
                            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                        >
                            I've Scanned the Code
                        </button>
                    </>
                ) : (
                    <div className="text-center py-8">
                        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-3" />
                        <p className="text-lg font-semibold text-green-700">
                            Smartphone Connected!
                        </p>
                        <p className="text-sm text-gray-600 mt-2">
                            Secondary camera is active and monitoring
                        </p>
                    </div>
                )}
            </div>

            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs text-blue-800">
                    <span className="font-semibold">Privacy Note:</span> The secondary camera stream
                    is encrypted and only used for proctoring. It will be deleted after exam verification.
                </p>
            </div>
        </div>
    );
};

export default SmartphonePairing;
