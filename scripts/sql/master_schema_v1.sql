-- =========================================================
-- FreshKeeper – Master schema (Phases 1 → 14)
-- (idempotent; safe to re-run)
-- =========================================================
SET lock_timeout = '5s';
SET statement_timeout = '180s';

BEGIN;

-- 0) Utilities ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1) PRODUCTS & CATEGORIES ---------------------------------------------------
CREATE TABLE IF NOT EXISTS product_categories (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

ALTER TABLE products
  ADD COLUMN IF NOT EXISTS category_id   INTEGER REFERENCES product_categories(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS default_unit  TEXT,
  ADD COLUMN IF NOT EXISTS is_active     BOOLEAN NOT NULL DEFAULT TRUE;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='products' AND column_name='name_normalized'
  ) THEN
    ALTER TABLE products
      ADD COLUMN name_normalized TEXT GENERATED ALWAYS AS (lower(name)) STORED;
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='uq_products_name_norm') THEN
    CREATE UNIQUE INDEX uq_products_name_norm ON products (name_normalized);
  END IF;
END$$;

-- 2) STORAGE LOCATIONS -------------------------------------------------------
CREATE TABLE IF NOT EXISTS storage_locations (
  id        SERIAL PRIMARY KEY,
  name      TEXT NOT NULL,
  kind      TEXT NOT NULL,  -- fridge|freezer|pantry|other
  parent_id INTEGER NULL REFERENCES storage_locations(id) ON DELETE SET NULL
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='ix_storage_locations_kind_name') THEN
    CREATE UNIQUE INDEX ix_storage_locations_kind_name ON storage_locations(kind, name);
  END IF;
END$$;

INSERT INTO storage_locations(name, kind) VALUES
  ('Frigo','fridge'),
  ('Congélateur','freezer'),
  ('Placard 1','pantry')
ON CONFLICT DO NOTHING;

-- 3) LOTS (stock per DLU & location) ----------------------------------------
CREATE TABLE IF NOT EXISTS lots (
  id SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  quantity NUMERIC(12,3) NOT NULL DEFAULT 0,
  unit TEXT NULL,
  expiry_date DATE NULL,
  storage_location_id INTEGER NOT NULL REFERENCES storage_locations(id) ON DELETE RESTRICT,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_lots_updated_at') THEN
    CREATE TRIGGER trg_lots_updated_at
    BEFORE UPDATE ON lots
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='uq_lots_product_expiry_storage_unit') THEN
    CREATE UNIQUE INDEX uq_lots_product_expiry_storage_unit
      ON lots (product_id, expiry_date, storage_location_id, (COALESCE(unit,'')));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='ix_lots_product') THEN
    CREATE INDEX ix_lots_product ON lots(product_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='ix_lots_expiry') THEN
    CREATE INDEX ix_lots_expiry ON lots(expiry_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='ix_lots_storage') THEN
    CREATE INDEX ix_lots_storage ON lots(storage_location_id);
  END IF;
END$$;

-- 4) ALERTS (link to lot when relevant) -------------------------------------
ALTER TABLE alerts
  ADD COLUMN IF NOT EXISTS lot_id INTEGER NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_name='fk_alerts_lot'
  ) THEN
    ALTER TABLE alerts
      ADD CONSTRAINT fk_alerts_lot
      FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL;
  END IF;
END$$;

-- 5) SHOPPING (AA -> BB -> CC) ----------------------------------------------
CREATE TABLE IF NOT EXISTS shopping_lists (
  id SERIAL PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'open', -- open|done
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS shopping_list_items (
  id SERIAL PRIMARY KEY,
  list_id INTEGER NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  requested_qty NUMERIC(12,3) NOT NULL DEFAULT 0,
  unit TEXT NULL,
  status TEXT NOT NULL DEFAULT 'pending', -- pending|bought|assigned
  assigned_storage_location_id INTEGER NULL REFERENCES storage_locations(id) ON DELETE SET NULL
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='ix_shopping_items_list') THEN
    CREATE INDEX ix_shopping_items_list ON shopping_list_items(list_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='ix_shopping_items_product') THEN
    CREATE INDEX ix_shopping_items_product ON shopping_list_items(product_id);
  END IF;
END$$;

-- 6) STOCK EVENTS (journal) --------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_events (
  id SERIAL PRIMARY KEY,
  lot_id INTEGER NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,      -- consume|expire|move|adjust
  qty NUMERIC(12,3) NOT NULL,
  note TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_stock_events_lot ON stock_events(lot_id);
CREATE INDEX IF NOT EXISTS ix_stock_events_type ON stock_events(event_type);

-- 7) API TOKENS --------------------------------------------------------------
CREATE TABLE IF NOT EXISTS api_tokens (
  id SERIAL PRIMARY KEY,
  token TEXT NOT NULL UNIQUE,
  label TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  expires_at TIMESTAMP NULL,
  is_revoked BOOLEAN NOT NULL DEFAULT FALSE
);

-- 8) THRESHOLDS & VIEWS ------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_thresholds (
  product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
  min_qty NUMERIC(12,3) NOT NULL DEFAULT 0,
  unit TEXT NULL,
  days_of_cover INTEGER NULL
);

CREATE OR REPLACE VIEW v_inventory_by_product AS
SELECT
  p.id AS product_id,
  p.name,
  SUM(l.quantity) AS total_qty,
  MIN(l.expiry_date) AS nearest_expiry
FROM products p
LEFT JOIN lots l ON l.product_id = p.id
GROUP BY p.id, p.name;

CREATE OR REPLACE VIEW v_lot_status AS
SELECT
  l.*,
  CASE
    WHEN l.expiry_date IS NULL THEN 'green'
    WHEN l.expiry_date < CURRENT_DATE THEN 'red'
    WHEN l.expiry_date <= CURRENT_DATE + INTERVAL '3 days' THEN 'yellow'
    ELSE 'green'
  END AS status_color
FROM lots l;

DROP MATERIALIZED VIEW IF EXISTS mv_suggested_purchases;
CREATE MATERIALIZED VIEW mv_suggested_purchases AS
SELECT
  p.id AS product_id,
  p.name,
  COALESCE(pt.min_qty,0) AS min_qty,
  COALESCE(v.total_qty,0) AS current_qty,
  GREATEST(COALESCE(pt.min_qty,0) - COALESCE(v.total_qty,0), 0) AS suggested_qty
FROM products p
LEFT JOIN product_thresholds pt ON pt.product_id = p.id
LEFT JOIN v_inventory_by_product v ON v.product_id = p.id;

-- 9) BACKFILL products -> lots ----------------------------------------------
INSERT INTO lots (product_id, quantity, unit, expiry_date, storage_location_id)
SELECT
  p.id,
  COALESCE(p.quantity,0)::NUMERIC(12,3),
  NULL,
  p.expiry_date,
  sl.id
FROM products p
JOIN storage_locations sl
  ON sl.kind = CASE
    WHEN lower(p.location) = 'freezer' THEN 'freezer'
    WHEN lower(p.location) = 'pantry'  THEN 'pantry'
    ELSE 'fridge'
  END
WHERE NOT EXISTS (SELECT 1 FROM lots l WHERE l.product_id = p.id);

COMMIT;
