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

create view if not exists v_SecretDetails as
(
    Select Secrets.Id, Secrets.Description, nsr.nextRotation, rp.Title, pp.idlist from vault.Secrets
    join (select SecretId, nextRotation from vault.v_NextSecretRotationTime) as nsr on
    Secrets.Id=nsr.SecretId join vault.RotationPolicies as rp on rp.Id=Secrets.RotationPolicyID
    join (select SecretId, GROUP_CONCAT(PermissionPolicyId) idlist FROM SecretPermissions group by SecretId) as pp on
    pp.SecretId = Secrets.Id
)$$

create view if not exists v_UserPermissionsForSecret as
(
select Users.Id as UserId, Users.UserName, SP.PermissionPolicyId as PermissionPolicyId, PP.Title as PermissionPolicyTitle, SecretId, S.Description as SecretDescription
from Secrets as S
left join SecretPermissions SP on S.Id = SP.SecretId
left join PermissionPolicies PP on SP.PermissionPolicyId = PP.Id
left join UserPermissions UP on PP.Id = UP.PermissionPolicyId
left join Users on UP.UserId = Users.Id
)$$

create view if not exists v_SecretEvents as
(
select E.Id as 'Id', EC.Description as 'Description', E.Timestamp as 'Timestamp', E.SecretId as 'SecretId'
from Events E
join EventCodes EC on EC.Code = E.EventCode
order by Timestamp desc
)$$