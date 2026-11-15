-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 12, 2026 at 03:05 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rental_management_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `app_settings`
--

CREATE TABLE `app_settings` (
  `setting_key` varchar(80) NOT NULL,
  `setting_value` text NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `app_settings`
--

INSERT INTO `app_settings` (`setting_key`, `setting_value`, `updated_at`) VALUES
('backup_reminder', '0', '2026-10-12 06:51:35'),
('company_name', 'BIGGIE Rentals', '2026-10-12 07:05:28'),
('currency', 'UGX', '2026-10-12 06:51:35'),
('email', 'manager@example.com', '2026-10-12 06:51:35'),
('email_reminders', '1', '2026-10-12 06:51:35'),
('late_fee', '50000', '2026-10-12 06:51:35'),
('manager_name', 'Property Manager', '2026-10-12 06:51:35'),
('phone', '+256 700 000 000', '2026-10-12 06:51:35'),
('rent_due_day', '5', '2026-10-12 06:51:35'),
('sms_reminders', '1', '2026-10-12 06:51:35'),
('theme', 'Light', '2026-10-12 07:05:03'),
('two_factor_login', 'Not enabled', '2026-10-12 06:51:35');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `payment_date` date NOT NULL,
  `payment_method` varchar(40) NOT NULL,
  `reference_no` varchar(80) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `balance` decimal(12,2) NOT NULL DEFAULT 0.00,
  `status` varchar(30) NOT NULL DEFAULT 'Paid',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`payment_id`, `tenant_id`, `amount`, `payment_date`, `payment_method`, `reference_no`, `notes`, `balance`, `status`, `created_at`) VALUES
