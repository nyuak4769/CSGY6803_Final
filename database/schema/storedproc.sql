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

CREATE PROCEDURE usp_DeleteSecretById (IN `secretId` varchar(128))
    NO SQL
BEGIN
    Delete from vault.Events where Events.SecretId = secretId;
    Delete from vault.SecretPermissions where SecretPermissions.SecretId = secretId;
    Delete from vault.Secrets where Secrets.Id = secretId;
end $$

CREATE PROCEDURE usp_DeleteUserByUsername (IN `userName` varchar(128))
    NO SQL
BEGIN
    SET @userID = (SELECT ID from vault.Users where Users.UserName = userName);
    Delete from vault.UserPermissions where UserPermissions.UserId = @userID;
    Delete from vault.Users where Users.Id = @userID;
end $$