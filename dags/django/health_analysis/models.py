from django.db import models

# Model-model ini MENCERMINKAN tabel yang sudah ada di database.
# Django TIDAK akan mengelola skema mereka (membuat, mengubah, menghapus).

class DimPatient(models.Model):
    patientkey = models.AutoField(primary_key=True, db_column='PatientKey')
    sex = models.IntegerField(db_column='Sex')
    class Meta:
        managed = False
        db_table = 'dim_patient'

class DimDemographics(models.Model):
    demographicskey = models.AutoField(primary_key=True, db_column='DemographicsKey')
    age = models.IntegerField(db_column='Age')
    education = models.IntegerField(db_column='Education')
    income = models.IntegerField(db_column='Income')
    class Meta:
        managed = False
        db_table = 'dim_demographics'

class DimBehavior(models.Model):
    behaviorkey = models.AutoField(primary_key=True, db_column='BehaviorKey')
    is_smoker = models.IntegerField(db_column='Smoker')
    has_physactivity = models.IntegerField(db_column='PhysActivity')
    consumes_fruits = models.IntegerField(db_column='Fruits')
    consumes_veggies = models.IntegerField(db_column='Veggies')
    is_hvyalcoholconsumer = models.IntegerField(db_column='HvyAlcoholConsump')
    class Meta:
        managed = False
        db_table = 'dim_behavior'

class DimHealthcare(models.Model):
    healthcarekey = models.AutoField(primary_key=True, db_column='HealthcareKey')
    has_cholcheck_5yrs = models.IntegerField(db_column='CholCheck')
    has_anyhealthcare = models.IntegerField(db_column='AnyHealthcare')
    nodocbccost = models.IntegerField(db_column='NoDocbcCost')
    general_health = models.IntegerField(db_column='GenHlth')
    has_diffwalk = models.IntegerField(db_column='DiffWalk')
    class Meta:
        managed = False
        db_table = 'dim_healthcare'

# --- Tabel Fakta ---

class FactHealthOutcome(models.Model):
    id = models.AutoField(primary_key=True) # Django perlu primary key
    patientkey = models.ForeignKey(DimPatient, on_delete=models.DO_NOTHING, db_column='PatientKey')
    demographicskey = models.ForeignKey(DimDemographics, on_delete=models.DO_NOTHING, db_column='DemographicsKey')
    behaviorkey = models.ForeignKey(DimBehavior, on_delete=models.DO_NOTHING, db_column='BehaviorKey')
    healthcarekey = models.ForeignKey(DimHealthcare, on_delete=models.DO_NOTHING, db_column='HealthcareKey')
    is_diabetes = models.IntegerField(db_column='Is_Diabetes')
    is_prediabetes = models.IntegerField(db_column='Is_Prediabetes')
    has_highbp = models.IntegerField(db_column='Has_HighBP')
    has_highchol = models.IntegerField(db_column='Has_HighChol')
    has_stroke = models.IntegerField(db_column='Has_Stroke')
    has_heartdisease = models.IntegerField(db_column='Has_HeartDisease')
    bmi = models.IntegerField(db_column='BMI')
    menthlth_days = models.IntegerField(db_column='MentHlth_Days')
    physhlth_days = models.IntegerField(db_column='PhysHlth_Days')
    class Meta:
        managed = False
        db_table = 'fact_health_outcome'

class FactPatientSegment(models.Model):
    id = models.AutoField(primary_key=True)
    patientkey = models.ForeignKey(DimPatient, on_delete=models.DO_NOTHING, db_column='PatientKey')
    demographicskey = models.ForeignKey(DimDemographics, on_delete=models.DO_NOTHING, db_column='DemographicsKey')
    behaviorkey = models.ForeignKey(DimBehavior, on_delete=models.DO_NOTHING, db_column='BehaviorKey')
    healthcarekey = models.ForeignKey(DimHealthcare, on_delete=models.DO_NOTHING, db_column='HealthcareKey')
    segmentid = models.IntegerField(db_column='SegmentID')
    class Meta:
        managed = False
        db_table = 'fact_patient_segment'

class FactRiskFactors(models.Model):
    id = models.AutoField(primary_key=True)
    patientkey = models.ForeignKey(DimPatient, on_delete=models.DO_NOTHING, db_column='PatientKey')
    demographicskey = models.ForeignKey(DimDemographics, on_delete=models.DO_NOTHING, db_column='DemographicsKey')
    behaviorkey = models.ForeignKey(DimBehavior, on_delete=models.DO_NOTHING, db_column='BehaviorKey')
    healthcarekey = models.ForeignKey(DimHealthcare, on_delete=models.DO_NOTHING, db_column='HealthcareKey')
    has_highbp = models.IntegerField(db_column='Has_HighBP')
    bmi = models.IntegerField(db_column='BMI')
    class Meta:
        managed = False
        db_table = 'fact_risk_factors'