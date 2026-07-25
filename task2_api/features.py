"""
Feature definitions shared by the prediction schema and the retraining pipeline.

These lists and category values come straight from the feature engineering
section of task1_regression_analysis/multivariate.ipynb (the "Dropping Columns",
"Encoding Categorical Variables" and "Standardization" cells). Keeping them here
as a single source of truth means main.py (validation) and train_utils.py
(retraining) can never drift apart on what a "cow record" looks like.
"""

NUMERIC_FEATURES = [
    "Age_Months",
    "Weight_kg",
    "Parity",
    "Days_in_Milk",
    "Feed_Quantity_kg",
    "Feeding_Frequency",
    "Water_Intake_L",
    "Walking_Distance_km",
    "Grazing_Duration_hrs",
    "Rumination_Time_hrs",
    "Resting_Hours",
    "Ambient_Temperature_C",
    "Humidity_percent",
    "Housing_Score",
    "FMD_Vaccine",
    "Brucellosis_Vaccine",
    "HS_Vaccine",
    "BQ_Vaccine",
    "Anthrax_Vaccine",
    "IBR_Vaccine",
    "BVD_Vaccine",
    "Rabies_Vaccine",
    "Previous_Week_Avg_Yield",
    "Body_Condition_Score",
    "Milking_Interval_hrs",
]

CATEGORICAL_FEATURES = [
    "Breed",
    "Climate_Zone",
    "Management_System",
    "Lactation_Stage",
    "Feed_Type",
    "Season",
]

TARGET = "Milk_Yield_L"

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Exact category values seen in the training data (df_clean[col].unique()).
# Used both for Pydantic Literal validation in schemas.py and for sanity-checking
# uploaded retrain data.
BREED_CATEGORIES = [
    "Africander", "Ankole", "Australian_Friesian_Sahiwal", "Australian_Milking_Zebu",
    "Ayrshire", "Boran", "Brown_Swiss", "Butana", "Danish_Red", "Deoni",
    "Exotic_Local_Cross", "Fleckvieh", "Gangatiri", "Gir", "Girolando", "Guernsey",
    "Hariana", "Holstein-Friesian", "Holstein_Zebu_Cross", "Illawarra_Shorthorn",
    "Jersey", "Jersey_Zebu_Cross", "Kankrej", "Kenana", "Krishna_Valley",
    "Milking_Shorthorn", "Montbeliarde", "NDama", "Normande", "Norwegian_Red",
    "Ongole", "Rathi", "Red_Poll_Africa", "Red_Sindhi", "Sahiwal", "Simmental",
    "Tharparkar", "Tipo_Carora", "White_Fulani", "Zebu_Cross_Brazil",
]

CLIMATE_ZONE_CATEGORIES = [
    "Arid", "Continental", "Mediterranean", "Subtropical", "Temperate", "Tropical",
]

MANAGEMENT_SYSTEM_CATEGORIES = [
    "Extensive", "Intensive", "Mixed", "Pastoral", "Semi_Intensive",
]

LACTATION_STAGE_CATEGORIES = ["Early", "Late", "Mid"]

FEED_TYPE_CATEGORIES = [
    "Concentrates", "Crop_Residues", "Dry_Fodder", "Green_Fodder", "Hay",
    "Mixed_Feed", "Pasture_Grass", "Silage",
]

SEASON_CATEGORIES = ["Autumn", "Monsoon", "Spring", "Summer", "Winter"]
