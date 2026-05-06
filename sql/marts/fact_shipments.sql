DROP TABLE IF EXISTS fact_shipments;

CREATE TABLE fact_shipments AS
SELECT
    o.order_id,
    o.order_date,
    o.warehouse_id,
    o.total_weight,

    s.shipment_id,
    s.carrier,
    s.ship_date,
    s.delivery_date,
    s.status,

    JULIANDAY(s.delivery_date) - JULIANDAY(s.ship_date) AS delivery_days

FROM orders o
JOIN stg_shipments s
    ON o.order_id = s.order_id;