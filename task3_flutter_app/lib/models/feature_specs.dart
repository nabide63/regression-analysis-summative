/// Feature definitions for the cow prediction form.
///
/// Mirrors task2_api/features.py and task2_api/schemas.py (field bounds,
/// category values, and the example record) so the form only ever sends
/// values the API's Pydantic validation will accept.
library;

class NumericFieldSpec {
  final String key;
  final String label;
  final String unit;
  final double min;
  final double max;
  final bool isInt;
  final num defaultValue;

  const NumericFieldSpec({
    required this.key,
    required this.label,
    required this.unit,
    required this.min,
    required this.max,
    required this.isInt,
    required this.defaultValue,
  });
}

class VaccineSpec {
  final String key;
  final String label;
  final bool defaultValue;

  const VaccineSpec({
    required this.key,
    required this.label,
    required this.defaultValue,
  });
}

class CategoricalSpec {
  final String key;
  final String label;
  final List<String> options;
  final String defaultValue;

  const CategoricalSpec({
    required this.key,
    required this.label,
    required this.options,
    required this.defaultValue,
  });
}

const List<NumericFieldSpec> animalProfileFields = [
  NumericFieldSpec(key: 'Age_Months', label: 'Age', unit: 'months', min: 24, max: 143, isInt: true, defaultValue: 48),
  NumericFieldSpec(key: 'Weight_kg', label: 'Weight', unit: 'kg', min: 250, max: 750, isInt: false, defaultValue: 480.0),
  NumericFieldSpec(key: 'Parity', label: 'Parity (times calved)', unit: '', min: 1, max: 6, isInt: true, defaultValue: 3),
  NumericFieldSpec(key: 'Days_in_Milk', label: 'Days in milk', unit: 'days', min: 1, max: 364, isInt: true, defaultValue: 120),
  NumericFieldSpec(key: 'Body_Condition_Score', label: 'Body condition score', unit: '', min: 2.0, max: 5.0, isInt: false, defaultValue: 3.5),
];

const List<NumericFieldSpec> feedingFields = [
  NumericFieldSpec(key: 'Feed_Quantity_kg', label: 'Feed quantity', unit: 'kg/day', min: 3.0, max: 25.0, isInt: false, defaultValue: 14.5),
  NumericFieldSpec(key: 'Feeding_Frequency', label: 'Feeding frequency', unit: 'times/day', min: 1, max: 5, isInt: true, defaultValue: 3),
  NumericFieldSpec(key: 'Water_Intake_L', label: 'Water intake', unit: 'L/day', min: 20.0, max: 120.0, isInt: false, defaultValue: 70.0),
];

const List<NumericFieldSpec> activityFields = [
  NumericFieldSpec(key: 'Walking_Distance_km', label: 'Walking distance', unit: 'km/day', min: 0.5, max: 12.0, isInt: false, defaultValue: 4.0),
  NumericFieldSpec(key: 'Grazing_Duration_hrs', label: 'Grazing duration', unit: 'hrs/day', min: 1.0, max: 14.0, isInt: false, defaultValue: 6.0),
  NumericFieldSpec(key: 'Rumination_Time_hrs', label: 'Rumination time', unit: 'hrs/day', min: 4.0, max: 14.0, isInt: false, defaultValue: 8.0),
  NumericFieldSpec(key: 'Resting_Hours', label: 'Resting hours', unit: 'hrs/day', min: 5.0, max: 18.0, isInt: false, defaultValue: 10.0),
];

const List<NumericFieldSpec> environmentFields = [
  NumericFieldSpec(key: 'Ambient_Temperature_C', label: 'Ambient temperature', unit: '°C', min: -10.0, max: 45.0, isInt: false, defaultValue: 24.0),
  NumericFieldSpec(key: 'Humidity_percent', label: 'Humidity', unit: '%', min: 10.0, max: 100.0, isInt: false, defaultValue: 55.0),
  NumericFieldSpec(key: 'Housing_Score', label: 'Housing quality score', unit: '(0.3-1.0)', min: 0.3, max: 1.0, isInt: false, defaultValue: 0.7),
];

