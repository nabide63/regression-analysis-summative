import 'package:flutter/material.dart';

import '../models/feature_specs.dart';
import '../services/api_service.dart';

class PredictScreen extends StatefulWidget {
  const PredictScreen({super.key});

  @override
  State<PredictScreen> createState() => _PredictScreenState();
}

class _PredictScreenState extends State<PredictScreen> {
  final _formKey = GlobalKey<FormState>();
  final _scrollController = ScrollController();
  final _resultKey = GlobalKey();
  late PredictionApi _api;
  late TextEditingController _baseUrlController;

  final Map<String, TextEditingController> _numericControllers = {};
  final Map<String, bool> _vaccineValues = {};
  final Map<String, String> _categoricalValues = {};

  bool _loading = false;
  String? _error;
  double? _result;

  @override
  void initState() {
    super.initState();
    _baseUrlController = TextEditingController(
      text: 'https://milk-yield-predictor-viec.onrender.com',
    );
    _api = PredictionApi(baseUrl: _baseUrlController.text);

    for (final spec in allNumericFields) {
      _numericControllers[spec.key] = TextEditingController(
        text: spec.isInt
            ? spec.defaultValue.toInt().toString()
            : spec.defaultValue.toString(),
      );
    }
    for (final spec in vaccineFields) {
      _vaccineValues[spec.key] = spec.defaultValue;
    }
    for (final spec in categoricalFields) {
      _categoricalValues[spec.key] = spec.defaultValue;
    }
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    _scrollController.dispose();
    for (final c in _numericControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  void _scrollToResult() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final context = _resultKey.currentContext;
      if (context != null) {
        Scrollable.ensureVisible(
          context,
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeInOut,
          alignment: 0.1,
        );
      }
    });
  }

  Future<void> _editBaseUrl() async {
    final controller = TextEditingController(text: _baseUrlController.text);
    final updated = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('API base URL'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'https://milk-yield-predictor-viec.onrender.com',
            helperText: 'Defaults to my deployed API. Change this if you\'re running the backend locally.',
          ),
          keyboardType: TextInputType.url,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (updated != null && updated.isNotEmpty) {
      setState(() {
        _baseUrlController.text = updated;
        _api = PredictionApi(baseUrl: updated);
      });
    }
  }

  Future<void> _submit() async {
    final form = _formKey.currentState;
    if (form == null || !form.validate()) return;

    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    final payload = <String, dynamic>{};
    for (final spec in allNumericFields) {
      final text = _numericControllers[spec.key]!.text;
      final value = num.parse(text);
      payload[spec.key] = spec.isInt ? value.toInt() : value.toDouble();
    }
    for (final spec in vaccineFields) {
      payload[spec.key] = (_vaccineValues[spec.key]! ? 1 : 0);
    }
    for (final spec in categoricalFields) {
      payload[spec.key] = _categoricalValues[spec.key];
    }

    try {
      final prediction = await _api.predict(payload);
      setState(() => _result = prediction);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      setState(() => _loading = false);
      _scrollToResult();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Milk Yield Predictor'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'API base URL',
            onPressed: _editBaseUrl,
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          controller: _scrollController,
          padding: const EdgeInsets.all(16),
          children: [
            _buildSection(context, 'Animal profile', animalProfileFields),
            _buildSection(context, 'Feeding', feedingFields),
            _buildSection(context, 'Activity', activityFields),
            _buildSection(context, 'Environment & housing', environmentFields),
            _buildSection(context, 'Milking', milkingFields),
            _buildVaccineSection(context),
            _buildCategoricalSection(context),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _loading ? null : _submit,
              icon: _loading
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.query_stats),
              label: Text(_loading ? 'Predicting…' : 'Predict milk yield'),
              style: FilledButton.styleFrom(padding: const EdgeInsets.all(16)),
            ),
            const SizedBox(height: 16),
            Container(
              key: _resultKey,
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                transitionBuilder: (child, animation) => SizeTransition(
                  sizeFactor: animation,
                  alignment: Alignment.topCenter,
                  child: FadeTransition(opacity: animation, child: child),
                ),
                child: _buildResultCard(context),
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard(BuildContext context) {
    if (_error != null) {
      return Card(
        key: ValueKey(_error),
        color: Theme.of(context).colorScheme.errorContainer,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.error_outline, color: Theme.of(context).colorScheme.onErrorContainer),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  _error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.onErrorContainer),
                ),
              ),
            ],
          ),
        ),
      );
    }
    if (_result != null) {
      return Card(
        key: ValueKey(_result),
        color: Theme.of(context).colorScheme.primaryContainer,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Predicted daily milk yield',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                '${_result!.toStringAsFixed(2)} L',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ],
          ),
        ),
      );
    }
    return const SizedBox.shrink();
  }

  Widget _buildSection(BuildContext context, String title, List<NumericFieldSpec> specs) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Text(title, style: Theme.of(context).textTheme.titleMedium),
          ),
          ...specs.map((spec) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: TextFormField(
                  controller: _numericControllers[spec.key],
                  keyboardType: TextInputType.numberWithOptions(decimal: !spec.isInt, signed: spec.min < 0),
                  decoration: InputDecoration(
                    labelText: spec.label,
                    suffixText: spec.unit.isEmpty ? null : spec.unit,
                    helperText: 'Range: ${_fmt(spec.min)} – ${_fmt(spec.max)}',
                    border: const OutlineInputBorder(),
                  ),
                  validator: (value) => _validateNumeric(value, spec),
                ),
              )),
        ],
      ),
    );
  }

  String _fmt(double v) => v == v.roundToDouble() ? v.toInt().toString() : v.toString();

  String? _validateNumeric(String? value, NumericFieldSpec spec) {
    if (value == null || value.trim().isEmpty) return 'Required';
    final parsed = num.tryParse(value);
    if (parsed == null) return 'Enter a valid number';
    if (spec.isInt && parsed != parsed.roundToDouble()) return 'Enter a whole number';
    if (parsed < spec.min || parsed > spec.max) {
      return 'Must be between ${_fmt(spec.min)} and ${_fmt(spec.max)}';
    }
    return null;
  }

  Widget _buildVaccineSection(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Text('Vaccinations', style: Theme.of(context).textTheme.titleMedium),
          ),
          ...vaccineFields.map((spec) => SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(spec.label),
                value: _vaccineValues[spec.key]!,
                onChanged: (value) => setState(() => _vaccineValues[spec.key] = value),
              )),
        ],
      ),
    );
  }

  Widget _buildCategoricalSection(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Text('Farm context', style: Theme.of(context).textTheme.titleMedium),
          ),
          ...categoricalFields.map((spec) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: DropdownButtonFormField<String>(
                  initialValue: _categoricalValues[spec.key],
                  decoration: InputDecoration(
                    labelText: spec.label,
                    border: const OutlineInputBorder(),
                  ),
                  items: spec.options
                      .map((o) => DropdownMenuItem(value: o, child: Text(o.replaceAll('_', ' '))))
                      .toList(),
                  onChanged: (value) {
                    if (value != null) setState(() => _categoricalValues[spec.key] = value);
                  },
                  isExpanded: true,
                ),
              )),
        ],
      ),
    );
  }
}
