import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:provider/provider.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({Key? key}) : super(key: key);

  @override
  _QRScannerScreenState createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  MobileScannerController cameraController = MobileScannerController();
  bool isScanning = true;
  String? scannedData;

  @override
  void dispose() {
    cameraController.dispose();
    super.dispose();
  }

  void _onQRCodeDetect(BarcodeCapture capture) {
    if (!isScanning) return;
    
    final List<Barcode> barcodes = capture.barcodes;
    if (barcodes.isNotEmpty) {
      setState(() {
        isScanning = false;
        scannedData = barcodes.first.rawValue;
      });
      
      _processQRCode(scannedData!);
    }
  }

  Future<void> _processQRCode(String qrData) async {
    try {
      // Parse QR data: fatigue-app:token:user_id:device_type
      final parts = qrData.split(':');
      if (parts.length != 4 || parts[0] != 'fatigue-app') {
        throw Exception('Invalid QR code format');
      }

      final token = parts[1];
      final userId = parts[2];
      final deviceType = parts[3];

      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final deviceId = await authProvider.getDeviceId();

      // Verify pairing with backend
      final apiService = ApiService();
      final response = await apiService.verifyPairing(
        token: token,
        deviceId: deviceId,
      );

      if (response['success']) {
        // Update auth provider with paired user
        await authProvider.setPairedUser(userId);
        
        if (mounted) {
          Navigator.pushReplacementNamed(context, '/dashboard');
        }
      } else {
        throw Exception('Pairing failed');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
        setState(() => isScanning = true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Code'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: cameraController,
            onDetect: _onQRCodeDetect,
          ),
          Positioned.fill(
            child: CustomPaint(
              painter: QRScannerOverlay(
                scanArea: MediaQuery.of(context).size.width * 0.7,
              ),
            ),
          ),
          Positioned(
            bottom: 50,
            left: 0,
            right: 0,
            child: Column(
              children: [
                Text(
                  'Align QR code within the frame',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 20),
                if (!isScanning)
                  const CircularProgressIndicator(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class QRScannerOverlay extends CustomPainter {
  final double scanArea;

  QRScannerOverlay({required this.scanArea});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(0.5)
      ..style = PaintingStyle.fill;

    // Draw darkened overlay
    canvas.drawRect(Rect.fromLTRB(0, 0, size.width, size.height), paint);

    // Clear scanning area
    final scanRect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2),
      width: scanArea,
      height: scanArea,
    );
    canvas.drawRect(scanRect, Paint()..blendMode = BlendMode.clear);

    // Draw border
    final borderPaint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;

    canvas.drawRect(scanRect, borderPaint);

    // Draw corners
    final cornerPaint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    final cornerLength = 30.0;
    final offset = 2.0;

    // Top-left corner
    canvas.drawLine(
      Offset(scanRect.left + offset, scanRect.top + cornerLength),
      Offset(scanRect.left + offset, scanRect.top + offset),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(scanRect.left + offset, scanRect.top + offset),
      Offset(scanRect.left + cornerLength, scanRect.top + offset),
      cornerPaint,
    );

    // Top-right corner
    canvas.drawLine(
      Offset(scanRect.right - offset, scanRect.top + cornerLength),
      Offset(scanRect.right - offset, scanRect.top + offset),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(scanRect.right - offset, scanRect.top + offset),
      Offset(scanRect.right - cornerLength, scanRect.top + offset),
      cornerPaint,
    );

    // Bottom-left corner
    canvas.drawLine(
      Offset(scanRect.left + offset, scanRect.bottom - cornerLength),
      Offset(scanRect.left + offset, scanRect.bottom - offset),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(scanRect.left + offset, scanRect.bottom - offset),
      Offset(scanRect.left + cornerLength, scanRect.bottom - offset),
      cornerPaint,
    );

    // Bottom-right corner
    canvas.drawLine(
      Offset(scanRect.right - offset, scanRect.bottom - cornerLength),
      Offset(scanRect.right - offset, scanRect.bottom - offset),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(scanRect.right - offset, scanRect.bottom - offset),
      Offset(scanRect.right - cornerLength, scanRect.bottom - offset),
      cornerPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}