-- Prepare only. Run against staging only after explicit migration approval.
BEGIN;
CREATE TABLE IF NOT EXISTS public.parameter_label_registry (
    parameter_key TEXT PRIMARY KEY,
    prefix TEXT NOT NULL CHECK (prefix IN ('P', 'IP')),
    label_number BIGINT NOT NULL CHECK (label_number > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (prefix, label_number)
);
COMMIT;
