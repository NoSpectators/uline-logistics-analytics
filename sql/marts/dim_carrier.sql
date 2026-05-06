DROP TABLE IF EXISTS dim_carrier;

CREATE TABLE dim_carrier AS
SELECT DISTINCT
    carrier
FROM shipments;