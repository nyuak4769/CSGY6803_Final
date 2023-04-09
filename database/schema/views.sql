DELIMITER $$

create view if not exists v_NextSecretRotationTime as
(
select LastRotation.SecretId,
       LastRotation.Timestamp,
       date_add(LastRotation.Timestamp, interval RotationPolicies.hours HOUR) as nextRotation
from (select `SecretId` as SecretId, max(`timestamp`) as Timestamp
      from Events
      where Events.EventCode in (SELECT EventCode from EventCodes where Description in ('Rotation', 'Create'))
      group by `SecretId`
      ) as LastRotation
join Secrets
    on Secrets.Id=LastRotation.SecretId
join RotationPolicies
    on Secrets.RotationPolicyID = RotationPolicies.Id
)$$

create view if not exists v_UserPermissionsForSecret as
(
select Users.Id as UserId, Users.UserName, SP.PermissionPolicyId as PermissionPolicyId, PP.Title as PermissionPolicyTitle, SecretId, S.Description as SecretDescription
from Users
join UserPermissions UP on Users.Id = UP.UserId
join SecretPermissions SP on UP.PermissionPolicyId = SP.PermissionPolicyId
join PermissionPolicies PP on SP.PermissionPolicyId = PP.Id
join Secrets S on S.Id = SP.SecretId
)$$