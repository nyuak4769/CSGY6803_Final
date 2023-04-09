use vault;

insert into RotationPolicies (`Id`, `Title`, `description`, hours) values (uuid(), 'My Policy', 'This describes my policy', 72);

insert into EventCodes (Code, Description) VALUES ('C001', 'Create');
insert into EventCodes (Code, Description) VALUES ('U001', 'Rotation');
insert into EventCodes (Code, Description) VALUES ('R001', 'Retrieval');

insert into Secrets (`Id`, `Description`, `value`, `RotationPolicyID`)
values (uuid(), 'Secret 1', 'abc1234', (select Id from RotationPolicies where `Title` = "My Policy"));

insert into Secrets (`Id`, `Description`, `value`, `RotationPolicyID`)
values (uuid(), 'Secret 2',  'dec5678', (select Id from RotationPolicies where `Title` = "My Policy"));

insert into PermissionPolicies (Id, Title, Description) VALUES (uuid(), 'Policy 1', 'Permission Policy 1');
insert into PermissionPolicies (Id, Title, Description) VALUES (uuid(), 'Policy 2', 'Permission Policy 2');

insert into SecretPermissions (Id, SecretId, PermissionPolicyId) VALUES (
                                                                     uuid(),
                                                                     (select Id from Secrets where Description = 'Secret 1'),
                                                                     (select Id from PermissionPolicies where Title = 'Policy 1')
                                                                    );

insert into SecretPermissions (Id, SecretId, PermissionPolicyId) VALUES (
                                                                        uuid(),
                                                                        (select Id from Secrets where Description = 'Secret 2'),
                                                                        (select Id from PermissionPolicies where Title = 'Policy 2')
                                                                    );

insert into SecretPermissions (Id, SecretId, PermissionPolicyId) VALUES (
                                                                        uuid(),
                                                                        (select Id from Secrets where Description = 'Secret 2'),
                                                                        (select Id from PermissionPolicies where Title = 'Policy 1')
                                                                    );

insert into Users (Id, UserName, Password) VALUES (uuid(), 'user1', 'myPassword1');
insert into Users (Id, UserName, Password) VALUES (uuid(), 'user2', 'myPassword1');

insert into UserPermissions (UserId, PermissionPolicyId) VALUES (
                                                                 (select Id from Users where UserName = 'user1'),
                                                                 (select Id from PermissionPolicies where Title = 'Policy 1')
                                                                );

insert into UserPermissions (UserId, PermissionPolicyId) VALUES (
                                                                    (select Id from Users where UserName = 'user1'),
                                                                    (select Id from PermissionPolicies where Title = 'Policy 2')
                                                                );

insert into UserPermissions (UserId, PermissionPolicyId) VALUES (
                                                                    (select Id from Users where UserName = 'user2'),
                                                                    (select Id from PermissionPolicies where Title = 'Policy 2')
                                                                );