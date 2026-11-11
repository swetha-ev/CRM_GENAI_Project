CREATE DATABASE crm_ai;
USE crm_ai;

CREATE TABLE customers(
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    city VARCHAR(50),
    state VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE products(
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE orders(
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)
);

CREATE TABLE order_items(
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    amount DECIMAL(10,2),
    FOREIGN KEY(order_id)
    REFERENCES orders(order_id),
    FOREIGN KEY(product_id)
    REFERENCES products(product_id)
);

CREATE TABLE leads(
    lead_id INT PRIMARY KEY AUTO_INCREMENT,
    lead_name VARCHAR(100),
    source VARCHAR(50),
    status VARCHAR(30),
    assigned_to VARCHAR(50)
);

CREATE TABLE employees(
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_name VARCHAR(100),
    department VARCHAR(50),
    email VARCHAR(100)
);



INSERT INTO customers
(name,email,phone,city,state)
VALUES
('Customer 01','customer01@example.com','0000000001','Kochi','Kerala'),
('Customer 02','customer02@example.com','0000000002','Kochi','Kerala'),
('Customer 03','customer03@example.com','0000000003','Thrissur','Kerala'),
('Customer 04','customer04@example.com','0000000004','Calicut','Kerala'),
('Customer 05','customer05@example.com','0000000005','Bangalore','Karnataka'),
('Customer 06','customer06@example.com','0000000006','Chennai','Tamil Nadu'),
('Customer 07','customer07@example.com','0000000007','Mumbai','Maharashtra'),
('Customer 08','customer08@example.com','0000000008','Delhi','Delhi'),
('Customer 09','customer09@example.com','0000000009','Pune','Maharashtra'),
('Customer 10','customer10@example.com','0000000010','Kochi','Kerala'),
('Customer 11','customer11@example.com','0000000011','Kollam','Kerala'),
('Customer 12','customer12@example.com','0000000012','Kannur','Kerala'),
('Customer 13','customer13@example.com','0000000013','Kochi','Kerala'),
('Customer 14','customer14@example.com','0000000014','Mysore','Karnataka'),
('Customer 15','customer15@example.com','0000000015','Palakkad','Kerala'),
('Customer 16','customer16@example.com','0000000016','Hyderabad','Telangana'),
('Customer 17','customer17@example.com','0000000017','Kochi','Kerala'),
('Customer 18','customer18@example.com','0000000018','Thrissur','Kerala'),
('Customer 19','customer19@example.com','0000000019','Kochi','Kerala'),
('Customer 20','customer20@example.com','0000000020','Trivandrum','Kerala');


INSERT INTO products (product_name, category, price)
VALUES
('Laptop Pro','Electronics',75000),
('Gaming Laptop','Electronics',95000),
('Wireless Mouse','Accessories',1200),
('Mechanical Keyboard','Accessories',3500),
('Monitor 24 Inch','Electronics',12000),
('Monitor 27 Inch','Electronics',18000),
('USB Hub','Accessories',800),
('External SSD','Storage',6500),
('Printer','Office',9000),
('Scanner','Office',7000),
('Tablet','Electronics',25000),
('Smartphone','Electronics',30000),
('Router','Networking',2500),
('Webcam','Accessories',2200),
('Headset','Accessories',1800),
('Projector','Office',35000),
('Power Bank','Accessories',1500),
('Office Chair','Furniture',8500),
('Standing Desk','Furniture',22000),
('NAS Storage','Storage',45000);



INSERT INTO employees
(employee_name,department,email)
VALUES
('Employee 01','Sales','employee01@example.com'),
('Employee 02','Sales','employee02@example.com'),
('Employee 03','Marketing','employee03@example.com'),
('Employee 04','Support','employee04@example.com'),
('Employee 05','IT','employee05@example.com'),
('Employee 06','HR','employee06@example.com'),
('Employee 07','Sales','employee07@example.com'),
('Employee 08','Finance','employee08@example.com'),
('Employee 09','IT','employee09@example.com'),
('Employee 10','Support','employee10@example.com'),
('Employee 11','Marketing','employee11@example.com'),
('Employee 12','HR','employee12@example.com'),
('Employee 13','Sales','employee13@example.com'),
('Employee 14','Support','employee14@example.com'),
('Employee 15','Finance','employee15@example.com'),
('Employee 16','Marketing','employee16@example.com'),
('Employee 17','Sales','employee17@example.com'),
('Employee 18','IT','employee18@example.com'),
('Employee 19','Support','employee19@example.com'),
('Employee 20','Sales','employee20@example.com');


INSERT INTO leads
(lead_name,source,status,assigned_to)
VALUES
('Tech Solutions','Website','New','Employee 01'),
('ABC Retail','LinkedIn','Contacted','Employee 02'),
('Future Systems','Referral','Qualified','Employee 03'),
('Vision Tech','Website','New','Employee 07'),
('Green Energy','Email','Contacted','Employee 17'),
('Blue Ocean','LinkedIn','Lost','Employee 13'),
('Data Minds','Referral','Qualified','Employee 01'),
('Cloud Corp','Website','Won','Employee 02'),
('Quick Mart','Email','New','Employee 03'),
('SoftEdge','LinkedIn','Contacted','Employee 07'),
('NextGen','Referral','Qualified','Employee 17'),
('Prime Tech','Website','Won','Employee 13'),
('Star Retail','Email','Lost','Employee 01'),
('Smart Systems','Website','New','Employee 02'),
('Innovate Ltd','LinkedIn','Contacted','Employee 03'),
('Global Trade','Referral','Qualified','Employee 07'),
('Fast Logistics','Website','Won','Employee 17'),
('SecureNet','Email','Lost','Employee 13'),
('Metro Stores','Website','New','Employee 01'),
('Bright Future','Referral','Qualified','Employee 02');



INSERT INTO orders
(customer_id,order_date,total_amount,status)
VALUES
(1,'2026-06-01',75000,'Completed'),
(2,'2026-06-02',95000,'Completed'),
(3,'2026-06-03',1200,'Completed'),
(4,'2026-06-04',3500,'Pending'),
(5,'2026-06-05',12000,'Completed'),
(6,'2026-06-06',18000,'Completed'),
(7,'2026-06-07',800,'Pending'),
(8,'2026-06-08',6500,'Completed'),
(9,'2026-06-09',9000,'Completed'),
(10,'2026-06-10',7000,'Completed'),
(11,'2026-06-11',25000,'Pending'),
(12,'2026-06-12',30000,'Completed'),
(13,'2026-06-13',2500,'Completed'),
(14,'2026-06-14',2200,'Pending'),
(15,'2026-06-15',1800,'Completed'),
(16,'2026-06-16',35000,'Completed'),
(17,'2026-06-17',1500,'Completed'),
(18,'2026-06-18',8500,'Pending'),
(19,'2026-06-19',22000,'Completed'),
(20,'2026-06-20',45000,'Completed');



INSERT INTO order_items
(order_id,product_id,quantity,amount)
VALUES
(1,1,1,75000),
(2,2,1,95000),
(3,3,1,1200),
(4,4,1,3500),
(5,5,1,12000),
(6,6,1,18000),
(7,7,1,800),
(8,8,1,6500),
(9,9,1,9000),
(10,10,1,7000),
(11,11,1,25000),
(12,12,1,30000),
(13,13,1,2500),
(14,14,1,2200),
(15,15,1,1800),
(16,16,1,35000),
(17,17,1,1500),
(18,18,1,8500),
(19,19,1,22000),
(20,20,1,45000);