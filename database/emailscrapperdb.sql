-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 19, 2023 at 04:20 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `emailscrapperdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `action`
--

CREATE TABLE `action` (
  `ACTION_ID` int(11) NOT NULL,
  `USER_ID` int(11) NOT NULL,
  `ACTION_DATE` char(10) NOT NULL,
  `ACTION_TIME` char(5) NOT NULL,
  `ACTION_RESULT` varchar(100) DEFAULT NULL,
  `ACTION_INPUT` varchar(1000) NOT NULL,
  `ACTION_INPUT_TYPE` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `action`
--

INSERT INTO `action` (`ACTION_ID`, `USER_ID`, `ACTION_DATE`, `ACTION_TIME`, `ACTION_RESULT`, `ACTION_INPUT`, `ACTION_INPUT_TYPE`) VALUES
(11, 1, '19-07-2023', '02:35', 'www.birmingham.ac.uk11.xlsx', 'https://www.birmingham.ac.uk/schools/education/staff/index.aspx', 'mono_link'),
(13, 1, '19-07-2023', '02:38', 'www.ed.ac.uk13.xlsx', 'https://www.ed.ac.uk/education/about-us/people/academic-staff-a-z', 'mono_link'),
(14, 1, '19-07-2023', '03:04', 'www.gse.harvard.edu14.xlsx', 'https://www.gse.harvard.edu/directory\r\nhttp://www.narg.org.uk/people-and-partners/staff-directory/', 'bulk_text'),
(15, 1, '19-07-2023', '03:13', 'www.birmingham.ac.uk15.xlsx', 'https://www.birmingham.ac.uk/research/metabolism-systems/staff/a-z-staff-list.aspx\r\nhttps://www.birmingham.ac.uk/schools/education/staff/index.aspx\r\nhttps://www.ed.ac.uk/education/about-us/people/academic-staff-a-z', 'bulk_text');

-- --------------------------------------------------------

--
-- Table structure for table `urls`
--

CREATE TABLE `urls` (
  `URL_ID` int(11) NOT NULL,
  `USER_ID` int(11) NOT NULL,
  `ACTION_ID` int(11) NOT NULL,
  `URL_LINK` varchar(200) NOT NULL,
  `URL_EMAILS` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `urls`
--

INSERT INTO `urls` (`URL_ID`, `USER_ID`, `ACTION_ID`, `URL_LINK`, `URL_EMAILS`) VALUES
(22, 1, 11, 'https://www.birmingham.ac.uk/schools/education/staff/index.aspx', 97),
(25, 1, 13, 'https://www.ed.ac.uk/education/about-us/people/academic-staff-a-z', 241),
(26, 1, 14, 'https://www.gse.harvard.edu/directory', 0),
(27, 1, 14, 'http://www.narg.org.uk/people-and-partners/staff-directory/', 26),
(28, 1, 15, 'https://www.birmingham.ac.uk/research/metabolism-systems/staff/a-z-staff-list.aspx', 106),
(29, 1, 15, 'https://www.birmingham.ac.uk/schools/education/staff/index.aspx', 97),
(30, 1, 15, 'https://www.ed.ac.uk/education/about-us/people/academic-staff-a-z', 241);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `USER_ID` int(11) NOT NULL,
  `USER_NAME` varchar(30) NOT NULL,
  `USER_EMAIL` varchar(60) NOT NULL,
  `USER_PASSWORD` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`USER_ID`, `USER_NAME`, `USER_EMAIL`, `USER_PASSWORD`) VALUES
(1, 'yassine', 'basskar2049@gmail.com', 'pbkdf2:sha256:600000$qvk8eLX9y');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `action`
--
ALTER TABLE `action`
  ADD PRIMARY KEY (`ACTION_ID`),
  ADD KEY `FK_ACTION_AVOIR_USER` (`USER_ID`);

--
-- Indexes for table `urls`
--
ALTER TABLE `urls`
  ADD PRIMARY KEY (`URL_ID`,`USER_ID`,`ACTION_ID`),
  ADD KEY `FK_URLS_CONTENIR_ACTION` (`USER_ID`,`ACTION_ID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`USER_ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `action`
--
ALTER TABLE `action`
  MODIFY `ACTION_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `urls`
--
ALTER TABLE `urls`
  MODIFY `URL_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `USER_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `action`
--
ALTER TABLE `action`
  ADD CONSTRAINT `FK_ACTION_AVOIR_USER` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`USER_ID`),
  ADD CONSTRAINT `action_ibfk_1` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`USER_ID`);

--
-- Constraints for table `urls`
--
ALTER TABLE `urls`
  ADD CONSTRAINT `FK_URLS_CONTENIR_ACTION` FOREIGN KEY (`USER_ID`,`ACTION_ID`) REFERENCES `action` (`USER_ID`, `ACTION_ID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
