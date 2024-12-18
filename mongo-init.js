db = db.getSiblingDB('StravaChallangeV2Db');


// Create collections
db.createCollection('athletes');
db.createCollection('activities');
db.createCollection('yearlyStats');

// Create unique indexes
db.athletes.createIndex({ "athlete_id": 1 }, { unique: true });
db.activities.createIndex({ "activity_id": 1 }, { unique: true });

// Create indexes
db.yearlyStats.createIndex({ "athlete_id": 1, "year": 1 });
db.activities.createIndex({ "athlete_id": 1, "type": 1, "year": 1 });
db.activities.createIndex({ "athlete_id": 1, "year": 1, "summary_polyline": 1 });
db.activities.createIndex({ "summary_polyline": "2dsphere" });

// Note: The _id index is created automatically by MongoDB for each collection
