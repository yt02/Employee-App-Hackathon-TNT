import 'package:flutter/foundation.dart';
import '../models/message.dart';
import '../services/api_service.dart';

class ChatProvider with ChangeNotifier {
  final List<Message> _messages = [];
  final ApiService _apiService = ApiService();
  bool _isLoading = false;

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // Add user message
    final userMessage = Message(text: text, isUser: true);
    _messages.add(userMessage);
    notifyListeners();

    // Set loading state
    _isLoading = true;
    notifyListeners();

    try {
      // Get response from API
      final response = await _apiService.sendMessage(text);
      
      // Add bot message
      final botMessage = Message(text: response, isUser: false);
      _messages.add(botMessage);
    } catch (e) {
      // Add error message
      final errorMessage = Message(
        text: 'Sorry, I encountered an error: ${e.toString()}',
        isUser: false,
      );
      _messages.add(errorMessage);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearMessages() {
    _messages.clear();
    notifyListeners();
  }
}

