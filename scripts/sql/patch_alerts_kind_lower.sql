BEGIN;

-- 0) Détection/Déduplication préalable sur (product_id, due_date, lower(kind))
WITH ranked AS (
  SELECT id,
         ROW_NUMBER() OVER (
           PARTITION BY product_id, due_date, lower(kind)
           ORDER BY
             is_active DESC,
             updated_at DESC NULLS LAST,
             id DESC
         ) AS rn
  FROM alerts
)
DELETE FROM alerts a
USING ranked r
WHERE a.id = r.id AND r.rn > 1;

-- 1) Normaliser toutes les valeurs en minuscule
UPDATE alerts SET kind = lower(kind);

-- 2) Trigger de normalisation pour les écritures futures
CREATE OR REPLACE FUNCTION normalize_alert_kind() RETURNS trigger AS $$
BEGIN
  NEW.kind := lower(NEW.kind);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_alerts_kind_lower ON alerts;
CREATE TRIGGER trg_alerts_kind_lower
BEFORE INSERT OR UPDATE ON alerts
FOR EACH ROW
EXECUTE FUNCTION normalize_alert_kind();

-- 3) Garde-fou: vérifier que kind est toujours en minuscule
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name='alerts' AND constraint_name='alerts_kind_lower_chk'
  ) THEN
    ALTER TABLE alerts
      ADD CONSTRAINT alerts_kind_lower_chk CHECK (kind = lower(kind));
  END IF;
END$$;

COMMIT;
