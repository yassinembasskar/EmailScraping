-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : lun. 11 sep. 2023 à 02:44
-- Version du serveur : 10.4.28-MariaDB
-- Version de PHP : 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `emailscrapperdb`
--

-- --------------------------------------------------------

--
-- Structure de la table `action`
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

-- --------------------------------------------------------

--
-- Structure de la table `urls`
--

CREATE TABLE `urls` (
  `URL_ID` int(11) NOT NULL,
  `USER_ID` int(11) NOT NULL,
  `ACTION_ID` int(11) NOT NULL,
  `URL_LINK` varchar(200) NOT NULL,
  `URL_EMAILS` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

CREATE TABLE `user` (
  `USER_ID` int(11) NOT NULL,
  `USER_NAME` varchar(30) NOT NULL,
  `USER_EMAIL` varchar(60) NOT NULL,
  `USER_PASSWORD` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `user`
--

INSERT INTO `user` (`USER_ID`, `USER_NAME`, `USER_EMAIL`, `USER_PASSWORD`) VALUES
(1, 'yassine', 'basskar2049@gmail.com', 'pbkdf2:sha256:600000$qvk8eLX9y');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `action`
--
ALTER TABLE `action`
  ADD PRIMARY KEY (`ACTION_ID`),
  ADD KEY `FK_ACTION_AVOIR_USER` (`USER_ID`);

--
-- Index pour la table `urls`
--
ALTER TABLE `urls`
  ADD PRIMARY KEY (`URL_ID`,`USER_ID`,`ACTION_ID`),
  ADD KEY `FK_URLS_CONTENIR_ACTION` (`USER_ID`,`ACTION_ID`);

--
-- Index pour la table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`USER_ID`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `action`
--
ALTER TABLE `action`
  MODIFY `ACTION_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT pour la table `urls`
--
ALTER TABLE `urls`
  MODIFY `URL_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT pour la table `user`
--
ALTER TABLE `user`
  MODIFY `USER_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `action`
--
ALTER TABLE `action`
  ADD CONSTRAINT `FK_ACTION_AVOIR_USER` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`USER_ID`),
  ADD CONSTRAINT `action_ibfk_1` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`USER_ID`);

--
-- Contraintes pour la table `urls`
--
ALTER TABLE `urls`
  ADD CONSTRAINT `FK_URLS_CONTENIR_ACTION` FOREIGN KEY (`USER_ID`,`ACTION_ID`) REFERENCES `action` (`USER_ID`, `ACTION_ID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
