DELIMITER $$

CREATE TRIGGER IF NOT EXISTS `TR_Secrets_AddCreateEvent`
    AFTER INSERT
    ON `vault`.`Secrets`
    FOR EACH ROW
BEGIN
    INSERT INTO `vault`.`Events`
    VALUES (uuid(),
            (SELECT Code FROM `vault`.`EventCodes` WHERE Description = "Create"),
            now(),
            NEW.Id);
END $$

CREATE TRIGGER IF NOT EXISTS `TR_Secrets_AddRotationEvent`
    AFTER UPDATE
    ON `vault`.`Secrets`
    FOR EACH ROW
BEGIN
    IF !(NEW.Value <=> OLD.Value) THEN
        INSERT INTO `vault`.`Events`
        VALUES (uuid(),
                (SELECT Code FROM `vault`.`EventCodes` WHERE Description = "Rotation"),
                now(),
                OLD.Id);
    END IF;
END $$

