DELIMITER $$

CREATE TABLE IF NOT EXISTS `RotationPolicies`
(
    `Id`          varchar(128) NOT NULL,
    `Title`       varchar(45)  NOT NULL,
    `Description` varchar(45)  NOT NULL,
    `Hours`       int unsigned NOT NULL,
    PRIMARY KEY `PK_RotationPolicies` (`Id`),
    UNIQUE KEY `UQ_RotationPolicies_Id` (`Id`),
    UNIQUE KEY `UQ_RotationPolicies_Title` (`Title`),
    constraint `CK_RotationPolicies_Id`
        check (Id regexp '([A-F 0-9]{8})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{12})'),
    constraint `CK_RotationPolicies_Hours`
        check (Hours >= 1 && Hours < 65535)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `PermissionPolicies`
(
    `Id`          varchar(128) NOT NULL,
    `Title`       varchar(45)  NOT NULL,
    `Description` varchar(45)  NOT NULL,
    PRIMARY KEY `PK_PermissionPolicies` (`Id`),
    UNIQUE KEY `UQ_PermissionPolicies_Id` (`Id`),
    UNIQUE KEY `UQ_PermissionPolicies_Title` (`Title`),
    constraint `CK_PermissionPolicies_Id`
        check (Id regexp '([A-F 0-9]{8})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{12})')
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `Users`
(
    `Id`       varchar(128) NOT NULL,
    `UserName` varchar(45)  NOT NULL,
    `Password` varchar(45)  NOT NULL,
    PRIMARY KEY `PK_Users` (`Id`),
    UNIQUE KEY `UQ_Users_Name` (`UserName`),
    constraint `CK_Users_Id`
        check (Id regexp '([A-F 0-9]{8})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{12})')
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `Secrets`
(
    `Id`               varchar(128) NOT NULL,
    `Description`      varchar(128) NOT NULL,
    `Value`            varchar(128) NOT NULL,
    `RotationPolicyID` varchar(128) NOT NULL,
    CONSTRAINT `FK_Secrets_RotationPolicies`
        FOREIGN KEY (RotationPolicyID) REFERENCES RotationPolicies (Id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
    constraint `CK_Id`
        check (`Id` regexp '([A-F 0-9]{8})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{12})'),
    PRIMARY KEY `PK_Secrets` (`Id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `EventCodes`
(
    `Code`        varchar(10)  NOT NULL,
    `Description` varchar(128) NOT NULL,
    PRIMARY KEY `PK_EventCodes` (`Code`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `Events`
(
    `Id`        varchar(128) NOT NULL,
    `EventCode` varchar(128) NOT NULL,
    `Timestamp` timestamp    NOT NULL,
    `SecretId`  varchar(128) NOT NULL,
    Primary Key `PK_Events` (`Id`),
    CONSTRAINT `FK_Events_Secrets`
        FOREIGN KEY (`SecretId`) REFERENCES Secrets (Id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
    CONSTRAINT `CK_Id`
        check (`Id` regexp '([A-F 0-9]{8})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{4})-([A-F 0-9]{12})'),
    CONSTRAINT `FK_Events_EventCodes`
        FOREIGN KEY (EventCode) REFERENCES EventCodes (Code)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `SecretPermissions`
(
    `SecretId`     varchar(128) NOT NULL,
    `PermissionPolicyId` varchar(128)  NOT NULL,
    CONSTRAINT `FK_SecretPermissions_Secrets`
        FOREIGN KEY (`SecretId`) REFERENCES Secrets (`Id`)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
    CONSTRAINT `FK_SecretPermissions_PermissionPolicies`
        FOREIGN KEY (`PermissionPolicyId`) REFERENCES `PermissionPolicies` (`Id`)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
    PRIMARY KEY `PK_SecretPermissions` (SecretId, PermissionPolicyId)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$

CREATE TABLE IF NOT EXISTS `UserPermissions`
(
    `UserId`     varchar(128) NOT NULL,
    `PermissionPolicyId` varchar(128)  NOT NULL,
    CONSTRAINT `FK_UserPermissions_Users`
        FOREIGN KEY (`UserId`) REFERENCES Users (`Id`)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
    CONSTRAINT `FK_UserPermissions_PermissionPolicies`
        FOREIGN KEY (`PermissionPolicyId`) REFERENCES `PermissionPolicies` (`Id`)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
    PRIMARY KEY `PK_UserPermissions` (UserId, PermissionPolicyId)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci$$