(1, 1, 650000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00001', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(2, 2, 650000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00002', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(3, 3, 475000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00003', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 475000.00, 'Pending', '2026-11-05 12:01:16'),
(4, 4, 0.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00004', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 950000.00, 'Overdue', '2026-11-05 12:01:16'),
(5, 5, 1200000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00005', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(6, 6, 1200000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00006', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(7, 7, 375000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00007', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 375000.00, 'Pending', '2026-11-05 12:01:16'),
(8, 8, 0.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00008', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 750000.00, 'Overdue', '2026-11-05 12:01:16'),
(9, 9, 1100000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00009', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(10, 10, 1100000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00010', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(11, 11, 425000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00011', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 425000.00, 'Pending', '2026-11-05 12:01:16'),
(12, 12, 0.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00012', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 850000.00, 'Overdue', '2026-11-05 12:01:16'),
(13, 13, 550000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00013', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(14, 14, 550000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00014', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(15, 15, 450000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00015', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 450000.00, 'Pending', '2026-11-05 12:01:16'),
(16, 16, 0.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00016', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 900000.00, 'Overdue', '2026-11-05 12:01:16'),
(17, 17, 500000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00017', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(18, 18, 500000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00018', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(19, 19, 300000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00019', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 300000.00, 'Pending', '2026-11-05 12:01:16'),
(20, 20, 0.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00020', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 600000.00, 'Overdue', '2026-11-05 12:01:16'),
(21, 21, 800000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00021', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(22, 22, 800000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00022', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(23, 23, 225000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00023', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 225000.00, 'Pending', '2026-11-05 12:01:16'),
(24, 24, 0.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00024', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 450000.00, 'Overdue', '2026-11-05 12:01:16'),
(25, 25, 1400000.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00025', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(26, 26, 1400000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00026', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(27, 27, 200000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00027', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 200000.00, 'Pending', '2026-11-05 12:01:16'),
(28, 28, 0.00, '2026-11-05', 'Mobile Money', 'SAMPLE-202611-00028', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 400000.00, 'Overdue', '2026-11-05 12:01:16'),
(29, 29, 550000.00, '2026-11-05', 'Bank Transfer', 'SAMPLE-202611-00029', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16'),
(30, 30, 550000.00, '2026-11-05', 'Cash', 'SAMPLE-202611-00030', 'Fictional sample rental data (November 2026). November rent demonstration; no real money received.', 0.00, 'Paid', '2026-11-05 12:01:16');

-- --------------------------------------------------------

--
-- Table structure for table `properties`
--

CREATE TABLE `properties` (
  `property_id` int(11) NOT NULL,
  `property_name` varchar(120) NOT NULL,
  `location` varchar(120) NOT NULL,
  `total_units` int(11) NOT NULL DEFAULT 0,
  `monthly_rent` decimal(12,2) NOT NULL DEFAULT 0.00,
  `status` varchar(30) NOT NULL DEFAULT 'Active',
  `extra_details` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `properties`
--

INSERT INTO `properties` (`property_id`, `property_name`, `location`, `total_units`, `monthly_rent`, `status`, `extra_details`, `created_at`) VALUES
(1, 'Rocky Estates', 'Kampala', 20, 1200000.00, 'Active', NULL, '2026-10-12 06:51:35'),
(2, 'Entebbe Apartment', 'Entebbe', 10, 500000.00, 'Active', NULL, '2026-10-12 06:51:35'),
(3, 'Kampala Flats', 'Kampala', 12, 850000.00, 'Active', NULL, '2026-10-12 06:51:35'),
(4, 'Kisaasi Palm Court', 'Kisaasi, Kampala', 8, 650000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom apartments; gated compound, water tanks and parking.', '2026-11-03 07:31:05'),
(5, 'Naalya Green Apartments', 'Naalya, Wakiso', 12, 950000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom apartments with balconies, security and separate electricity meters.', '2026-11-03 07:31:05'),
(6, 'Ntinda View Residences', 'Ntinda, Kampala', 6, 1200000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom apartments; paved parking and an on-site caretaker.', '2026-11-03 07:31:05'),
(7, 'Kira Garden Homes', 'Kira, Wakiso', 10, 750000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom homes with shared gardens and individual water meters.', '2026-11-03 07:31:05'),
(8, 'Najjera Heights', 'Najjera, Wakiso', 8, 1100000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom apartments; secure gate, balconies and covered laundry space.', '2026-11-03 07:31:05'),
(9, 'Kyanja Olive Court', 'Kyanja, Kampala', 6, 850000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom apartments with fitted kitchens and backup water storage.', '2026-11-03 07:31:05'),
(10, 'Makindye Hill Flats', 'Makindye, Kampala', 10, 550000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom flats near public transport; fenced compound and caretaker.', '2026-11-03 07:31:05'),
(11, 'Entebbe Lakeview Court', 'Katabi, Entebbe', 8, 900000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom apartments with shared green space and resident parking.', '2026-11-03 07:31:05'),
(12, 'Mbarara Acacia Homes', 'Nyamitanga, Mbarara', 6, 500000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom homes; tiled floors, water tanks and secure perimeter fence.', '2026-11-03 07:31:05'),
(13, 'Jinja Riverside Apartments', 'Walukuba, Jinja', 8, 600000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom apartments with separate meters and shared courtyard.', '2026-11-03 07:31:05'),
(14, 'Bukoto Cedar Apartments', 'Bukoto, Kampala', 8, 800000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom apartments with parking and shared water storage.', '2026-11-05 12:01:16'),
(15, 'Mukono Sunrise Court', 'Seeta, Mukono', 10, 450000.00, 'Active', 'Fictional sample rental data (November 2026). Self-contained homes near public transport with individual meters.', '2026-11-05 12:01:16'),
(16, 'Lubowa Terrace Homes', 'Lubowa, Wakiso', 6, 1400000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom homes with private verandas and resident parking.', '2026-11-05 12:01:16'),
(17, 'Gulu Mango Court', 'Pece, Gulu', 8, 400000.00, 'Active', 'Fictional sample rental data (November 2026). One-bedroom homes around a shared courtyard with secure fencing.', '2026-11-05 12:01:16'),
(18, 'Fort Portal Hillview', 'Kagote, Fort Portal', 6, 550000.00, 'Active', 'Fictional sample rental data (November 2026). Two-bedroom flats with balconies and separate utility meters.', '2026-11-05 12:01:16');

-- --------------------------------------------------------

--
-- Table structure for table `tenants`
--

CREATE TABLE `tenants` (
  `tenant_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `tenant_name` varchar(120) NOT NULL,
  `phone` varchar(40) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `unit_number` varchar(40) NOT NULL,
  `lease_start` date DEFAULT NULL,
  `monthly_rent` decimal(12,2) NOT NULL DEFAULT 0.00,
  `emergency_contact` varchar(120) DEFAULT NULL,
  `status` varchar(30) NOT NULL DEFAULT 'Active',
  `kyc_image_path` varchar(500) DEFAULT NULL,
  `lc1_letter_path` varchar(500) DEFAULT NULL,
  `extra_details` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tenants`
--

INSERT INTO `tenants` (`tenant_id`, `property_id`, `tenant_name`, `phone`, `email`, `unit_number`, `lease_start`, `monthly_rent`, `emergency_contact`, `status`, `kyc_image_path`, `lc1_letter_path`, `extra_details`, `created_at`) VALUES
(1, 4, 'Amina Nansubuga', '+256 770 900 001', 'amina.nansubuga@example.com', 'A01', '2026-03-01', 650000.00, 'Rose Namusoke (sibling), +256 770 901 001', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 650,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(2, 4, 'David Ssekandi', '+256 770 900 002', 'david.ssekandi@example.com', 'A02', '2026-03-01', 650000.00, 'James Mukasa (sibling), +256 770 901 002', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 650,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(3, 5, 'Grace Nakato', '+256 770 900 003', 'grace.nakato@example.com', 'A01', '2026-04-01', 950000.00, 'Rose Namusoke (sibling), +256 770 901 003', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 950,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(4, 5, 'Brian Mugisha', '+256 770 900 004', 'brian.mugisha@example.com', 'A02', '2026-04-01', 950000.00, 'James Mukasa (sibling), +256 770 901 004', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 950,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(5, 6, 'Sarah Namutebi', '+256 770 900 005', 'sarah.namutebi@example.com', 'A01', '2026-05-01', 1200000.00, 'Rose Namusoke (sibling), +256 770 901 005', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 1,200,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(6, 6, 'Daniel Okello', '+256 770 900 006', 'daniel.okello@example.com', 'A02', '2026-05-01', 1200000.00, 'James Mukasa (sibling), +256 770 901 006', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 1,200,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(7, 7, 'Esther Akello', '+256 770 900 007', 'esther.akello@example.com', 'A01', '2026-06-01', 750000.00, 'Rose Namusoke (sibling), +256 770 901 007', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 750,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(8, 7, 'Michael Kato', '+256 770 900 008', 'michael.kato@example.com', 'A02', '2026-06-01', 750000.00, 'James Mukasa (sibling), +256 770 901 008', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 750,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(9, 8, 'Patricia Nabirye', '+256 770 900 009', 'patricia.nabirye@example.com', 'A01', '2026-07-01', 1100000.00, 'Rose Namusoke (sibling), +256 770 901 009', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 1,100,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(10, 8, 'Joseph Tumusiime', '+256 770 900 010', 'joseph.tumusiime@example.com', 'A02', '2026-07-01', 1100000.00, 'James Mukasa (sibling), +256 770 901 010', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 1,100,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(11, 9, 'Rebecca Achieng', '+256 770 900 011', 'rebecca.achieng@example.com', 'A01', '2026-08-01', 850000.00, 'Rose Namusoke (sibling), +256 770 901 011', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 850,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(12, 9, 'Samuel Wasswa', '+256 770 900 012', 'samuel.wasswa@example.com', 'A02', '2026-08-01', 850000.00, 'James Mukasa (sibling), +256 770 901 012', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 850,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(13, 10, 'Florence Nakiwala', '+256 770 900 013', 'florence.nakiwala@example.com', 'A01', '2026-09-01', 550000.00, 'Rose Namusoke (sibling), +256 770 901 013', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 550,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(14, 10, 'Peter Ssentongo', '+256 770 900 014', 'peter.ssentongo@example.com', 'A02', '2026-09-01', 550000.00, 'James Mukasa (sibling), +256 770 901 014', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 550,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(15, 11, 'Lydia Atim', '+256 770 900 015', 'lydia.atim@example.com', 'A01', '2026-03-01', 900000.00, 'Rose Namusoke (sibling), +256 770 901 015', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 900,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(16, 11, 'Emmanuel Ssemanda', '+256 770 900 016', 'emmanuel.ssemanda@example.com', 'A02', '2026-03-01', 900000.00, 'James Mukasa (sibling), +256 770 901 016', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 900,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(17, 12, 'Doreen Asiimwe', '+256 770 900 017', 'doreen.asiimwe@example.com', 'A01', '2026-04-01', 500000.00, 'Rose Namusoke (sibling), +256 770 901 017', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 500,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(18, 12, 'Andrew Byaruhanga', '+256 770 900 018', 'andrew.byaruhanga@example.com', 'A02', '2026-04-01', 500000.00, 'James Mukasa (sibling), +256 770 901 018', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 500,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(19, 13, 'Harriet Naigaga', '+256 770 900 019', 'harriet.naigaga@example.com', 'A01', '2026-05-01', 600000.00, 'Rose Namusoke (sibling), +256 770 901 019', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 600,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(20, 13, 'Patrick Waiswa', '+256 770 900 020', 'patrick.waiswa@example.com', 'A02', '2026-05-01', 600000.00, 'James Mukasa (sibling), +256 770 901 020', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 600,000. No identity documents supplied.', '2026-11-03 07:31:05'),
(21, 14, 'Agnes Nankya', '+256 770 900 021', 'agnes.nankya@example.com', 'A01', '2026-06-01', 800000.00, 'Rose Namusoke (sibling), +256 770 901 021', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 800,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(22, 14, 'Francis Lubega', '+256 770 900 022', 'francis.lubega@example.com', 'A02', '2026-06-01', 800000.00, 'James Mukasa (sibling), +256 770 901 022', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 800,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(23, 15, 'Christine Namirembe', '+256 770 900 023', 'christine.namirembe@example.com', 'A01', '2026-07-01', 450000.00, 'Rose Namusoke (sibling), +256 770 901 023', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 450,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(24, 15, 'Robert Kirya', '+256 770 900 024', 'robert.kirya@example.com', 'A02', '2026-07-01', 450000.00, 'James Mukasa (sibling), +256 770 901 024', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 450,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(25, 16, 'Irene Nambassa', '+256 770 900 025', 'irene.nambassa@example.com', 'A01', '2026-08-01', 1400000.00, 'Rose Namusoke (sibling), +256 770 901 025', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 1,400,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(26, 16, 'Henry Ssewankambo', '+256 770 900 026', 'henry.ssewankambo@example.com', 'A02', '2026-08-01', 1400000.00, 'James Mukasa (sibling), +256 770 901 026', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 1,400,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(27, 17, 'Beatrice Auma', '+256 770 900 027', 'beatrice.auma@example.com', 'A01', '2026-09-01', 400000.00, 'Rose Namusoke (sibling), +256 770 901 027', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 400,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(28, 17, 'George Ocen', '+256 770 900 028', 'george.ocen@example.com', 'A02', '2026-09-01', 400000.00, 'James Mukasa (sibling), +256 770 901 028', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 400,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(29, 18, 'Juliet Kabonesa', '+256 770 900 029', 'juliet.kabonesa@example.com', 'A01', '2026-03-01', 550000.00, 'Rose Namusoke (sibling), +256 770 901 029', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 550,000. No identity documents supplied.', '2026-11-05 12:01:16'),
(30, 18, 'Vincent Amooti', '+256 770 900 030', 'vincent.amooti@example.com', 'A02', '2026-03-01', 550000.00, 'James Mukasa (sibling), +256 770 901 030', 'Active', NULL, NULL, 'Fictional sample rental data (November 2026). Contact numbers are placeholders. Rent payable monthly by the 5th; refundable security deposit UGX 550,000. No identity documents supplied.', '2026-11-05 12:01:16');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(30) NOT NULL DEFAULT 'Admin',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`, `role`, `created_at`) VALUES
(1, 'eric', '12345', 'Admin', '2026-10-12 06:51:35');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `app_settings`
--
ALTER TABLE `app_settings`
  ADD PRIMARY KEY (`setting_key`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD UNIQUE KEY `reference_no` (`reference_no`),
  ADD KEY `fk_payments_tenant` (`tenant_id`);

--
-- Indexes for table `properties`
--
ALTER TABLE `properties`
  ADD PRIMARY KEY (`property_id`);

--
-- Indexes for table `tenants`
--
ALTER TABLE `tenants`
  ADD PRIMARY KEY (`tenant_id`),
  ADD UNIQUE KEY `phone` (`phone`),
  ADD KEY `fk_tenants_property` (`property_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `properties`
--
ALTER TABLE `properties`
  MODIFY `property_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `tenants`
--
ALTER TABLE `tenants`
  MODIFY `tenant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `fk_payments_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`) ON UPDATE CASCADE;

--
-- Constraints for table `tenants`
--
ALTER TABLE `tenants`
  ADD CONSTRAINT `fk_tenants_property` FOREIGN KEY (`property_id`) REFERENCES `properties` (`property_id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
