DELIMITER $$

CREATE PROCEDURE usp_RetrieveSecretById (IN `secretId` varchar(128))
    NO SQL
BEGIN
    INSERT INTO vault.Events (Id, EventCode, Timestamp, SecretId) VALUES (
                                                                          uuid(),
                                                                          (SELECT Code from vault.EventCodes where Description = 'Retrieval'),
                                                                          now(),
                                                                          secretId
                                                                         );
    select Id, Value from vault.Secrets where Id = secretId;
end $$

CREATE PROCEDURE usp_RetrieveSecretByDescription (IN `secretDescription` varchar(128))
    NO SQL
BEGIN
    SET @secretID = (SELECT ID from vault.Secrets where Description = secretDescription);
    call usp_RetrieveSecretById(@secretID);
end $$