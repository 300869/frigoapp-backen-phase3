BEGIN;
DROP INDEX IF EXISTS uq_lots_product_expiry_storage_unit;
ALTER TABLE lots
  ADD COLUMN IF NOT EXISTS unit_norm TEXT GENERATED ALWAYS AS (COALESCE(unit,'')) STORED;
CREATE UNIQUE INDEX IF NOT EXISTS uq_lots_key
  ON lots (product_id, expiry_date, storage_location_id, unit_norm);
COMMIT;
