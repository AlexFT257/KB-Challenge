INSERT INTO products (name, sku, description, current_stock, price)
VALUES
    ('Wireless Mouse', 'TECH-001', 'Ergonomic wireless mouse with USB receiver', 100, 29.99),
    ('Mechanical Keyboard', 'TECH-002', 'RGB mechanical keyboard with Cherry MX switches', 50, 89.99),
    ('USB-C Hub', 'TECH-003', '7-in-1 USB-C hub with HDMI and card reader', 75, 45.99),
    ('Laptop Stand', 'TECH-004', 'Adjustable aluminum laptop stand', 30, 39.99),
    ('Webcam HD', 'TECH-005', '1080p HD webcam with built-in microphone', 45, 59.99),
    ('Monitor 27"', 'TECH-006', '27-inch 4K IPS monitor with USB-C', 20, 399.99),
    ('Desk Lamp LED', 'TECH-007', 'LED desk lamp with adjustable brightness', 60, 24.99),
    ('External SSD 1TB', 'TECH-008', 'Portable 1TB SSD USB 3.2', 40, 89.99),
    ('Wireless Earbuds', 'TECH-009', 'True wireless earbuds with noise cancelling', 85, 79.99),
    ('Cable Management Kit', 'TECH-010', 'Desk cable management kit with clips and ties', 150, 14.99)
ON CONFLICT (sku) DO NOTHING;
