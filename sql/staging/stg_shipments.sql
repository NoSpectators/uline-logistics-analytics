DROP TABLE IF EXISTS stg_shipments;

CREATE TABLE stg_shipments AS
SELECT
    s.shipment_id,
    s.order_id,
    s.carrier,
    DATE(s.ship_date) AS ship_date,
    DATE(s.delivery_date) AS delivery_date,
    s.status
FROM shipments s;