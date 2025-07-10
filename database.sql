CREATE DATABASE  IF NOT EXISTS `db_project` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `db_project`;
-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: db_project
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class` (
  `class_id` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `college_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`class_id`),
  KEY `college_id` (`college_id`),
  CONSTRAINT `class_ibfk_1` FOREIGN KEY (`college_id`) REFERENCES `college` (`college_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

LOCK TABLES `class` WRITE;
/*!40000 ALTER TABLE `class` DISABLE KEYS */;
INSERT INTO `class` VALUES ('00101','量子信息','001'),('22901','数据科学','229');
/*!40000 ALTER TABLE `class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_headteacher`
--

DROP TABLE IF EXISTS `class_headteacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_headteacher` (
  `class_id` varchar(20) NOT NULL,
  `teacher_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`class_id`),
  UNIQUE KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `class_headteacher_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`) ON DELETE CASCADE,
  CONSTRAINT `class_headteacher_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_headteacher`
--

LOCK TABLES `class_headteacher` WRITE;
/*!40000 ALTER TABLE `class_headteacher` DISABLE KEYS */;
INSERT INTO `class_headteacher` VALUES ('00101','T001');
/*!40000 ALTER TABLE `class_headteacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `college`
--

DROP TABLE IF EXISTS `college`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `college` (
  `college_id` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `contact` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`college_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `college`
--

LOCK TABLES `college` WRITE;
/*!40000 ALTER TABLE `college` DISABLE KEYS */;
INSERT INTO `college` VALUES ('001','物理学院','110'),('002','数学学院','119'),('229','人工智能与数据科学学院','139');
/*!40000 ALTER TABLE `college` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `course_id` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `credit` decimal(3,1) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `time` varchar(100) DEFAULT NULL,
  `maxStudents` int NOT NULL,
  `numStudents` int DEFAULT '0',
  PRIMARY KEY (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES ('MA001','数学分析B1',6.0,'5202','1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18周:1(3,4);3(3,4);5(3,4)',120,2),('PY001','力学A',4.0,'5203','1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18周:1(1,2);3(3,4)',120,0),('PY002','电磁学B',4.0,'2102','1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18周:1(3,4);4(6,7)',100,1),('PY003','近代物理进展',4.0,'5203','1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16周:1(1,2);2(11,12,13)',80,2),('SC001','科学社会与研讨',1.0,'2201','2,6,13周:4(11,12,13)',1,1);
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_account`
--

DROP TABLE IF EXISTS `login_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_account` (
  `id` varchar(50) NOT NULL,
  `password` varchar(1000) NOT NULL,
  `role` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_account`
--

LOCK TABLES `login_account` WRITE;
/*!40000 ALTER TABLE `login_account` DISABLE KEYS */;
INSERT INTO `login_account` VALUES ('A001','scrypt:32768:8:1$9RKcoN65Ao5tdgQW$3f67317774ef7c1a78be9c778606daaaa097f8688c6476e57b7ee4704f96dfe9b7e23609c4662cb784f502a727f6481db1e06c74da073408d3f50015bd7e245e','admin'),('A002','scrypt:32768:8:1$OjQOp27Yv8KhE4CF$6269162570353b73a6e3ca9a88cae3143c688177402265af0c117741dac9ff47238edb99b93d4644262cbafc5a5337080d896e465ecc351dd81ebfc33cb82de4','admin'),('S001','scrypt:32768:8:1$3sCEd1UkiLA9dt54$5614154cb14365e83c666841300ebadeaf95a71730a06187f404c85bb0b02ff97e3b0a4b0e2535786e5422637f9f6c5024225899b8b7a19dfea17b8c72d9a92c','student'),('S002','scrypt:32768:8:1$gA6dKb4nx1B6Hxqo$ae89b2823ffa6f03da580eb7de5dd8e0c4695533741fd5df76ab1f001915b91a0027abdeda86e607acb838c3e5ff66b324d88e68ed4a6035d9771c95befb8198','student'),('S003','scrypt:32768:8:1$5gUl5m4K2aNHgjDD$0c2bafe2eb277d3427974d6b7c9b33a1212aca03120f9a139a0691f7b72eedbd6e2b8bd5864468461ace8f63074ac1ff78da88b11550e5ae46387a5cd8861470','student'),('T001','scrypt:32768:8:1$GPXIyhdWjVJs8VP9$f7751f1c587c92fa231aa8ee3f3760c7830b08e8d11b561d6e836aed4d05cf26ecc721e772a7b77a0f0865e7b1e77d0e9bd0685beb5fbd3293dab4e1e9c730dc','teacher'),('T002','scrypt:32768:8:1$JTs0QLafWpllUKAn$773cc8a4663c3037e7dadb9383f9ad774f6f68fe6183dc60082099ca9fa93b8b0dee602c66466108d2ea10cc39d5d2e369f34732112829d9864c1a05fd36f299','teacher'),('T003','scrypt:32768:8:1$5MM4KCLx8lAOBYT8$c48013f53273a2ea19ad428e2f9040b13c314e3ece05e1076dfbbe7153650091af0bd339a7ebc0464e97428a8c10c5691db4996a3724df9627847e139bdd4759','teacher');
/*!40000 ALTER TABLE `login_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `overlap_application`
--

DROP TABLE IF EXISTS `overlap_application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `overlap_application` (
  `student_id` varchar(32) NOT NULL,
  `course_id` varchar(32) NOT NULL,
  `status` varchar(16) NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`student_id`,`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `overlap_application`
--

LOCK TABLES `overlap_application` WRITE;
/*!40000 ALTER TABLE `overlap_application` DISABLE KEYS */;
INSERT INTO `overlap_application` VALUES ('S001','PY002','approved');
/*!40000 ALTER TABLE `overlap_application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `contact` varchar(100) DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `class_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `class_id` (`class_id`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `login_account` (`id`) ON DELETE CASCADE,
  CONSTRAINT `student_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('S001','张三','男','2005-06-08','18062726221','数据科学','00101'),('S002','李四',NULL,NULL,NULL,NULL,'00101'),('S003','王五',NULL,NULL,NULL,NULL,'00101');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_course`
--

DROP TABLE IF EXISTS `student_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_course` (
  `student_id` varchar(50) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  PRIMARY KEY (`student_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `student_course_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE,
  CONSTRAINT `student_course_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_course`
--

LOCK TABLES `student_course` WRITE;
/*!40000 ALTER TABLE `student_course` DISABLE KEYS */;
INSERT INTO `student_course` VALUES ('S001','MA001'),('S002','MA001'),('S001','PY002'),('S001','PY003'),('S002','PY003'),('S002','SC001');
/*!40000 ALTER TABLE `student_course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `teacher_id` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `title` varchar(50) DEFAULT NULL,
  `contact` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`teacher_id`),
  CONSTRAINT `teacher_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `login_account` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` VALUES ('T001','卢荣德',NULL,NULL,NULL,NULL),('T002','张明波',NULL,NULL,NULL,NULL),('T003','林箐',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_course`
--

DROP TABLE IF EXISTS `teacher_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_course` (
  `teacher_id` varchar(50) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  PRIMARY KEY (`teacher_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `teacher_course_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE CASCADE,
  CONSTRAINT `teacher_course_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_course`
--

LOCK TABLES `teacher_course` WRITE;
/*!40000 ALTER TABLE `teacher_course` DISABLE KEYS */;
INSERT INTO `teacher_course` VALUES ('T002','MA001'),('T001','PY001'),('T001','PY002'),('T003','PY003'),('T002','SC001');
/*!40000 ALTER TABLE `teacher_course` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-10 16:29:13
