DELIMITER $$
CREATE OR REPLACE FUNCTION udf_TimeToSecretExpiration (`secretDesc` VARCHAR(128)) RETURNS FLOAT
BEGIN
    SET @nextRotation = (select date_add(LastRotation.Timestamp, interval RotationPolicies.hours HOUR) as nextRotation
                         from (select `SecretId` as SecretId, max(`timestamp`) as Timestamp
                               from Events
                               where Events.EventCode in (SELECT EventCode from EventCodes where Description in ('Rotation', 'Create'))
                               group by `SecretId`
                               ) as LastRotation
                         join Secrets
                             on Secrets.Id=LastRotation.SecretId
                         join RotationPolicies
                             on Secrets.RotationPolicyID = RotationPolicies.Id
                         where Secrets.Description = secretDesc
                         );
    RETURN UNIX_TIMESTAMP(@nextRotation) - UNIX_TIMESTAMP(CURRENT_TIMESTAMP);
END$$
DELIMITER ;