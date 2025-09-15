DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name='alerts' AND constraint_name='alerts_kind_whitelist_chk'
  ) THEN
    ALTER TABLE alerts
      ADD CONSTRAINT alerts_kind_whitelist_chk
      CHECK (kind IN ('expiry','soon','out_of_stock'));
  END IF;
END$$;