const List<NumericFieldSpec> milkingFields = [
  NumericFieldSpec(key: 'Milking_Interval_hrs', label: 'Milking interval', unit: 'hrs', min: 6, max: 24, isInt: true, defaultValue: 12),
  NumericFieldSpec(key: 'Previous_Week_Avg_Yield', label: 'Previous week avg yield', unit: 'L', min: 0.0, max: 38.67, isInt: false, defaultValue: 9.2),
];

const List<VaccineSpec> vaccineFields = [
  VaccineSpec(key: 'FMD_Vaccine', label: 'Foot-and-mouth disease (FMD)', defaultValue: true),
  VaccineSpec(key: 'Brucellosis_Vaccine', label: 'Brucellosis', defaultValue: true),
  VaccineSpec(key: 'HS_Vaccine', label: 'Haemorrhagic septicaemia (HS)', defaultValue: false),
  VaccineSpec(key: 'BQ_Vaccine', label: 'Black quarter (BQ)', defaultValue: false),
  VaccineSpec(key: 'Anthrax_Vaccine', label: 'Anthrax', defaultValue: true),
  VaccineSpec(key: 'IBR_Vaccine', label: 'Infectious bovine rhinotracheitis (IBR)', defaultValue: false),
  VaccineSpec(key: 'BVD_Vaccine', label: 'Bovine viral diarrhea (BVD)', defaultValue: false),
  VaccineSpec(key: 'Rabies_Vaccine', label: 'Rabies', defaultValue: true),
];

const List<String> breedOptions = [
  'Africander', 'Ankole', 'Australian_Friesian_Sahiwal', 'Australian_Milking_Zebu',
  'Ayrshire', 'Boran', 'Brown_Swiss', 'Butana', 'Danish_Red', 'Deoni',
  'Exotic_Local_Cross', 'Fleckvieh', 'Gangatiri', 'Gir', 'Girolando', 'Guernsey',
  'Hariana', 'Holstein-Friesian', 'Holstein_Zebu_Cross', 'Illawarra_Shorthorn',
  'Jersey', 'Jersey_Zebu_Cross', 'Kankrej', 'Kenana', 'Krishna_Valley',
  'Milking_Shorthorn', 'Montbeliarde', 'NDama', 'Normande', 'Norwegian_Red',
  'Ongole', 'Rathi', 'Red_Poll_Africa', 'Red_Sindhi', 'Sahiwal', 'Simmental',
  'Tharparkar', 'Tipo_Carora', 'White_Fulani', 'Zebu_Cross_Brazil',
];

const List<CategoricalSpec> categoricalFields = [
  CategoricalSpec(key: 'Breed', label: 'Breed', options: breedOptions, defaultValue: 'Holstein-Friesian'),
  CategoricalSpec(
    key: 'Climate_Zone',
    label: 'Climate zone',
    options: ['Arid', 'Continental', 'Mediterranean', 'Subtropical', 'Temperate', 'Tropical'],
    defaultValue: 'Tropical',
  ),
  CategoricalSpec(
    key: 'Management_System',
    label: 'Management system',
    options: ['Extensive', 'Intensive', 'Mixed', 'Pastoral', 'Semi_Intensive'],
    defaultValue: 'Mixed',
  ),
  CategoricalSpec(
    key: 'Lactation_Stage',
    label: 'Lactation stage',
    options: ['Early', 'Mid', 'Late'],
    defaultValue: 'Mid',
  ),
  CategoricalSpec(
    key: 'Feed_Type',
    label: 'Feed type',
    options: [
      'Concentrates', 'Crop_Residues', 'Dry_Fodder', 'Green_Fodder', 'Hay',
      'Mixed_Feed', 'Pasture_Grass', 'Silage',
    ],
    defaultValue: 'Mixed_Feed',
  ),
  CategoricalSpec(
    key: 'Season',
    label: 'Season',
    options: ['Autumn', 'Monsoon', 'Spring', 'Summer', 'Winter'],
    defaultValue: 'Summer',
  ),
];

const List<NumericFieldSpec> allNumericFields = [
  ...animalProfileFields,
  ...feedingFields,
  ...activityFields,
  ...environmentFields,
  ...milkingFields,
];
