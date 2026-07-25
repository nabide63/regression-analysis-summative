import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}

// Calls my Task 2 API (POST /predict) and returns the predicted yield.
class PredictionApi {
  String baseUrl;

  PredictionApi({required this.baseUrl});

  Future<double> predict(Map<String, dynamic> features) async {
    final uri = Uri.parse('$baseUrl/predict');

    http.Response response;
    try {
      response = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(features),
          )
          .timeout(const Duration(seconds: 15));
    } catch (e) {
      throw ApiException('Could not reach the API at $baseUrl.\n($e)');
    }

    dynamic body;
    try {
      body = jsonDecode(response.body);
    } catch (_) {
      body = null;
    }

    if (response.statusCode != 200) {
      throw ApiException(_extractDetail(body, response.statusCode));
    }

    final prediction = body is Map ? body['predicted_milk_yield_l'] : null;
    if (prediction is! num) {
      throw ApiException('Unexpected response from API: ${response.body}');
    }
    return prediction.toDouble();
  }

  String _extractDetail(dynamic body, int statusCode) {
    final detail = body is Map ? body['detail'] : null;
    if (detail == null) return 'Request failed with status $statusCode.';
    if (detail is String) return detail;
    if (detail is List) {
      return detail.map((e) {
        if (e is Map && e['msg'] != null) {
          final loc = e['loc'] is List ? (e['loc'] as List).join('.') : '';
          return '$loc: ${e['msg']}';
        }
        return e.toString();
      }).join('\n');
    }
    return detail.toString();
  }
}
